import clang.cindex
import sys
import os

def print_ast(node: clang.cindex.Cursor, indent=0):
    prefix = "  " * indent
    info = f'{node.kind.name:<20}'

    # Typedef
    if node.kind == clang.cindex.CursorKind.TYPEDEF_DECL:
        info += f' | typedef: {node.spelling} -> {node.underlying_typedef_type.spelling}'
    # Struct/Union/Enum
    elif node.kind in (
        clang.cindex.CursorKind.STRUCT_DECL,
        clang.cindex.CursorKind.UNION_DECL,
        clang.cindex.CursorKind.ENUM_DECL,
    ):
        info += f' | name: {node.spelling}'
    # Function
    elif node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        params = [f"{c.type.spelling} {c.spelling}" for c in node.get_arguments()]
        info += f' | function: {node.spelling}({", ".join(params)}) -> {node.result_type.spelling}'
    # Variable
    elif node.kind in (
        clang.cindex.CursorKind.VAR_DECL,
        clang.cindex.CursorKind.PARM_DECL,
        clang.cindex.CursorKind.FIELD_DECL,
    ):
        info += f' | var: {node.spelling} : {node.type.spelling}'
    # Macro
    elif node.kind == clang.cindex.CursorKind.MACRO_DEFINITION:
        info += f' | macro: {node.spelling}'
    # Enum Constant
    elif node.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
        info += f' | enum_const: {node.spelling} = {node.enum_value}'
    # Compound statement
    elif node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
        info += ' | { ... }'
    # If statement
    elif node.kind == clang.cindex.CursorKind.IF_STMT:
        info += ' | if (...)'
    # For/While/Do
    elif node.kind == clang.cindex.CursorKind.FOR_STMT:
        info += ' | for (...)'
    elif node.kind == clang.cindex.CursorKind.WHILE_STMT:
        info += ' | while (...)'
    elif node.kind == clang.cindex.CursorKind.DO_STMT:
        info += ' | do {...} while (...)'
    # Return
    elif node.kind == clang.cindex.CursorKind.RETURN_STMT:
        info += ' | return ...'

    # General info
    # info += f' | display: "{node.displayname}"'
    # if hasattr(node, "type") and node.type:
    #     info += f' | type: "{getattr(node.type, "spelling", "")}"'
    # if hasattr(node, "location") and node.location and node.location.file:
    #     info += (
    #         f" | loc: {node.location.file}:{node.location.line}:{node.location.column}"
    #     )
    # if hasattr(node, "is_definition") and node.is_definition():
    #     info += " | is_definition"
    # if hasattr(node, "storage_class") and node.storage_class:
    #     info += f" | storage_class: {node.storage_class.name}"
    # if hasattr(node, "access_specifier") and node.access_specifier:
    #     info += f" | access: {node.access_specifier.name}"
    # if hasattr(node, "brief_comment") and node.brief_comment:
    #     info += f' | comment: "{node.brief_comment}"'

    print(prefix + info)
    for child in node.get_children():
        print_ast(child, indent + 1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clang AST Explorer")
    parser.add_argument(
        "c_file", nargs="?", default=None, help="C source/header file to parse"
    )
    parser.add_argument(
        "--libclang",
        default=r"U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll",
        help="Path to libclang.dll",
    )
    parser.add_argument("--std", default="c99", help="C standard (default: c99)")
    args = parser.parse_args()

    clang.cindex.Config.set_library_file(args.libclang)

    c_file = args.c_file
    if not c_file:
        print("No input file specified. Please provide a C file path as argument.")
        sys.exit(1)
    if not os.path.isfile(c_file):
        print(f"File not found: {c_file}")
        sys.exit(1)

    index = clang.cindex.Index.create()
    tu = index.parse(c_file, args=[f"-std={args.std}"])

    print(f"Translation unit: {tu.spelling}")
    print_ast(tu.cursor)