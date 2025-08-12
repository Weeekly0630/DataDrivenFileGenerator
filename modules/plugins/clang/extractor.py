import sys
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# 自动添加项目根目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.plugins.c import Decl, Expr, Attr

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


class ClangDebugPrinter:
    """Clang调试打印器，用于打印光标和诊断信息"""

    def _serialize_cursor_tree(self, cursor: cindex.Cursor) -> str:
        """递归序列化Cursor树为字符串表示"""

        @staticmethod
        def traverse(
            cur: cindex.Cursor, depth: int = 0, is_last: bool = True, prefix: str = ""
        ) -> str:
            result = ""
            connector = "└── " if is_last else "├── "
            result += f"{prefix}{connector}{ClangExtractor.describe_node(cur,)}\n"
            # Prepare next prefix for children
            child_prefix = f"{prefix}    " if is_last else f"{prefix}│   "

            children = ClangExtractor.iter_children(cur)

            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                result += traverse(child, depth + 1, is_last_child, child_prefix)
            return result

        return traverse(cursor)

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
        tu: "cindex.TranslationUnit",
        print_tree: bool = False,
        print_diagnostics: bool = True,
    ) -> str:
        """获取TranslationUnit的基本信息"""
        result = ""
        if print_tree:
            result += "Cursor Tree:\n"
            result += ClangDebugPrinter()._serialize_cursor_tree(tu.cursor) + "\n"
        if print_diagnostics:
            result += "Diagnostics:\n"
            result += ClangDebugPrinter.print_diagnostics(tu) + "\n"

        return result


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
        
        # 宏收集相关
        self.used_macros = set()  # 全局收集使用的宏
        self.macro_definitions = {}  # 宏定义：{宏名: 宏值}

    @staticmethod
    def format_loc(cur: "cindex.Cursor") -> str:
        """格式化光标位置为字符串"""
        loc = cur.location
        if loc and loc.file:
            return f"{loc.file}:{loc.line}:{loc.column}"
        return ""

    @staticmethod
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
                    pieces.append(
                        f"type={t.spelling} [canon={t.get_canonical().spelling}]"
                    )
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

    def extract_declarations(
        self,
        source_file: str,
        c_args: List[str],
        debug_level: int = 0,
        main_file_only: bool = True,  # 仅处理主文件中的声明
    ) -> Any:
        """从源文件中提取声明信息"""
        structs = []
        variables = []
        functions = []
        enums = []
        unions = []
        typedefs = []
        macros = []

        # 清空宏收集缓存
        self.used_macros.clear()
        self.macro_definitions.clear()

        try:
            tu = cindex.TranslationUnit.from_source(
                source_file,
                args=c_args,
                options=(
                    cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
                    | cindex.TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION
                    | cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
                ),
            )
        except cindex.TranslationUnitLoadError as e:
            sys.stderr.write(f"Failed to parse {source_file}: {e}\n")

        if debug_level == 0:
            # 仅打印诊断信息
            print(
                ClangDebugPrinter.get_info(tu, print_tree=False, print_diagnostics=True)
            )
        elif debug_level == 1:
            # 打印光标树和诊断信息
            print(
                ClangDebugPrinter.get_info(tu, print_tree=True, print_diagnostics=True)
            )

        # 先收集宏定义
        if tu.cursor:
            self._collect_macro_definitions(tu.cursor)

        def traverse(cursor: cindex.Cursor):
            # Filter to main file if requested
            if main_file_only and cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
                if not ClangExtractor.in_main_file_only(tu, cursor):
                    return

            # Get comment for the current cursor
            comment: str = ClangExtractor.extract_comment(cursor)

            if cursor.kind == cindex.CursorKind.STRUCT_DECL:
                pass
            elif cursor.kind == cindex.CursorKind.VAR_DECL:
                variables.append(self.extract_variable(cursor))

            # Recursively traverse children
            for child in cursor.get_children():
                traverse(child)

        # 遍历光标树
        if tu.cursor:
            traverse(tu.cursor)

        return {
            "structs": structs,
            "variables": variables,
            "functions": functions,
            "enums": enums,
            "unions": unions,
            "typedefs": typedefs,
            "macros": macros,
            "used_macros": list(self.used_macros),
            "macro_definitions": self.macro_definitions,
        }

    @staticmethod
    def extract_comment(cursor: "cindex.Cursor") -> str:
        """Extract comment text from cursor."""
        try:
            comment = cursor.brief_comment
            if comment:
                return comment
            comment = cursor.raw_comment
            if comment:
                return comment
        except:
            pass
        return ""

    def _collect_macro_definitions(self, cursor: "cindex.Cursor") -> None:
        """收集所有宏定义"""
        for child in cursor.walk_preorder():
            if child.kind == cindex.CursorKind.MACRO_DEFINITION:
                macro_name = child.spelling
                # 提取宏值（从 tokens）
                tokens = list(child.get_tokens())
                if len(tokens) > 1:  # 跳过宏名本身
                    macro_value = " ".join(t.spelling for t in tokens[1:])
                else:
                    macro_value = ""
                self.macro_definitions[macro_name] = macro_value

    def _collect_macro_usage_in_node(self, cursor: "cindex.Cursor") -> None:
        """递归收集某个节点中的宏使用"""
        for child in cursor.walk_preorder():
            if child.kind == cindex.CursorKind.DECL_REF_EXPR:
                ref_name = child.spelling
                if ref_name in self.macro_definitions:
                    self.used_macros.add(ref_name)
            elif child.kind == cindex.CursorKind.MACRO_INSTANTIATION:
                self.used_macros.add(child.spelling)

    def _get_macros_in_node(self, cursor: "cindex.Cursor") -> List[str]:
        """获取某个节点中使用的宏列表"""
        node_macros = set()
        for child in cursor.walk_preorder():
            if child.kind == cindex.CursorKind.DECL_REF_EXPR:
                ref_name = child.spelling
                if ref_name in self.macro_definitions:
                    node_macros.add(ref_name)
            elif child.kind == cindex.CursorKind.MACRO_INSTANTIATION:
                node_macros.add(child.spelling)
        return list(node_macros)

    @staticmethod
    def extract_type_modifier(ctype: "cindex.Type") -> Decl.TypeModifier.MetaData:
        """从cindex.Type对象中提取类型修饰符信息，便于变量和字段等复用"""
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
        attributes = []

        return Decl.TypeModifier.MetaData(
            type=Decl.TypeRef.MetaData(ref=ctype.spelling),
            qualifiers=qualifiers_str,
            attributes=attributes,
            pointer_level=pointer_level,
            array_dims=array_dims,
        )

    def extract_init_expr_text(self, cursor: "cindex.Cursor") -> str:
        """提取初始化表达式的文本，同时收集宏使用"""
        # 方法1: 使用 cursor 的 extent 来限制 token 范围
        if hasattr(cursor, "extent") and cursor.extent:
            start = cursor.extent.start
            end = cursor.extent.end
            tokens = []

            # 只收集在当前 cursor extent 范围内的 token
            for token in cursor.get_tokens():
                # 检查 token 是否在当前 cursor 的范围内
                if (
                    token.location.file.name == start.file.name
                    and start.offset <= token.location.offset <= end.offset
                ):
                    # 检查是否为宏引用，如果是就记录
                    if token.spelling in self.macro_definitions:
                        self.used_macros.add(token.spelling)
                    tokens.append(token.spelling)
                elif token.location.offset > end.offset:
                    # 如果超出范围就停止
                    break

            if tokens:
                return " ".join(tokens)

        # 方法2: 如果没有 extent，尝试递归子节点
        parts = []
        for child in cursor.get_children():
            child_text = self.extract_init_expr_text(child)
            if child_text:
                parts.append(child_text)

        # 同时收集该节点的宏使用
        self._collect_macro_usage_in_node(cursor)

        return " ".join(parts) if parts else cursor.spelling or ""

    def extract_variable(self, cursor: cindex.Cursor) -> Decl.Variable.MetaData:
        """从VAR_DECL节点中提取变量声明元数据"""
        name = cursor.spelling
        ctype = cursor.type
        modifier = ClangExtractor.extract_type_modifier(ctype)

        # storage_class 只在变量声明时有意义
        storage_class = ""
        if hasattr(cursor, "storage_class") and cursor.storage_class is not None:
            sc = cursor.storage_class
            # StorageClass.NONE 表示没有存储类别
            if hasattr(sc, "name") and sc != cindex.StorageClass.NONE:
                storage_class = str(sc.name)

        # 初始化表达式（如有）
        init_expr = None
        for child in cursor.get_children():
            if child.kind in (
                cindex.CursorKind.UNEXPOSED_EXPR,
                cindex.CursorKind.BINARY_OPERATOR,
                cindex.CursorKind.INTEGER_LITERAL,
                cindex.CursorKind.FLOATING_LITERAL,
                cindex.CursorKind.STRING_LITERAL,
                cindex.CursorKind.CHARACTER_LITERAL,
                cindex.CursorKind.CALL_EXPR,
                cindex.CursorKind.DECL_REF_EXPR,
                cindex.CursorKind.MACRO_INSTANTIATION,
                cindex.CursorKind.MACRO_DEFINITION,
                cindex.CursorKind.PAREN_EXPR,
            ):
                init_expr = self.extract_init_expr_text(child)
                if init_expr:
                    break
        
        # 收集该变量声明中使用的宏
        self._collect_macro_usage_in_node(cursor)
        
        # 注释
        comment = cursor.raw_comment or cursor.brief_comment or ""

        return Decl.Variable.MetaData(
            name=name,
            storage_class=storage_class,
            modifier=modifier,
            init_expr=init_expr,
            comment=comment,
        )


if __name__ == "__main__":
    extractor = ClangExtractor(
        "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll"
    )

    res = extractor.extract_declarations(
        rf"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\clang\test\test_simple.c",
        c_args=[
            "-x",
            "c",
            "-std=c99",
            "-detailed-preprocessing-record",  # 保留预处理信息，包括宏
            "-IU:\\Users\\Enlink\\Documents\\code\\python\\DataDrivenFileGenerator\\solution\\AUTOSAR-C\\clang",
            "-IU:\\Users\\Enlink\\Documents\\参考文档\\AUTOSAR_SampleProject_S32K144-master\\plugins\\I2c_TS_T40D2M10I1R0\\include",
        ],
        debug_level=1,
    )

    for var in res["variables"]:
        print(var)
    
    print("\n=== 宏定义 ===")
    for macro_name, macro_value in res["macro_definitions"].items():
        print(f"#define {macro_name} {macro_value}")
    
    print("\n=== 使用的宏 ===")
    for macro in res["used_macros"]:
        print(f"使用了宏: {macro}")
