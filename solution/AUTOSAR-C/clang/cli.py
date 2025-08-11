#!/usr/bin/env python3
# cindex_call.py
# Minimal CLI to invoke libclang via clang.cindex, with optional full AST printing.

import sys
import os
import argparse

# 获取当前文件所在目录（clang目录）
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将顶级包目录添加到Python路径
sys.path.insert(0, current_dir)

from modules.c_node_printer import print_ast_tree, extract_declarations, print_extracted_declarations, generate_markdown_report

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


def build_arg_parser() -> argparse.ArgumentParser:
    # Advanced: allow passing all custom clang args if --target is not given
    # Example: --clang-arg -march=armv7-m --clang-arg -mfloat-abi=hard --clang-arg -fno-builtin
    p = argparse.ArgumentParser(
        description="Parse a C/C++ source with libclang; optionally print the AST."
    )
    # Source input: path or stdin
    p.add_argument("source", help="Source file path or '-' to read from stdin")

    # libclang location
    p.add_argument(
        "--libclang",
        help="Path to libclang shared library (e.g., /usr/lib/libclang.so, libclang.dll, libclang.dylib).",
    )

    # Language and standard
    p.add_argument(
        "-x",
        "--language",
        choices=["c", "c++", "objective-c", "objective-c++"],
        help="Language kind passed to Clang (-x).",
    )
    p.add_argument(
        "--std",
        help="Language standard (e.g., c99, gnu11, c11, c17, c2x, c++17, gnu++20).",
    )
    p.add_argument(
        "--target",
        help="Target triple (e.g., x86_64-unknown-linux-gnu, aarch64-apple-darwin).",
    )

    # Includes and macros
    p.add_argument(
        "-I",
        "--include",
        action="append",
        default=[],
        help="Add include directory. Repeatable.",
    )
    p.add_argument(
        "--isystem",
        action="append",
        default=[],
        help="Add system include directory. Repeatable.",
    )
    p.add_argument(
        "-D",
        "--define",
        action="append",
        default=[],
        help="Define macro (NAME or NAME=VALUE). Repeatable.",
    )
    p.add_argument(
        "-U",
        "--undefine",
        action="append",
        default=[],
        help="Undefine macro NAME. Repeatable.",
    )
    p.add_argument(
        "--include-file",
        action="append",
        default=[],
        help="Force include file (-include). Repeatable.",
    )

    # Built-in includes control and resources
    p.add_argument(
        "--resource-dir", help="Set Clang resource directory (for built-in headers)."
    )
    p.add_argument(
        "--nostdinc", action="store_true", help="Ignore standard system include paths."
    )
    p.add_argument(
        "--nostdincpp", action="store_true", help="Ignore standard C++ include paths."
    )

    # TU options (libclang side)
    p.add_argument(
        "--skip-function-bodies",
        action="store_true",
        help="Ask parser to skip function bodies (faster, less complete).",
    )
    p.add_argument(
        "--detailed-pp-record",
        action="store_true",
        help="Enable detailed preprocessing record in the TU.",
    )
    p.add_argument(
        "--single-file-parse",
        action="store_true",
        help="Parse only the main file, not transitive headers.",
    )

    # Diagnostics
    p.add_argument(
        "--no-diags",
        action="store_true",
        help="Do not print diagnostics (exit code still reflects errors).",
    )

    # Stdin mode controls
    p.add_argument(
        "--virtual-filename",
        default="__stdin__.c",
        help="Filename to associate with stdin when source is '-'.",
    )

    # Passthrough arbitrary Clang args
    p.add_argument(
        "--clang-arg",
        action="append",
        default=[],
        help="Additional raw argument to pass directly to Clang. Repeatable.",
    )

    # AST printing controls
    p.add_argument(
        "--print-ast", action="store_true", help="Print the full AST as an ASCII tree."
    )
    p.add_argument(
        "--extract-decls", action="store_true", help="Extract and print struct, variable, and function declarations."
    )
    p.add_argument(
        "--ast-max-depth",
        type=int,
        default=None,
        help="Limit AST printing to this depth (root=0).",
    )
    p.add_argument(
        "--ast-main-file-only",
        action="store_true",
        help="Only show nodes whose locations come from the main file.",
    )
    p.add_argument(
        "--ast-show-type",
        action="store_true",
        help="Show cursor.type.spelling next to each node.",
    )
    p.add_argument(
        "--ast-show-canonical",
        action="store_true",
        help="When showing type, also show canonical type.",
    )
    p.add_argument(
        "--ast-show-usr",
        action="store_true",
        help="Show Unified Symbol Resolution (USR) for each node.",
    )
    p.add_argument(
        "--ast-include-pp",
        action="store_true",
        help="Include preprocessing cursors (MACRO_DEFINITION/INSTANTIATION). Implies detailed PP record.",
    )

    return p


def configure_libclang(libclang_path: str | None) -> None:
    if libclang_path:
        cindex.Config.set_library_file(libclang_path)
        return
    env_path = os.environ.get("LIBCLANG_PATH")
    if env_path:
        if os.path.isdir(env_path):
            cindex.Config.set_library_path(env_path)
        else:
            cindex.Config.set_library_file(env_path)


def build_compile_args(ns: argparse.Namespace) -> list[str]:
    args: list[str] = []

    # Language and standard
    if ns.language:
        args.extend(["-x", ns.language])
    if ns.std:
        args.append(f"-std={ns.std}")
    if ns.target:
        args.extend(["--target", ns.target])

    # Includes and macros
    for inc in ns.include:
        args.append(f"-I{inc}")
    for inc in ns.isystem:
        args.extend(["-isystem", inc])
    for d in ns.define:
        args.append(f"-D{d}")
    for u in ns.undefine:
        args.append(f"-U{u}")
    for f in ns.include_file:
        args.extend(["-include", f])

    # Built-in include behavior
    if ns.nostdinc:
        args.append("-nostdinc")
    if ns.nostdincpp:
        args.append("-nostdinc++")
    if ns.resource_dir:
        args.extend(["-resource-dir", ns.resource_dir])

    # Passthrough
    args.extend(ns.clang_arg)

    return args


def build_tu_options(ns: argparse.Namespace) -> int:
    opts = 0
    if ns.skip_function_bodies:
        opts |= cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
    if ns.detailed_pp_record or ns.ast_include_pp:
        opts |= cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    if ns.single_file_parse:
        opts |= cindex.TranslationUnit.PARSE_SINGLE_FILE
    return opts


def print_diagnostics(tu: "cindex.TranslationUnit") -> int:
    max_sev = 0
    for d in tu.diagnostics:
        loc = d.location
        where = ""
        if loc and loc.file:
            where = f"{loc.file}:{loc.line}:{loc.column}: "
        sev_name = d.severity.name if hasattr(d.severity, "name") else str(d.severity)
        print(f"{where}{sev_name}: {d.spelling}")
        max_sev = max(max_sev, SEVERITY_ORDER.get(d.severity, 0))
    return 1 if max_sev >= SEVERITY_ORDER[cindex.Diagnostic.Error] else 0


def format_loc(cur: "cindex.Cursor") -> str:
    loc = cur.location
    if loc and loc.file:
        return f"{loc.file}:{loc.line}:{loc.column}"
    return ""


def main(argv: list[str]) -> int:
    ap = build_arg_parser()

    # extend argv
    argv.extend(
        [
            "--print-ast",
            "--libclang",
            "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll",
            "-I",
            "U:\\Users\\Enlink\\Documents\\code\\python\\DataDrivenFileGenerator\\solution\\AUTOSAR-C\\clang",
        ]
    )
    argv.extend(
        [
            "--language",
            "c",
            "--std",
            "c99",
            # "--target", "arm-none-eabi",
            "--print-ast",
            "--ast-include-pp",
            "--extract-decls"
            # "--ast-main-file-only",
        ]
    )
    ns = ap.parse_args(argv)

    configure_libclang(ns.libclang)

    index = cindex.Index.create()

    compile_args = build_compile_args(ns)
    tu_options = build_tu_options(ns)

    # If --target is not given, allow user to pass all advanced options via --clang-arg
    # Example usage:
    # python cli.py test_file.c --language c --std c99 --clang-arg -march=armv7-m --clang-arg -mfloat-abi=hard --clang-arg -fno-builtin --clang-arg -save-temps --clang-arg -dD --clang-arg -E --clang-arg -fno-strict-aliasing --detailed-pp-record --ast-include-pp --print-ast --libclang "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll"

    unsaved_files = None
    source_path = ns.source
    if ns.source == "-":
        source_text = sys.stdin.read()
        source_path = ns.virtual_filename
        unsaved_files = [(source_path, source_text)]

    try:
        tu = cindex.TranslationUnit.from_source(
            source_path,
            args=compile_args,
            options=tu_options,
            unsaved_files=unsaved_files,
        )
    except cindex.TranslationUnitLoadError as e:
        sys.stderr.write(f"Failed to parse TU: {e}\n")
        return 2

    exit_code = 0
    if not ns.no_diags:
        exit_code = print_diagnostics(tu)

    # Print AST if requested
    if ns.print_ast:
        serialized_ast_tree = print_ast_tree(
            tu,
            tu.cursor,
            max_depth=ns.ast_max_depth,
            main_file_only=ns.ast_main_file_only,
            show_type=ns.ast_show_type,
            show_canonical=ns.ast_show_canonical,
            show_usr=ns.ast_show_usr,
            include_pp=ns.ast_include_pp,
        )
        print(serialized_ast_tree)
        with open("ast_output.txt", "w", encoding="utf-8") as f:
            f.write(serialized_ast_tree)
        print(f"AST tree written to ast_output.txt")
    
    # Extract declarations if requested
    if ns.extract_decls:
        declarations = extract_declarations(tu, main_file_only=ns.ast_main_file_only)
        print_extracted_declarations(declarations)
        
        # Generate Markdown report
        source_filename = os.path.basename(ns.source) if ns.source != "-" else ns.virtual_filename
        # markdown_content = generate_markdown_report(declarations, source_filename)
        
        # Save Markdown report
        # with open("declarations_report.md", "w", encoding="utf-8") as f:
        #     f.write(markdown_content)
        # print(f"Markdown report written to declarations_report.md")
        
        # Also save the old text format for compatibility
        with open("declarations_output.txt", "w", encoding="utf-8") as f:
            f.write("=== STRUCT DECLARATIONS ===\n")
            for struct in declarations['structs']:
                f.write(f"{struct}\n")
            
            f.write("\n=== UNION DECLARATIONS ===\n")
            for union in declarations['unions']:
                f.write(f"{union}\n")
            
            f.write("\n=== ENUM DECLARATIONS ===\n")
            for enum in declarations['enums']:
                f.write(f"{enum}\n")
            
            f.write("\n=== TYPEDEF DECLARATIONS ===\n")
            for typedef in declarations['typedefs']:
                f.write(f"{typedef}\n")
            
            f.write("\n=== VARIABLE DECLARATIONS ===\n")
            for var in declarations['variables']:
                f.write(f"{var}\n")
            
            f.write("\n=== FUNCTION DECLARATIONS ===\n")
            for func in declarations['functions']:
                f.write(f"{func}\n")
            
            f.write("\n=== MACRO DEFINITIONS ===\n")
            for macro in declarations['macros']:
                f.write(f"{macro}\n")
        print(f"Text report written to declarations_output.txt")
    # If we printed the AST, keep the diagnostic-derived exit code.
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

    rf"""
    python cli.py test_file.c --print-ast --lib "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll"
    python cli.py test_file.c --language c --std c99 --print-ast --lib "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll"

    python cli.py test_file.c --language c --std c99 --target arm-none-eabi -D __arm__ -D __ARM_ARCH_7M__ --detailed-pp-record --ast-include-pp --print-ast --libclang "U:\\Users\\Enlink\\Documents\\clang+llvm-20.1.0-x86_64-pc-windows-msvc\\bin\\libclang.dll" -I "U:\Users\Enlink\Documents\gcc-arm-none-eabi-10.3-2021.10\arm-none-eabi\include" -I "U:\Users\Enlink\Documents\gcc-arm-none-eabi-10.3-2021.10\lib\gcc\arm-none-eabi\14.2.1\include"

    """
