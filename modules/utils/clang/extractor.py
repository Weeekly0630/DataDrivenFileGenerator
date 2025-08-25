import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union, Optional, Protocol, Tuple
from enum import Enum, IntFlag

# 自动添加项目根目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.plugins.type_classes.c import Decl, Expr, Attr, Preprocess

try:
    from clang import cindex
except ImportError as e:
    sys.stderr.write(
        "Error: Python bindings for libclang not found. Install 'clang' (pip) and ensure libclang is available.\n"
    )
    raise

SEVERITY_ORDER = {
    cindex.Diagnostic.Ignored: 0,
    cindex.Diagnostic.Note: 1,
    cindex.Diagnostic.Warning: 2,
    cindex.Diagnostic.Error: 3,
    cindex.Diagnostic.Fatal: 4,
}


class CursorVisitorResult(IntFlag):
    """Visitor函数访问结果枚举, 用来控制VisitorChain的遍历行为"""

    CONTINUE = 0  # 继续遍历子节点
    SKIP_VISITOR = 1  # 跳过后续访问器
    SKIP_CHILDREN = 2  # 跳过子节点, 用于控制当前节点的子节点访问
    BREAK_CHILDREN = 4  # 跳过兄弟节点，用于返回给父节点，使其跳过兄弟节点


@dataclass
class CursorVisitorContext:
    """访问器上下文信息"""

    depth: int


class CursorVisitor(Protocol):
    """Clang Cursor访问器"""

    def visit(
        self, cursor: "cindex.Cursor", context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问Cursor节点，提供一个遍历上下文信息，返回一定信息"""
        ...


class CursorPrintVisitor(CursorVisitor):
    """AST打印访问器，用于打印AST节点信息"""

    def __init__(self):
        self.nodes: List[Tuple[int, str]] = []  # 收集(depth, node_desc)

    def visit(
        self, cur: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        method_name = f"visit_{cur.kind.name.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(cur, context)
        return CursorVisitorResult.CONTINUE

    def generic_visit(self, cur: cindex.Cursor, context: CursorVisitorContext) -> None:
        depth = context.depth
        node_desc = describe_node(cur)
        self.nodes.append((depth, node_desc))

    def format_tree(self) -> str:
        lines = []
        n = len(self.nodes)

        for i, (depth, desc) in enumerate(self.nodes):
            # 判断当前节点是否为父节点的最后一个子节点
            is_last = True
            # 向后查找同深度的兄弟节点
            for j in range(i + 1, n):
                next_depth = self.nodes[j][0]
                if next_depth < depth:
                    # 遇到更浅的节点，说明当前节点是最后一个
                    break
                elif next_depth == depth:
                    # 遇到同深度节点，说明当前节点不是最后一个
                    is_last = False
                    break

            # 构造前缀：需要知道每一层是否有后续兄弟节点
            prefix = ""
            for d in range(depth):
                # 判断第d层是否有后续兄弟节点
                has_sibling = False
                # 从当前节点向后查找
                for j in range(i + 1, n):
                    check_depth = self.nodes[j][0]
                    if check_depth < d:
                        # 遇到更浅的节点，停止查找
                        break
                    elif check_depth == d:
                        # 找到同层兄弟节点
                        has_sibling = True
                        break

                if has_sibling:
                    prefix += "│   "
                else:
                    prefix += "    "

            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{desc}")
        return "\n".join(lines)


class CursorFilterVisitor(CursorVisitor):
    """AST过滤访问器，用于过滤特定条件的节点"""

    def __init__(
        self,
        main_file_only: bool = False,
        allowed_files: Optional[List[str]] = None,
        excluded_files: Optional[List[str]] = None,
        allowed_kinds: Optional[List[cindex.CursorKind]] = None,
        excluded_kinds: Optional[List[cindex.CursorKind]] = None,
    ):
        """
        初始化过滤器

        Args:
            main_file_only: 只允许主文件的节点
            allowed_files: 允许的文件名列表（支持通配符）
            excluded_files: 排除的文件名列表（支持通配符）
            allowed_kinds: 允许的节点类型列表
            excluded_kinds: 排除的节点类型列表
        """
        self.main_file_only = main_file_only
        self.allowed_files = allowed_files or []
        self.excluded_files = excluded_files or []
        self.allowed_kinds = allowed_kinds or []
        self.excluded_kinds = excluded_kinds or []

    def _check_file_filter(self, cursor: cindex.Cursor) -> bool:
        """检查文件过滤条件"""
        # Translation Unit 节点始终允许通过
        if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return True

        loc = cursor.location
        if not loc or not loc.file:
            # 没有文件信息的节点（如内置类型）
            return not self.main_file_only

        filename = str(loc.file)

        # 主文件过滤
        if self.main_file_only:
            try:
                if hasattr(cursor, "translation_unit") and cursor.translation_unit:
                    if not os.path.samefile(filename, cursor.translation_unit.spelling):
                        return False
            except Exception:
                if filename != cursor.translation_unit.spelling:
                    return False

        # 排除文件列表
        for excluded in self.excluded_files:
            if excluded in filename or filename.endswith(excluded):
                return False

        # 允许文件列表
        if self.allowed_files:
            allowed = False
            for allowed_file in self.allowed_files:
                if allowed_file in filename or filename.endswith(allowed_file):
                    allowed = True
                    break
            if not allowed:
                return False

        return True

    def _check_kind_filter(self, cursor: cindex.Cursor) -> bool:
        """检查节点类型过滤条件"""
        # 排除类型列表
        if cursor.kind in self.excluded_kinds:
            return False

        # 允许类型列表
        if self.allowed_kinds and cursor.kind not in self.allowed_kinds:
            return False

        return True

    def visit(
        self, cur: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问节点并进行过滤"""
        # 检查文件过滤条件
        if not self._check_file_filter(cur):
            return CursorVisitorResult.SKIP_CHILDREN | CursorVisitorResult.SKIP_VISITOR

        # 检查节点类型过滤条件
        if not self._check_kind_filter(cur):
            return CursorVisitorResult.SKIP_CHILDREN | CursorVisitorResult.SKIP_VISITOR

        # 通过所有过滤条件，继续遍历
        return CursorVisitorResult.CONTINUE

    def generic_visit(self, cur: cindex.Cursor, context: CursorVisitorContext) -> None:
        """默认访问行为"""
        pass


class CursorExtractVisitor(CursorVisitor):
    """Cursor提取声明访问器"""

    def __init__(self) -> None:
        self.var_decl_list: List[Decl.Variable.MetaData] = []
        self.struct_decl_list: List[Decl.Struct.MetaData] = []
        self.union_decl_list: List[Decl.Union.MetaData] = []
        self.macro_definition_list: List[Preprocess.MacroDefinition.MetaData] = []
        self.function_decl_list: List[Decl.Function.MetaData] = []
        self.enum_decl_list: List[Decl.Enum.MetaData] = []
        self.typedef_decl_list: List[Decl.Typedef.MetaData] = []

    @property
    def var_declarations(self) -> List[Decl.Variable.MetaData]:
        return self.var_decl_list

    @property
    def struct_declarations(self) -> List[Decl.Struct.MetaData]:
        return self.struct_decl_list

    @property
    def union_declarations(self) -> List[Decl.Union.MetaData]:
        return self.union_decl_list

    @property
    def macro_definitions(self) -> List[Preprocess.MacroDefinition.MetaData]:
        return self.macro_definition_list

    @property
    def function_declarations(self) -> List[Decl.Function.MetaData]:
        return self.function_decl_list

    @property
    def enum_declarations(self) -> List[Decl.Enum.MetaData]:
        return self.enum_decl_list

    @property
    def typedef_declarations(self) -> List[Decl.Typedef.MetaData]:
        return self.typedef_decl_list

    def print_summary(self) -> None:
        """打印提取结果的总结信息"""
        print("=== Extraction Summary ===")
        print("=== Variables ===")
        for var in self.var_decl_list:
            print(var)
            print("Raw code: " + var.raw_code)

        print("=== Structs ===")
        for struct in self.struct_decl_list:
            print(struct)
            print("Raw code: " + struct.raw_code)

        print("=== Unions ===")
        for union in self.union_decl_list:
            print(union)
            print("Raw code: " + str(union.raw_code))

        print("=== Macros ===")
        for macro in self.macro_definition_list:
            print(macro)
            print("Raw code: " + macro.raw_code)

        print("=== Functions ===")
        for func in self.function_decl_list:
            print(func)
            print("Raw code: " + str(func.raw_code))

        print("=== Enums ===")
        for enum in self.enum_decl_list:
            print(enum)
            print("Raw code: " + str(enum.raw_code))

        print("=== Typedefs ===")
        for typedef in self.typedef_decl_list:
            print(typedef)
            print("Raw code: " + str(typedef.raw_code))

    def visit(
        self, cur: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问节点并提取信息"""
        method_name = f"visit_{cur.kind.name.lower()}"
        visitor = getattr(self, method_name, self.visit_generic)
        result = visitor(cur, context)
        return result

    def visit_generic(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """默认的访问行为"""
        return CursorVisitorResult.CONTINUE

    def visit_macro_definition(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        # 去重逻辑
        if not hasattr(self, "_macro_keys"):
            self._macro_keys = set()

        macro_key = (
            cursor.spelling,
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        if macro_key in self._macro_keys:
            return CursorVisitorResult.SKIP_CHILDREN
        self._macro_keys.add(macro_key)

        # 提取宏名
        name = cursor.spelling
        # 提取所有tokens
        tokens = list(cursor.get_tokens())

        # 分离参数和宏体
        params = []
        value = ""

        if len(tokens) > 1:
            # 检查是否是函数式宏（第二个token是'('）
            if len(tokens) > 2 and tokens[1].spelling == "(":
                # 函数式宏：#define FOO(x, y) body
                paren_count = 0
                param_start = 2  # 跳过宏名和'('
                body_start = 2

                # 找到参数结束位置
                for i, token in enumerate(tokens[2:], 2):
                    if token.spelling == "(":
                        paren_count += 1
                    elif token.spelling == ")":
                        if paren_count == 0:
                            body_start = i + 1
                            break
                        paren_count -= 1
                    elif paren_count == 0 and token.spelling != ",":
                        # 参数名
                        if token.spelling not in params:
                            params.append(token.spelling)

                # 提取宏体（括号后的内容）
                if body_start < len(tokens):
                    value = " ".join(t.spelling for t in tokens[body_start:])
            else:
                # 简单宏：#define FOO value
                value = " ".join(t.spelling for t in tokens[1:])

        # 手动提取前置注释
        comment = self._extract_macro_comment(cursor)

        # 提取源码
        raw_code = self.extract_raw_code(cursor)

        self.macro_definition_list.append(
            Preprocess.MacroDefinition.MetaData(
                name=name,
                value=value.strip(),
                params=params,
                comment=comment,
                raw_code=raw_code,
            )
        )
        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    def _extract_macro_comment(self, cursor: cindex.Cursor) -> str:
        """提取宏定义前面的注释"""
        try:
            # 首先尝试获取 Clang 提供的文档注释
            if cursor.raw_comment:
                return cursor.raw_comment
            if cursor.brief_comment:
                return cursor.brief_comment

            # 如果没有文档注释，尝试从 extent 中查找
            extent = cursor.extent
            if not extent or not extent.start.file:
                return ""

            # 获取翻译单元中的所有 tokens
            tu = cursor.translation_unit
            if not tu:
                return ""

            # 创建一个从文件开始到宏定义位置的范围
            try:
                # 使用 cursor 的 extent 来获取之前的 tokens
                start_loc = extent.start
                file_tokens = list(tu.get_tokens(extent=tu.cursor.extent))

                # 查找宏定义前的注释 tokens
                comment_parts = []
                macro_line = start_loc.line

                for token in file_tokens:
                    token_loc = token.location
                    if token_loc.line >= macro_line:
                        break

                    # 检查是否是注释
                    token_text = token.spelling
                    if (
                        token.kind == cindex.TokenKind.COMMENT
                        or token_text.startswith("/*")
                        or token_text.startswith("//")
                    ):
                        token_start_line = token_loc.line

                        # 计算注释的实际结束位置
                        if "/*" in token_text and "*/" in token_text:
                            # 多行注释：计算结束行
                            lines_in_comment = token_text.count("\n")
                            token_end_line = token_start_line + lines_in_comment
                        else:
                            # 单行注释或其他情况
                            token_end_line = token_start_line

                        # 检查注释结尾是否紧邻宏定义
                        distance = macro_line - token_end_line
                        if 0 <= distance <= 2:  # 注释结尾到宏定义之间相差0-2行
                            comment_parts.append(token_text)

                # 清理注释
                if comment_parts:
                    comment = " ".join(comment_parts)
                    # 移除注释符号
                    comment = (
                        comment.replace("/*", "").replace("*/", "").replace("//", "")
                    )
                    comment = comment.replace("*", "").strip()
                    return comment

            except Exception:
                pass

            return ""
        except Exception:
            return ""

    def visit_union_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问联合体声明节点"""
        # 跳过匿名联合体的typedef声明
        if cursor.is_anonymous():
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.TYPEDEF_DECL:
                    return CursorVisitorResult.SKIP_CHILDREN

        # 去重逻辑
        if not hasattr(self, "_union_keys"):
            self._union_keys = set()

        union_key = (
            cursor.spelling,
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        if union_key in self._union_keys:
            return CursorVisitorResult.SKIP_CHILDREN
        self._union_keys.add(union_key)

        self.union_decl_list.append(
            Decl.Union.MetaData(
                record=CursorExtractVisitor.extract_record(cursor),
                raw_code=CursorExtractVisitor.extract_raw_code(cursor),
            )
        )
        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    def visit_struct_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问结构体声明节点"""
        # 跳过匿名结构体的typedef声明，因为它会在typedef_decl中处理
        if cursor.is_anonymous():
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.TYPEDEF_DECL:
                    return CursorVisitorResult.SKIP_CHILDREN

        # 初始化结构体key集合（用于去重）
        if not hasattr(self, "_struct_keys"):
            self._struct_keys = set()

        # 使用结构体名称和位置作为唯一标识
        struct_key = (
            cursor.spelling,
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        # 如果已经处理过这个结构体，跳过
        if struct_key in self._struct_keys:
            return CursorVisitorResult.SKIP_CHILDREN

        self._struct_keys.add(struct_key)

        # 1. Record
        self.struct_decl_list.append(
            Decl.Struct.MetaData(
                record=CursorExtractVisitor.extract_record(cursor),
                raw_code=CursorExtractVisitor.extract_raw_code(cursor),
            )
        )

        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    def visit_var_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问变量声明节点"""
        # 去重逻辑
        if not hasattr(self, "_var_keys"):
            self._var_keys = set()

        var_key = (
            cursor.spelling,
            cursor.type.spelling if cursor.type else "",
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        if var_key in self._var_keys:
            return CursorVisitorResult.SKIP_CHILDREN
        self._var_keys.add(var_key)

        # 1. Name
        name = cursor.spelling

        # 2. storage_class
        storage_class = ""
        if hasattr(cursor, "storage_class") and cursor.storage_class is not None:
            sc = cursor.storage_class
            # StorageClass.NONE 表示没有存储类别
            if hasattr(sc, "name") and sc != cindex.StorageClass.NONE:
                storage_class = str(sc.name)

        # 3. Modifier
        modifier = self.extract_type_modifier(cursor)

        # 4. Init Expression
        init_expr = ""
        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.INIT_LIST_EXPR:
                init_expr = self.extract_raw_code(child)
                break

        # 5. Comment
        comment = self.extract_comment(cursor)

        # 6. Raw Code
        raw_code = self.extract_raw_code(cursor)

        self.var_decl_list.append(
            Decl.Variable.MetaData(
                name=name,
                storage_class=storage_class,
                modifier=modifier,
                comment=comment,
                init_expr=init_expr,
                raw_code=raw_code,
            )
        )
        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    def visit_function_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问函数声明节点"""
        raw_code = CursorExtractVisitor.extract_raw_code(cursor)

        if cursor.is_definition():
            # 如果是函数定义，提取声明部分
            idx = raw_code.find("{")
            if idx != -1:
                raw_code = raw_code[:idx].rstrip()

        # 去重逻辑：用函数名、参数类型和位置信息做唯一标识
        param_types = tuple(
            p.type.spelling if hasattr(p, "type") else ""
            for p in cursor.get_arguments()
        )
        func_key = (
            cursor.spelling,
            param_types,
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )
        # 已收集的函数key集合
        if not hasattr(self, "_function_keys"):
            self._function_keys = set()
        if func_key in self._function_keys:
            return CursorVisitorResult.SKIP_CHILDREN  # 已收集，跳过
        self._function_keys.add(func_key)

        self.function_decl_list.append(
            Decl.Function.MetaData(
                name=cursor.spelling,
                return_type=Decl.TypeRef.MetaData(ref=cursor.result_type.spelling),
                params=CursorExtractVisitor.extract_params(cursor),
                comment=CursorExtractVisitor.extract_comment(cursor),
                raw_code=raw_code,
            )
        )

        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    def visit_typedef_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问typedef声明节点"""
        # 去重逻辑
        if not hasattr(self, "_typedef_keys"):
            self._typedef_keys = set()

        typedef_key = (
            cursor.spelling,
            (
                cursor.underlying_typedef_type.spelling
                if cursor.underlying_typedef_type
                else ""
            ),
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        if typedef_key in self._typedef_keys:
            return CursorVisitorResult.SKIP_CHILDREN
        self._typedef_keys.add(typedef_key)

        # 获取原始类型
        underlying_type = cursor.underlying_typedef_type
        # 获取类型定义的目标类型
        type_ref = Decl.TypeRef.MetaData(
            ref=underlying_type.spelling if underlying_type else ""
        )

        # 提取注释
        comment = self.extract_comment(cursor)

        # 提取源码
        raw_code = self.extract_raw_code(cursor)

        self.typedef_decl_list.append(
            Decl.Typedef.MetaData(
                name=cursor.spelling,
                typeref=type_ref,
                comment=comment,
                raw_code=raw_code,
            )
        )

        return CursorVisitorResult.SKIP_CHILDREN

    def visit_enum_decl(
        self, cursor: cindex.Cursor, context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """访问枚举声明节点"""
        # 跳过匿名枚举的typedef声明
        if cursor.is_anonymous():
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.TYPEDEF_DECL:
                    return CursorVisitorResult.SKIP_CHILDREN

        # 去重逻辑
        if not hasattr(self, "_enum_keys"):
            self._enum_keys = set()

        enum_key = (
            cursor.spelling,
            cursor.location.file.name if cursor.location.file else "",
            cursor.location.line,
            cursor.location.column,
        )

        if enum_key in self._enum_keys:
            return CursorVisitorResult.SKIP_CHILDREN
        self._enum_keys.add(enum_key)

        # 提取枚举常量
        constants = []
        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
                constants.append(
                    Decl.EnumConstant.MetaData(
                        name=child.spelling,
                        value=child.enum_value,
                        comment=CursorExtractVisitor.extract_comment(child),
                        raw_code=CursorExtractVisitor.extract_raw_code(child),
                    )
                )

        # 构造枚举声明元数据
        self.enum_decl_list.append(
            Decl.Enum.MetaData(
                name=cursor.spelling,
                constants=constants,
                comment=CursorExtractVisitor.extract_comment(cursor),
                raw_code=CursorExtractVisitor.extract_raw_code(cursor),
            )
        )

        return CursorVisitorResult.SKIP_CHILDREN  # 跳过子节点解析

    @staticmethod
    def extract_params(cursor: cindex.Cursor) -> List[Decl.Param.MetaData]:
        params: List[Decl.Param.MetaData] = []
        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.PARM_DECL:
                # 提取参数名和类型
                name = child.spelling
                modifier = CursorExtractVisitor.extract_type_modifier(child)
                params.append(
                    Decl.Param.MetaData(
                        name=name,
                        modifier=modifier,
                        raw_code=CursorExtractVisitor.extract_raw_code(child),
                    )
                )
        return params

    @staticmethod
    def extract_fields(cursor: cindex.Cursor) -> List[Decl.Field.MetaData]:
        fields: List[Decl.Field.MetaData] = []
        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                # 提取字段名和类型
                name = child.spelling
                modifier = CursorExtractVisitor.extract_type_modifier(child)
                comment = CursorExtractVisitor.extract_comment(child)
                bitfield_width = (
                    child.get_bitfield_width() if child.is_bitfield() else None
                )
                fields.append(
                    Decl.Field.MetaData(
                        name=name,
                        modifier=modifier,
                        bitfield_width=bitfield_width,
                        comment=comment,
                        raw_code=CursorExtractVisitor.extract_raw_code(child),
                    )
                )
        return fields

    # @staticmethod
    # def extract_attributes(cursor: cindex.Cursor) -> List[Attr.Attribute.MetaData]:
    #     """从Cursor中提取属性列表"""
    #     attributes: List[Attr.Attribute.MetaData] = []

    @staticmethod
    def extract_record(cursor: cindex.Cursor) -> Decl.Record.MetaData:
        """从结构体声明节点中提取记录信息"""
        return Decl.Record.MetaData(
            name=cursor.spelling,
            fields=CursorExtractVisitor.extract_fields(cursor),
            attribute=CursorExtractVisitor.extract_attribute(cursor),
            comment=CursorExtractVisitor.extract_comment(cursor),
        )

    @staticmethod
    def extract_attribute(cursor: cindex.Cursor) -> Attr.MetaData:
        """从Cursor中提取属性字符串"""
        # TODO: 完善attribute的提取
        return Attr.MetaData([])

    @staticmethod
    def extract_raw_code(cursor: "cindex.Cursor") -> str:
        """从光标的源码范围中提取代码文本"""
        extent = cursor.extent
        if not extent or not extent.start.file:
            return ""
        filename = extent.start.file.name
        with open(filename, encoding="utf-8") as f:
            lines = f.readlines()
        # 单行表达式
        if extent.start.line == extent.end.line:
            return lines[extent.start.line - 1][
                extent.start.column - 1 : extent.end.column - 1
            ].strip()
        # 多行表达式
        parts = []
        parts.append(lines[extent.start.line - 1][extent.start.column - 1 :])
        for i in range(extent.start.line, extent.end.line - 1):
            parts.append(lines[i])
        parts.append(lines[extent.end.line - 1][: extent.end.column - 1])
        return "".join(parts).strip()

    @staticmethod
    def extract_comment(cursor: "cindex.Cursor") -> str:
        """从Cursor中提取注释"""
        if cursor.raw_comment:
            return cursor.raw_comment
        elif cursor.brief_comment:
            return cursor.brief_comment
        return ""

    @staticmethod
    def extract_type_modifier(
        cursor: cindex.Cursor,
    ) -> Decl.TypeModifier.MetaData:
        """从节点中提取类型修饰符
        TODO: 处理匿名类型，因为匿名类型没有spelling属性，需要进一步处理
        例如：struct { int a; } x;
        这种情况下，cursor.spelling会是空字符串，但我们仍然需要提取类型信息
        """
        ctype = cursor.type
        # 指针和数组信息
        pointer_level = 0
        array_dims: List[int] = []

        t = ctype
        while t.kind == cindex.TypeKind.POINTER:
            pointer_level += 1
            is_pointer = True
            t = t.get_pointee()

        # 检查是否为数组
        t = ctype
        while t.kind == cindex.TypeKind.CONSTANTARRAY:
            is_array = True
            array_dims.append(t.element_count)
            t = t.element_type

        # 限定符
        qualifiers = []
        if ctype.is_const_qualified():
            qualifiers.append("const")
        if ctype.is_volatile_qualified():
            qualifiers.append("volatile")
        if ctype.is_restrict_qualified():
            qualifiers.append("restrict")
        qualifiers_str = " ".join(qualifiers)

        # 属性（可扩展）
        attribute = CursorExtractVisitor.extract_attribute(cursor)

        return Decl.TypeModifier.MetaData(
            type=Decl.TypeRef.MetaData(ref=ctype.spelling),
            qualifiers=qualifiers_str,
            attribute=attribute,
            pointer_level=pointer_level,
            array_dims=array_dims,
        )


class VisitorChain:
    """访问器链，用于递归访问Cursor节点，同时调用多个访问器"""

    def __init__(self, visitors: List[CursorVisitor]):
        self.visitors = visitors

    def traverse(self, cursor: "cindex.Cursor") -> None:
        """开始遍历AST节点"""
        self._traverse(cursor=cursor, context=CursorVisitorContext(depth=0))

    def _traverse(
        self, cursor: "cindex.Cursor", context: CursorVisitorContext
    ) -> CursorVisitorResult:
        """遍历AST节点，按顺序调用每个访问器"""
        visit_result: CursorVisitorResult = CursorVisitorResult.CONTINUE

        for visitor in self.visitors:
            result = visitor.visit(cursor, context)
            visit_result |= result
            if result & CursorVisitorResult.SKIP_VISITOR:
                break

        if visit_result & CursorVisitorResult.SKIP_CHILDREN:
            return visit_result

        children = list(cursor.get_children())
        for child in children:
            child_result = self._traverse(
                child, CursorVisitorContext(depth=context.depth + 1)
            )
            if child_result & CursorVisitorResult.BREAK_CHILDREN:
                break

        return visit_result


class ClangDebugPrinter:
    """Clang调试打印器，用于打印光标和诊断信息"""

    def _serialize_cursor_tree(self, cursor: cindex.Cursor) -> str:
        """使用VisitorChain模式打印Cursor树"""
        filter_visitor = CursorFilterVisitor(main_file_only=False)
        print_visitor = CursorPrintVisitor()

        visitor = VisitorChain([filter_visitor, print_visitor])
        visitor.traverse(cursor)
        return print_visitor.format_tree()

    @staticmethod
    def print_diagnostics(tu: "cindex.TranslationUnit") -> str:
        result = ""
        max_sev = 0
        for d in tu.diagnostics:
            loc = d.location
            where = ""
            if loc and loc.file:
                where = f"{loc.file}:{loc.line}:{loc.column}: "
            sev_name = (
                d.severity.name if hasattr(d.severity, "name") else str(d.severity)
            )
            result += f"{where}{sev_name}: {d.spelling}\n"
            max_sev = max(max_sev, SEVERITY_ORDER.get(d.severity, 0))
        # return 1 if max_sev >= SEVERITY_ORDER[cindex.Diagnostic.Error] else 0
        return result

    @staticmethod
    def get_info(
        tu: Optional["cindex.TranslationUnit"],
        print_tree: bool = False,
        print_diagnostics: bool = True,
    ) -> str:
        """获取TranslationUnit的基本信息"""
        result = ""
        if not tu:
            result += "No translation unit available.\n"
            return result

        if print_tree:
            result += "Cursor Tree:\n"
            if tu.cursor:
                result += ClangDebugPrinter()._serialize_cursor_tree(tu.cursor) + "\n"
        if print_diagnostics:
            result += "Diagnostics:\n"
            result += ClangDebugPrinter.print_diagnostics(tu) + "\n"

        return result


def describe_node(
    cur: "cindex.Cursor",
    show_type: bool = False,
    show_canonical: bool = False,
    show_usr: bool = False,
) -> str:
    """描述光标节点的字符串表示"""
    name = cur.spelling or "<anon>"
    kind = cur.kind.name
    pieces = [f"{kind}", name]
    if show_type:
        t = cur.type
        if t.kind.name != "INVALID":
            if show_canonical:
                pieces.append(f"type={t.spelling} [canon={t.get_canonical().spelling}]")
            else:
                pieces.append(f"type={t.spelling}")
    if show_usr:
        usr = cur.get_usr()
        if usr:
            pieces.append(f"usr={usr}")
    loc = ClangExtractor.format_loc(cur)
    if loc:
        pieces.append(f"@ {loc}")
    return " ".join(pieces)


@dataclass
class ClangExtractorOptional:
    """Clang提取器的可选功能类"""

    c_args: List[str] = field(default_factory=list)
    debug_level: int = 0
    main_file_only: bool = False  # 仅提取主文件中的声明


class ClangExtractor:
    """Clang提取器，用于从C/C++源文件中提取信息"""

    def __init__(self, lib_clang_path: str) -> None:
        # 初始化libclang
        cindex.Config.set_library_file(lib_clang_path)
        env_path = os.environ.get("LIBCLANG_PATH")
        if env_path:
            if os.path.isdir(env_path):
                cindex.Config.set_library_path(env_path)
            else:
                cindex.Config.set_library_file(env_path)

    @staticmethod
    def format_loc(cur: "cindex.Cursor") -> str:
        """格式化光标位置为字符串"""
        loc = cur.location
        if loc and loc.file:
            return f"{loc.file}:{loc.line}:{loc.column}"
        return ""

    @staticmethod
    def iter_children(cur: "cindex.Cursor"):
        # Provide a stable list to use len() for tree connectors.
        return [c for c in cur.get_children()]

    @staticmethod
    def in_main_file_only(tu: "cindex.TranslationUnit", cur: "cindex.Cursor") -> bool:
        loc = cur.location
        if not loc or not loc.file:
            # Keep nodes without a file (e.g., some implicit or synthesized nodes).
            return True
        # Compare canonicalized paths if available.
        try:
            return os.path.samefile(str(loc.file), tu.spelling)
        except Exception:
            return str(loc.file) == tu.spelling

    def extract(
        self, source_file: str, optional: Optional[ClangExtractorOptional] = None
    ) -> CursorExtractVisitor:
        """从源文件中提取声明信息"""
        if optional is None:
            optional = ClangExtractorOptional()

        c_args = optional.c_args
        main_file_only = optional.main_file_only

        tu: Optional[cindex.TranslationUnit] = None
        try:
            index = cindex.Index.create()
            tu = index.parse(
                source_file,
                args=optional.c_args,
                options=(
                    cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
                    | cindex.TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION
                    # | cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
                ),
            )
            if not tu:
                raise cindex.TranslationUnitLoadError(
                    "Failed to create translation unit"
                )
        except Exception as e:
            sys.stderr.write(f"Failed to parse {source_file}: {e}\n")
            sys.stderr.write("Command line arguments: " + str(optional.c_args) + "\n")
            # Print diagnostics even if parsing failed
            if tu:
                sys.stderr.write(ClangDebugPrinter.print_diagnostics(tu) + "\n")
            raise

        debug_level = optional.debug_level

        if debug_level == 0:
            # 仅打印诊断信息
            print(
                ClangDebugPrinter.get_info(tu, print_tree=False, print_diagnostics=True)
            )
        elif debug_level >= 1:
            # 打印光标树和诊断信息
            print(
                ClangDebugPrinter.get_info(tu, print_tree=True, print_diagnostics=True)
            )
            print(f"Args: {c_args}")

        # 创建访问器链
        filter_visitor = CursorFilterVisitor(main_file_only)
        extract_visitor = CursorExtractVisitor()
        visitor_chain = VisitorChain([filter_visitor, extract_visitor])
        if tu.cursor:
            visitor_chain.traverse(tu.cursor)

        if debug_level >= 1:
            extract_visitor.print_summary()

        return extract_visitor


if __name__ == "__main__":
    extractor = ClangExtractor(
        "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll",
    )

    res = extractor.extract(
        rf"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\utils\clang\test\mcal_example.c",
        optional=ClangExtractorOptional(
            c_args=[
                "-std=c99",
                rf"-IU:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\utils\clang\test\inc",
                rf"-IU:\Users\Enlink\Documents\gcc-arm-none-eabi-10.3-2021.10\arm-none-eabi\include",
                rf"-IU:\Users\Enlink\Documents\gcc-arm-none-eabi-10.3-2021.10\lib\gcc\arm-none-eabi\14.2.1\include",
            ],
            debug_level=1,
            main_file_only=True,
        ),
    )
