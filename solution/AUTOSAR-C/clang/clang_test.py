def format_location(location):
    """格式化位置信息"""
    if location and location.file:
        return f"{Path(location.file.name).name}:{location.line}:{location.column}"
    return "unknown"
def get_tokens_for_node(node, translation_unit):
    """获取节点对应的token序列"""
    try:
        extent = node.extent
        tokens = list(translation_unit.get_tokens(extent=extent))
        return " ".join([token.spelling for token in tokens])
    except:
        return ""
def print_ast(node, translation_unit=None, indent=0, show_location=True, show_tokens=False):
    """递归打印AST树"""
    prefix = "  " * indent
    info = f'{node.kind.name:<25}'
    # 基本信息
    if node.spelling:
        info += f' | name: "{node.spelling}"'
    # 根据节点类型添加详细信息
    if node.kind == clang.cindex.CursorKind.TYPEDEF_DECL:
        try:
            underlying = node.underlying_typedef_type.spelling
            info += f' | typedef: {node.spelling} -> {underlying}'
        except:
            info += f' | typedef: {node.spelling}'
    
    elif node.kind in (
        clang.cindex.CursorKind.STRUCT_DECL,
        clang.cindex.CursorKind.UNION_DECL,
        clang.cindex.CursorKind.ENUM_DECL,
    ):
        if node.is_definition():
            info += f' | {node.kind.name.lower()}: {node.spelling} (definition)'
        else:
            info += f' | {node.kind.name.lower()}: {node.spelling} (declaration)'
    
    elif node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        try:
            params = []
            for arg in node.get_arguments():
                if arg and hasattr(arg, 'type') and arg.type:
                    param_info = f"{arg.type.spelling}"
                    if hasattr(arg, 'spelling') and arg.spelling:
                        param_info += f" {arg.spelling}"
                    params.append(param_info)
            
            return_type = node.result_type.spelling if node.result_type else "void"
            info += f' | func: {return_type} {node.spelling}({", ".join(params)})'
            
            if node.is_definition():
                info += ' (definition)'
            else:
                info += ' (declaration)'
        except Exception as e:
            info += f' | func: {node.spelling} (error: {e})'
    
    elif node.kind in (
        clang.cindex.CursorKind.VAR_DECL,
        clang.cindex.CursorKind.PARM_DECL,
        clang.cindex.CursorKind.FIELD_DECL,
    ):
        try:
            type_spelling = node.type.spelling if node.type else "unknown"
            info += f' | var: {type_spelling} {node.spelling}'
            
            # 尝试获取初始值
            if show_tokens and translation_unit:
                tokens = get_tokens_for_node(node, translation_unit)
                if "=" in tokens:
                    info += f' | init: {tokens.split("=", 1)[1].strip().rstrip(";")}'
        except Exception as e:
            info += f' | var: {node.spelling} (error: {e})'
    
    elif node.kind == clang.cindex.CursorKind.MACRO_DEFINITION:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            # 移除第一个token（宏名）和最后可能的换行
            token_list = tokens.split()
            if len(token_list) > 1:
                macro_body = " ".join(token_list[1:])
                info += f' | macro: #define {node.spelling} {macro_body}'
            else:
                info += f' | macro: #define {node.spelling}'
        else:
            info += f' | macro: #define {node.spelling}'
    
    elif node.kind == clang.cindex.CursorKind.MACRO_INSTANTIATION:
        info += f' | macro_use: {node.spelling}'
    
    elif node.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | include: {tokens}'
        else:
            info += f' | include: {node.spelling}'
    
    elif node.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
        try:
            value = node.enum_value
            info += f' | enum_const: {node.spelling} = {value}'
        except:
            info += f' | enum_const: {node.spelling}'
    
    # 语句类型
    elif node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
        info += ' | { compound_statement }'
    elif node.kind == clang.cindex.CursorKind.IF_STMT:
        info += ' | if_statement'
    elif node.kind == clang.cindex.CursorKind.FOR_STMT:
        info += ' | for_statement'
    elif node.kind == clang.cindex.CursorKind.WHILE_STMT:
        info += ' | while_statement'
    elif node.kind == clang.cindex.CursorKind.DO_STMT:
        info += ' | do_while_statement'
    elif node.kind == clang.cindex.CursorKind.RETURN_STMT:
        info += ' | return_statement'
    elif node.kind == clang.cindex.CursorKind.BREAK_STMT:
        info += ' | break_statement'
    elif node.kind == clang.cindex.CursorKind.CONTINUE_STMT:
        info += ' | continue_statement'
    
    # 表达式类型
    elif node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        info += f' | ref: {node.spelling}'
    elif node.kind == clang.cindex.CursorKind.INTEGER_LITERAL:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | int_literal: {tokens}'
        else:
            info += ' | int_literal'
    elif node.kind == clang.cindex.CursorKind.STRING_LITERAL:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | string_literal: {tokens}'
        else:
            info += ' | string_literal'
    elif node.kind == clang.cindex.CursorKind.CHARACTER_LITERAL:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | char_literal: {tokens}'
        else:
            info += ' | char_literal'
    elif node.kind == clang.cindex.CursorKind.FLOATING_LITERAL:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | float_literal: {tokens}'
        else:
            info += ' | float_literal'
    
    # 二元操作符
    elif node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | binary_op: {tokens}'
        else:
            info += ' | binary_operator'
    elif node.kind == clang.cindex.CursorKind.UNARY_OPERATOR:
        if show_tokens and translation_unit:
            tokens = get_tokens_for_node(node, translation_unit)
            info += f' | unary_op: {tokens}'
        else:
            info += ' | unary_operator'
    elif node.kind == clang.cindex.CursorKind.CALL_EXPR:
        info += f' | function_call: {node.spelling}'
    
    # 类型信息
    if node.type and node.type.spelling and node.kind not in [
        clang.cindex.CursorKind.FUNCTION_DECL,
        clang.cindex.CursorKind.VAR_DECL,
        clang.cindex.CursorKind.PARM_DECL,
        clang.cindex.CursorKind.FIELD_DECL,
    ]:
        info += f' | type: {node.type.spelling}'

    # 位置信息
    if show_location:
        loc = format_location(node.location)
        info += f' | @{loc}'

    # 定义/声明标记
    if hasattr(node, 'is_definition') and node.is_definition():
        info += ' | [DEF]'

    print(prefix + info)
    
    # 递归打印子节点
    for child in node.get_children():
        print_ast(child, translation_unit, indent + 1, show_location, show_tokens)
def print_diagnostics(translation_unit):
    """打印诊断信息（错误和警告）"""
    diagnostics = list(translation_unit.diagnostics)
    if diagnostics:
        print("\n=== DIAGNOSTICS ===")
        for diag in diagnostics:
            severity = {
                clang.cindex.Diagnostic.Ignored: "IGNORED",
                clang.cindex.Diagnostic.Note: "NOTE",
                clang.cindex.Diagnostic.Warning: "WARNING", 
                clang.cindex.Diagnostic.Error: "ERROR",
                clang.cindex.Diagnostic.Fatal: "FATAL"
            }.get(diag.severity, "UNKNOWN")
            
            location = format_location(diag.location)
            print(f"[{severity}] {location}: {diag.spelling}")
        print("=" * 20)
def print_file_includes(translation_unit):
    """打印文件包含信息"""
    print("\n=== FILE INCLUDES ===")
    includes = []
    
    def collect_includes(cursor):
        if cursor.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
            included_file = cursor.get_included_file()
            if included_file:
                includes.append(included_file.name)
        
        for child in cursor.get_children():
            collect_includes(child)
    
    collect_includes(translation_unit.cursor)
    
    if includes:
        for include in includes:
            print(f"  #include {Path(include).name}")
    else:
        print("  No includes found")
    print("=" * 20)

# === core_ast.py ===
import clang.cindex
import sys
import os
from pathlib import Path

class ClangAstParser:
    def __init__(self, libclang_path=None):
        if libclang_path:
            clang.cindex.Config.set_library_file(libclang_path)
        self.index = clang.cindex.Index.create()

    def parse(self, c_file, compile_args=None, parse_options=None):
        if compile_args is None:
            compile_args = []
        if parse_options is None:
            parse_options = clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        return self.index.parse(c_file, args=compile_args, options=parse_options)

    @staticmethod
    def print_diagnostics(translation_unit):
        diagnostics = list(translation_unit.diagnostics)
        if diagnostics:
            print("\n=== DIAGNOSTICS ===")
            for diag in diagnostics:
                severity = {
                    clang.cindex.Diagnostic.Ignored: "IGNORED",
                    clang.cindex.Diagnostic.Note: "NOTE",
                    clang.cindex.Diagnostic.Warning: "WARNING", 
                    clang.cindex.Diagnostic.Error: "ERROR",
                    clang.cindex.Diagnostic.Fatal: "FATAL"
                }.get(diag.severity, "UNKNOWN")
                location = format_location(diag.location)
                print(f"[{severity}] {location}: {diag.spelling}")
            print("=" * 20)

    @staticmethod
    def print_file_includes(translation_unit):
        print("\n=== FILE INCLUDES ===")
        includes = []
        def collect_includes(cursor):
            if cursor.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
                included_file = cursor.get_included_file()
                if included_file:
                    includes.append(included_file.name)
            for child in cursor.get_children():
                collect_includes(child)
        collect_includes(translation_unit.cursor)
        if includes:
            for include in includes:
                print(f"  #include {Path(include).name}")
        else:
            print("  No includes found")
        print("=" * 20)

    @staticmethod
    def print_ast(node, translation_unit=None, indent=0, show_location=True, show_tokens=False):
        print_ast(node, translation_unit, indent, show_location, show_tokens)


# === CLI Entrypoint ===
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clang AST CLI Tool")
    parser.add_argument(
        "c_file", nargs="?", default=None, help="C source/header file to parse"
    )
    parser.add_argument(
        "--libclang",
        default=r"U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll",
        help="Path to libclang.dll",
    )
    parser.add_argument("--std", default="c99", help="C standard (default: c99)")
    parser.add_argument("--show-location", action="store_true", help="Show location information")
    parser.add_argument("--show-tokens", action="store_true", help="Show token information for nodes")
    parser.add_argument("--show-includes", action="store_true", help="Show file includes")
    parser.add_argument("--show-diagnostics", action="store_true", help="Show compilation diagnostics")
    parser.add_argument("--parse-detailed", action="store_true", help="Parse with detailed options including macro expansion")
    parser.add_argument("-I", "--include", action="append", default=[], help="Add include directory")
    parser.add_argument("-D", "--define", action="append", default=[], help="Add preprocessor definition")
    args = parser.parse_args()

    parser_core = ClangAstParser(libclang_path=args.libclang)

    c_file = args.c_file
    if not c_file:
        print("No input file specified. Please provide a C file path as argument.")
        print("Usage: python clang_test.py <c_file> [options]")
        sys.exit(1)
    if not os.path.isfile(c_file):
        print(f"File not found: {c_file}")
        sys.exit(1)

    compile_args = [f"-std={args.std}"]
    for include_dir in args.include:
        compile_args.append(f"-I{include_dir}")
    for define in args.define:
        compile_args.append(f"-D{define}")
    if args.parse_detailed:
        compile_args.extend([
            "-detailed-preprocessing-record",
            "-fparse-all-comments",
        ])

    print(f"Parsing file: {c_file}")
    print(f"Compile args: {' '.join(compile_args)}")
    print("=" * 50)

    parse_options = clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    if args.parse_detailed:
        parse_options |= clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES

    translation_unit = parser_core.parse(
        c_file,
        compile_args=compile_args,
        parse_options=parse_options
    )

    if args.show_diagnostics:
        parser_core.print_diagnostics(translation_unit)
    if args.show_includes:
        parser_core.print_file_includes(translation_unit)

    print(f"\n=== AST for {translation_unit.spelling} ===")
    if translation_unit.cursor:
        parser_core.print_ast(
            translation_unit.cursor,
            translation_unit,
            show_location=args.show_location,
            show_tokens=args.show_tokens
        )
    else:
        print("No cursor available for translation unit")
    print("=" * 50)

if __name__ == "__main__":
    main()