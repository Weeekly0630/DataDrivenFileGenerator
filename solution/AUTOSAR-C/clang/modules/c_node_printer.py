import sys
import os
from typing import Optional

try:
    from clang import cindex
except ImportError as e:
    sys.stderr.write(
        "Error: Python bindings for libclang not found. Install 'clang' (pip) and ensure libclang is available.\n"
    )
    raise


def format_loc(cur: "cindex.Cursor") -> str:
    loc = cur.location
    if loc and loc.file:
        return f"{loc.file}:{loc.line}:{loc.column}"
    return ""


def describe_node(
    cur: "cindex.Cursor", show_type: bool, show_canonical: bool, show_usr: bool
) -> str:
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
    loc = format_loc(cur)
    if loc:
        pieces.append(f"@ {loc}")
    return " ".join(pieces)


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


def iter_children(cur: "cindex.Cursor"):
    # Provide a stable list to use len() for tree connectors.
    return [c for c in cur.get_children()]


def print_ast_tree(
    tu: "cindex.TranslationUnit",
    cur: "cindex.Cursor",
    *,
    prefix: str = "",
    is_last: bool = True,
    depth: int = 0,
    max_depth: int | None = None,
    main_file_only: bool = False,
    show_type: bool = False,
    show_canonical: bool = False,
    show_usr: bool = False,
    include_pp: bool = False,
) -> str:
    result = ""

    if max_depth is not None and depth > max_depth:
        return result

    # Optionally filter to main file
    if main_file_only and cur.kind != cindex.CursorKind.TRANSLATION_UNIT:
        if not in_main_file_only(tu, cur):
            return result

    # Optionally hide preprocessing nodes unless requested
    if not include_pp and cur.kind in (
        cindex.CursorKind.MACRO_DEFINITION,
        cindex.CursorKind.MACRO_INSTANTIATION,
        cindex.CursorKind.INCLUSION_DIRECTIVE,
    ):
        return result

    connector = "└── " if is_last else "├── "
    result += (
        f"{prefix}{connector}{describe_node(cur, show_type, show_canonical, show_usr)}\n"
    )

    # Prepare next prefix for children
    child_prefix = f"{prefix}    " if is_last else f"{prefix}│   "

    children = iter_children(cur)
    if max_depth is not None and depth == max_depth:
        return result

    for i, child in enumerate(children):
        last = i == len(children) - 1
        result += print_ast_tree(
            tu,
            child,
            prefix=child_prefix,
            is_last=last,
            depth=depth + 1,
            max_depth=max_depth,
            main_file_only=main_file_only,
            show_type=show_type,
            show_canonical=show_canonical,
            show_usr=show_usr,
            include_pp=include_pp,
        )
    return result


# ============================================================================
# Declaration Extraction Prototypes
# ============================================================================

class StructDecl:
    def __init__(self, name: str, location: str, fields: list):
        self.name = name
        self.location = location
        self.fields = fields  # List of (field_name, field_type) tuples
    
    def __str__(self):
        fields_str = ", ".join([f"{name}: {type_}" for name, type_ in self.fields])
        return f"struct {self.name} {{ {fields_str} }} @ {self.location}"


class VarDecl:
    def __init__(self, name: str, type_name: str, location: str, initializer: Optional[str] = None):
        self.name = name
        self.type_name = type_name
        self.location = location
        self.initializer = initializer
    
    def __str__(self):
        init_str = f" = {self.initializer}" if self.initializer else ""
        return f"{self.type_name} {self.name}{init_str} @ {self.location}"


class FuncDecl:
    def __init__(self, name: str, return_type: str, location: str, parameters: list):
        self.name = name
        self.return_type = return_type
        self.location = location
        self.parameters = parameters  # List of (param_name, param_type) tuples
    
    def __str__(self):
        params_str = ", ".join([f"{type_} {name}" for name, type_ in self.parameters])
        return f"{self.return_type} {self.name}({params_str}) @ {self.location}"


def extract_struct_fields(struct_cursor: "cindex.Cursor") -> list:
    """Extract field declarations from a struct cursor."""
    fields = []
    for child in struct_cursor.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field_name = child.spelling or "<anon>"
            field_type = child.type.spelling
            fields.append((field_name, field_type))
    return fields


def extract_function_parameters(func_cursor: "cindex.Cursor") -> list:
    """Extract parameter declarations from a function cursor."""
    parameters = []
    for child in func_cursor.get_children():
        if child.kind == cindex.CursorKind.PARM_DECL:
            param_name = child.spelling or "<anon>"
            param_type = child.type.spelling
            parameters.append((param_name, param_type))
    return parameters


def get_initializer_text(var_cursor: "cindex.Cursor") -> Optional[str]:
    """Extract initializer expression text from variable declaration."""
    # This is a simplified approach - for more complex expressions,
    # you might want to traverse the AST and reconstruct the expression
    for child in var_cursor.get_children():
        if child.kind in (cindex.CursorKind.INTEGER_LITERAL, 
                         cindex.CursorKind.BINARY_OPERATOR,
                         cindex.CursorKind.CALL_EXPR):
            # For now, just return a placeholder - you can enhance this
            # to traverse the expression tree and reconstruct the original text
            return "<expression>"
    return None


def extract_declarations(tu: "cindex.TranslationUnit", main_file_only: bool = True) -> dict:
    """
    Extract struct, variable, and function declarations from the translation unit.
    
    Returns:
        dict: {
            'structs': [StructDecl, ...],
            'variables': [VarDecl, ...], 
            'functions': [FuncDecl, ...]
        }
    """
    structs = []
    variables = []
    functions = []
    
    def traverse(cursor):
        # Filter to main file if requested
        if main_file_only and cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
            if not in_main_file_only(tu, cursor):
                return
        
        if cursor.kind == cindex.CursorKind.STRUCT_DECL:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            fields = extract_struct_fields(cursor)
            structs.append(StructDecl(name, location, fields))
            
        elif cursor.kind == cindex.CursorKind.VAR_DECL:
            name = cursor.spelling or "<anon>"
            type_name = cursor.type.spelling
            location = format_loc(cursor)
            initializer = get_initializer_text(cursor)
            variables.append(VarDecl(name, type_name, location, initializer))
            
        elif cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            name = cursor.spelling or "<anon>"
            return_type = cursor.result_type.spelling
            location = format_loc(cursor)
            parameters = extract_function_parameters(cursor)
            functions.append(FuncDecl(name, return_type, location, parameters))
        
        # Recursively traverse children
        for child in cursor.get_children():
            traverse(child)
    
    traverse(tu.cursor)
    
    return {
        'structs': structs,
        'variables': variables,
        'functions': functions
    }


def print_extracted_declarations(declarations: dict):
    """Pretty print extracted declarations."""
    print("=== STRUCT DECLARATIONS ===")
    for struct in declarations['structs']:
        print(struct)
    
    print("\n=== VARIABLE DECLARATIONS ===")
    for var in declarations['variables']:
        print(var)
    
    print("\n=== FUNCTION DECLARATIONS ===")
    for func in declarations['functions']:
        print(func)
