import sys
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Union, Optional

# 自动添加项目根目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.plugins.c import Decl, Expr, Attr, Preprocess

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

    def extract(
        self,
        source_file: str,
        c_args: List[str],
        debug_level: int = 0,
        main_file_only: bool = True,  # 仅处理主文件中的声明
        user_macro_only: bool = True,  # 仅处理用户自定义宏
    ) -> Any:
        """从源文件中提取声明信息"""
        structs = []
        variables = []
        functions = []
        enums = []
        unions = []
        typedefs = []
        macros = []

        # 预处理信息
        macro_definitions = []
        inclusion_directives = []
        macro_instantiations: List[Preprocess.MacroInstantiation.MetaData] = []

        # 保存宏实例化信息
        self.macro_instantiations = macro_instantiations

        # 初始化类型引用字典
        self.type_table: Dict[str, Any] = {}
        
        try:
            tu = cindex.TranslationUnit.from_source(
                source_file,
                args=c_args,
                options=(
                    cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
                    | cindex.TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION
                    # | cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
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
            print(f"Args: {c_args}")

        def traverse(cursor: cindex.Cursor):
            # Filter to main file if requested
            if main_file_only and cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
                if not ClangExtractor.in_main_file_only(tu, cursor):
                    return

            # Filter system file
            if user_macro_only and cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
                if not cursor.location.file:
                    return

            # Get comment for the current cursor
            comment: str = self.extract_comment(cursor)

            if cursor.kind == cindex.CursorKind.STRUCT_DECL:
                structs.append(self.extract_struct(cursor))
            elif cursor.kind == cindex.CursorKind.VAR_DECL:
                variables.append(self.extract_variable(cursor))
            elif cursor.kind == cindex.CursorKind.UNION_DECL:
                unions.append(self.extract_union(cursor))
            elif cursor.kind == cindex.CursorKind.MACRO_DEFINITION:
                macro_definitions.append(self.extract_macro_definition(cursor))
            elif cursor.kind == cindex.CursorKind.INCLUSION_DIRECTIVE:
                inclusion_directives.append(self.extract_inclusion_directive(cursor))
            elif cursor.kind == cindex.CursorKind.MACRO_INSTANTIATION:
                macro_instantiations.append(self.extract_macro_instantiation(cursor))
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
            "preprocessing": {
                "macro_definitions": macro_definitions,
                "inclusion_directives": inclusion_directives,
                "macro_instantiations": macro_instantiations,
            },
        }

    # @staticmethod
    # def extract_preprocessing(cursor: "cindex.Cursor", preprocessing_results: Dict[str, List]):
    #     """从光标中提取预处理相关的对象，结果存储到 preprocessing_results 中"""

    #     # 宏定义
    #     if cursor.kind == cindex.CursorKind.MACRO_DEFINITION:
    #         name = cursor.spelling
    #         # 提取宏值：跳过宏名本身
    #         tokens = list(cursor.get_tokens())
    #         value = " ".join(t.spelling for t in tokens[1:]) if len(tokens) > 1 else ""
    #         location = ClangExtractor.format_loc(cursor)

    #         # 提取宏参数（如果是函数式宏）
    #         params = []
    #         # 简单的参数提取逻辑，可根据需要完善

    #         preprocessing_results["macro_definitions"].append(
    #             Preprocess.MacroDefinition.MetaData(
    #                 name=name,
    #                 value=value,
    #                 location=location,
    #                 params=params
    #             )
    #         )

    #     # 包含指令
    #     elif cursor.kind == cindex.CursorKind.INCLUSION_DIRECTIVE:
    #         filename = cursor.spelling
    #         location = ClangExtractor.format_loc(cursor)
    #         # 判断是否为系统头文件（尖括号包含）
    #         is_system = filename.startswith("<") and filename.endswith(">")

    #         preprocessing_results["inclusion_directives"].append(
    #             Preprocess.InclusionDirective.MetaData(
    #                 filename=filename,
    #                 location=location,
    #                 is_system=is_system
    #             )
    #         )

    #     # 宏实例化
    #     elif cursor.kind == cindex.CursorKind.MACRO_INSTANTIATION:
    #         name = cursor.spelling
    #         location = ClangExtractor.format_loc(cursor)

    #         # 提取宏参数（如有）
    #         tokens = list(cursor.get_tokens())
    #         args = []
    #         if len(tokens) > 1:
    #             # 简单的参数提取，跳过宏名本身
    #             args = [t.spelling for t in tokens[1:]]

    #         preprocessing_results["macro_instantiations"].append(
    #             Preprocess.MacroInstantiation.MetaData(
    #                 name=name,
    #                 location=location,
    #                 args=args
    #             )
    #         )
    # @staticmethod

    def extract_code_by_extent(self, cursor: "cindex.Cursor") -> str:
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

    # @staticmethod
    def extract_comment(self, cursor: "cindex.Cursor") -> str:
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

    # @staticmethod
    def extract_type_modifier(self, ctype: "cindex.Type") -> Decl.TypeModifier.MetaData:
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

    # def extract_init_expr_text(self, cursor):
    #     expr_range = ClangExtractor.extract_source_range(cursor)
    #     macro_name = None
    #     if expr_range and hasattr(self, "macro_instantiations"):
    #         for macro in self.macro_instantiations:
    #             macro_range = macro.source_range
    #             # 只有当整个节点被宏完全覆盖时才替换
    #             if macro_range and (
    #                 macro_range.start.file == expr_range.start.file
    #                 and macro_range.start.line == expr_range.start.line
    #                 and macro_range.start.column == expr_range.start.column
    #                 and macro_range.end.line == expr_range.end.line
    #                 and macro_range.end.column == expr_range.end.column
    #             ):
    #                 macro_name = macro.name
    #                 break
    #     if macro_name:
    #         return macro_name
    #     # 否则递归处理所有子节点
    #     parts = []
    #     for child in cursor.get_children():
    #         child_text = self.extract_init_expr_text(child)
    #         if child_text:
    #             parts.append(child_text)
    #     return " ".join(parts) if parts else cursor.spelling or ""

    def extract_variable(self, cursor: cindex.Cursor) -> Decl.Variable.MetaData:
        """从VAR_DECL节点中提取变量声明元数据"""
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
        ctype = cursor.type
        modifier = self.extract_type_modifier(ctype)

        # 4. 初始化表达式（如有）
        init_expr = None
        for child in cursor.get_children():
            if child.kind in (
                cindex.CursorKind.UNEXPOSED_EXPR,
                cindex.CursorKind.BINARY_OPERATOR,
                cindex.CursorKind.INTEGER_LITERAL,
                cindex.CursorKind.INIT_LIST_EXPR,
                cindex.CursorKind.FLOATING_LITERAL,
                cindex.CursorKind.STRING_LITERAL,
                cindex.CursorKind.CHARACTER_LITERAL,
                cindex.CursorKind.CALL_EXPR,
                cindex.CursorKind.DECL_REF_EXPR,
                cindex.CursorKind.MACRO_INSTANTIATION,
                cindex.CursorKind.MACRO_DEFINITION,
                cindex.CursorKind.PAREN_EXPR,
            ):
                # 新增：判断是否被宏实例化覆盖
                # expr_range = ClangExtractor.extract_source_range(child)
                # macro_name = None
                # if expr_range and hasattr(self, "macro_instantiations"):
                #     for macro in self.macro_instantiations:
                #         macro_range = macro.source_range
                #         if macro_range and (
                #             macro_range.start.file == expr_range.start.file and
                #             macro_range.start.line <= expr_range.start.line <= macro_range.end.line and
                #             macro_range.start.column <= expr_range.start.column <= macro_range.end.column
                #         ):
                #             macro_name = macro.name
                #             break
                # if macro_name:
                #     # 如果有参数，拼接成 SQUARE(10)
                #     if macro.args:
                #         init_expr = f"{macro_name}({', '.join(macro.args)})"
                #     else:
                #         init_expr = macro_name
                # else:
                #     init_expr = self.extract_init_expr_text(child)
                # if init_expr:
                #     break
                init_expr = self.extract_code_by_extent(
                    child
                )  # self.extract_init_expr_text(child)
                break

        # 5. 注释
        comment = cursor.raw_comment or cursor.brief_comment or ""

        return Decl.Variable.MetaData(
            name=name,
            storage_class=storage_class,
            modifier=modifier,
            init_expr=init_expr,
            comment=comment,
            raw_code=self.extract_code_by_extent(cursor),
        )

    # @staticmethod
    def extract_fileds(self, cursor: cindex.Cursor) -> List[Decl.Field.MetaData]:
        """从STRUCT_DECL节点中提取字段信息"""
        if cursor.kind not in (
            cindex.CursorKind.STRUCT_DECL,
            cindex.CursorKind.UNION_DECL,
            cindex.CursorKind.ENUM_DECL,
        ):
            raise ValueError("Cursor is not a record declaration.")
        fields: List[Decl.Field.MetaData] = []

        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                # 提取字段名和类型
                name = child.spelling
                ctype = child.type
                modifier = self.extract_type_modifier(ctype)
                comment = self.extract_comment(child)
                bitfield_width = (
                    child.get_bitfield_width() if child.is_bitfield() else None
                )
                fields.append(
                    Decl.Field.MetaData(
                        name=name,
                        modifier=modifier,
                        bitfield_width=bitfield_width,
                        comment=comment,
                        raw_code=self.extract_code_by_extent(child),
                    )
                )
        return fields

    def extract_record(self, cursor: cindex.Cursor) -> Decl.Record.MetaData:
        """从STRUCT_DECL节点中提取记录（结构体、联合体、枚举等）信息"""
        if cursor.kind not in (
            cindex.CursorKind.STRUCT_DECL,
            cindex.CursorKind.UNION_DECL,
            cindex.CursorKind.ENUM_DECL,
        ):
            raise ValueError("Cursor is not a record declaration.")

        name = cursor.spelling
        fileds: List[Decl.Field.MetaData] = self.extract_fileds(cursor)

        qualifiers: str = ""
        comment = self.extract_comment(cursor)

        return Decl.Record.MetaData(
            name=name,
            fields=fileds,
            qualifiers=qualifiers,
            comment=comment,
        )

    # @staticmethod
    def extract_struct(self, cursor: cindex.Cursor) -> Decl.Struct.MetaData:
        """从STRUCT_DECL节点中提取结构体声明元数据"""
        record: Decl.Record.MetaData = self.extract_record(cursor)
        raw_code: str = self.extract_code_by_extent(cursor)

        return Decl.Struct.MetaData(
            record=record,
            raw_code=raw_code,
        )

    # @staticmethod
    def extract_union(self, cursor: cindex.Cursor) -> Decl.Union.MetaData:
        """从UNION_DECL节点中提取联合体声明元数据"""
        record: Decl.Record.MetaData = self.extract_record(cursor)
        raw_code: str = self.extract_code_by_extent(cursor)
        return Decl.Union.MetaData(
            record=record,
            raw_code=raw_code,
        )

    # @staticmethod
    # def extract_enum(cursor: cindex.Cursor) -> Decl.Enum.MetaData:
    # @staticmethod
    # def extract_location(cursor: cindex.Cursor) -> FileLocation.Location:
    #     loc = cursor.location
    #     if not loc or not loc.file:
    #         return FileLocation.Location(file="None", line=0, column=0, offset=None)
    #     else:
    #         return FileLocation.Location(
    #             file=loc.file,
    #             line=loc.line,
    #             column=loc.column,
    #             offset=loc.offset,
    #         )

    # @staticmethod
    # def extract_source_range(cursor: cindex.Cursor) -> Optional[FileLocation.Range]:
    #     extent = cursor.extent
    #     source_range = None
    #     if extent and extent.start.file:
    #         start = FileLocation.Location(
    #             file=str(extent.start.file),
    #             line=extent.start.line,
    #             column=extent.start.column,
    #             offset=getattr(extent.start, "offset", None),
    #         )
    #         end = FileLocation.Location(
    #             file=str(extent.end.file),
    #             line=extent.end.line,
    #             column=extent.end.column,
    #             offset=getattr(extent.end, "offset", None),
    #         )
    #         source_range = FileLocation.Range(start=start, end=end)
    #     return source_range

    @staticmethod
    def extract_macro_definition(
        cursor: cindex.Cursor,
    ) -> "Preprocess.MacroDefinition.MetaData":
        """从MACRO_DEFINITION节点中提取宏定义元数据"""
        name = cursor.spelling
        # 提取宏值：跳过宏名本身
        tokens = list(cursor.get_tokens())
        value = " ".join(t.spelling for t in tokens[1:]) if len(tokens) > 1 else ""

        # 提取宏参数（如果是函数式宏）
        params = []
        # 简单的参数提取逻辑，可根据需要完善

        return Preprocess.MacroDefinition.MetaData(
            name=name,
            value=value,
            # location=ClangExtractor.extract_location(cursor),
            params=params,
        )

    @staticmethod
    def extract_inclusion_directive(
        cursor: cindex.Cursor,
    ) -> "Preprocess.InclusionDirective.MetaData":
        """从INCLUSION_DIRECTIVE节点中提取包含指令元数据"""
        filename = cursor.spelling
        # 判断是否为系统头文件（尖括号包含）
        is_system = filename.startswith("<") and filename.endswith(">")

        return Preprocess.InclusionDirective.MetaData(
            filename=filename,
            # location=ClangExtractor.extract_location(cursor),
            is_system=is_system,
        )

    @staticmethod
    def extract_macro_instantiation(
        cursor: cindex.Cursor,
    ) -> "Preprocess.MacroInstantiation.MetaData":
        """从MACRO_INSTANTIATION节点中提取宏实例化元数据"""
        name = cursor.spelling

        tokens = list(cursor.get_tokens())
        args = []
        if len(tokens) > 2 and tokens[1].spelling == "(" and tokens[-1].spelling == ")":
            args = [t.spelling for t in tokens[2:-1]]
        elif len(tokens) > 1:
            args = [t.spelling for t in tokens[1:]]
        # # 提取 source range
        # extent = cursor.extent
        # if extent and extent.start.file:
        #     source_range = (
        #         f"{extent.start.file.name}:"
        #         f"{extent.start.line}:{extent.start.column}-"
        #         f"{extent.end.line}:{extent.end.column}"
        #     )
        # else:
        #     source_range = None
        return Preprocess.MacroInstantiation.MetaData(
            name=name,
            # location=ClangExtractor.extract_location(cursor),
            args=args,
            # source_range=ClangExtractor.extract_source_range(cursor),
        )


if __name__ == "__main__":
    extractor = ClangExtractor(
        "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll"
    )

    res = extractor.extract(
        rf"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\clang\test\test_struct.c",
        c_args=[
            # "-x",
            # "c",
            # "-std=c99",
            rf"-IU:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\clang\test\inc",
        ],
        debug_level=1,
        main_file_only=False,
    )

    for var in res["variables"]:
        print(var)

    # for macro in res["preprocessing"]["macro_definitions"]:
    #     print(macro)

    # for inc in res["preprocessing"]["inclusion_directives"]:
    #     print(inc)

    for macro_inst in res["preprocessing"]["macro_instantiations"]:
        print(macro_inst)
