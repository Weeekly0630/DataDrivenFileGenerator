import sys
import os
from typing import Optional
from datetime import datetime

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
    def __init__(self, name: str, location: str, fields: list, comment: Optional[str] = None):
        self.name = name
        self.location = location
        self.fields = fields  # List of (field_name, field_type, field_comment) tuples
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        fields_str = ", ".join([f"{name}: {type_}" for name, type_, _ in self.fields])
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"struct {self.name}{comment_str} {{ {fields_str} }} @ {self.location}"


class VarDecl:
    def __init__(self, name: str, type_name: str, location: str, initializer: Optional[str] = None, comment: Optional[str] = None):
        self.name = name
        self.type_name = type_name
        self.location = location
        self.initializer = initializer
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        init_str = f" = {self.initializer}" if self.initializer else ""
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"{self.type_name} {self.name}{init_str}{comment_str} @ {self.location}"


class FuncDecl:
    def __init__(self, name: str, return_type: str, location: str, parameters: list, comment: Optional[str] = None):
        self.name = name
        self.return_type = return_type
        self.location = location
        self.parameters = parameters  # List of (param_name, param_type) tuples
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        params_str = ", ".join([f"{type_} {name}" for name, type_ in self.parameters])
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"{self.return_type} {self.name}({params_str}){comment_str} @ {self.location}"


class EnumDecl:
    def __init__(self, name: str, location: str, enumerators: list, comment: Optional[str] = None):
        self.name = name
        self.location = location
        self.enumerators = enumerators  # List of (enum_name, enum_value) tuples
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        enums_str = ", ".join([f"{name}={value}" if value else name for name, value in self.enumerators])
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"enum {self.name}{comment_str} {{ {enums_str} }} @ {self.location}"


class UnionDecl:
    def __init__(self, name: str, location: str, fields: list, comment: Optional[str] = None):
        self.name = name
        self.location = location
        self.fields = fields  # List of (field_name, field_type) tuples
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        fields_str = ", ".join([f"{name}: {type_}" for name, type_ in self.fields])
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"union {self.name}{comment_str} {{ {fields_str} }} @ {self.location}"


class TypedefDecl:
    def __init__(self, name: str, location: str, underlying_type: str, comment: Optional[str] = None):
        self.name = name
        self.location = location
        self.underlying_type = underlying_type
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"typedef {self.underlying_type} {self.name}{comment_str} @ {self.location}"


class MacroDecl:
    def __init__(self, name: str, location: str, definition: str, comment: Optional[str] = None):
        self.name = name
        self.location = location
        self.definition = definition
        self.comment = comment
        self.doxygen = parse_doxygen_comment(comment) if comment else DoxygenComment()
    
    def __str__(self):
        comment_str = f" /* {self.doxygen.brief or self.comment} */" if (self.doxygen.brief or self.comment) else ""
        return f"#define {self.name} {self.definition}{comment_str} @ {self.location}"


class CommentDecl:
    def __init__(self, text: str, location: str, kind: str):
        self.text = text
        self.location = location
        self.kind = kind  # "COMMENT" or other comment-related kinds
    
    def __str__(self):
        # Clean up the comment text for display
        clean_text = self.text.strip().replace('\n', ' ').replace('\r', '')
        if len(clean_text) > 80:
            clean_text = clean_text[:77] + "..."
        return f"/* {clean_text} */ @ {self.location}"


def extract_struct_fields(struct_cursor: "cindex.Cursor") -> list:
    """Extract field declarations from a struct cursor."""
    fields = []
    for child in struct_cursor.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field_name = child.spelling or "<anon>"
            field_type = child.type.spelling
            field_comment = get_comment_text(child)
            fields.append((field_name, field_type, field_comment))
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


def extract_enum_constants(enum_cursor: "cindex.Cursor") -> list:
    """Extract enum constant declarations from an enum cursor."""
    enumerators = []
    for child in enum_cursor.get_children():
        if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            enum_name = child.spelling or "<anon>"
            # Try to get the enum value
            enum_value = None
            try:
                enum_value = str(child.enum_value)
            except:
                enum_value = None
            enumerators.append((enum_name, enum_value))
    return enumerators


def extract_union_fields(union_cursor: "cindex.Cursor") -> list:
    """Extract field declarations from a union cursor."""
    fields = []
    for child in union_cursor.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field_name = child.spelling or "<anon>"
            field_type = child.type.spelling
            fields.append((field_name, field_type))
    return fields


def clean_comment_text(comment: Optional[str]) -> Optional[str]:
    """Clean up comment text for better readability."""
    if not comment:
        return None
    
    # Remove common comment markers and clean up whitespace
    lines = comment.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()
        # Remove common comment prefixes
        if line.startswith('/**'):
            line = line[3:].strip()
        elif line.startswith('/*'):
            line = line[2:].strip()
        elif line.startswith('*'):
            line = line[1:].strip()
        elif line.startswith('//'):
            line = line[2:].strip()
        
        # Remove trailing comment markers
        if line.endswith('*/'):
            line = line[:-2].strip()
            
        if line and line not in ['*', '/**', '*/', '//', '']:
            cleaned_lines.append(line)
    
    result = ' '.join(cleaned_lines).strip()
    return result if result else None


class DoxygenComment:
    """Structured representation of a Doxygen comment."""
    def __init__(self):
        self.brief: Optional[str] = None
        self.detailed: Optional[str] = None
        self.params: list = []  # List of (param_name, param_description) tuples
        self.returns: Optional[str] = None
        self.throws: list = []  # List of (exception_type, description) tuples
        self.since: Optional[str] = None
        self.deprecated: Optional[str] = None
        self.author: Optional[str] = None
        self.version: Optional[str] = None
        self.date: Optional[str] = None
        self.note: Optional[str] = None
        self.warning: Optional[str] = None
        self.see_also: list = []  # List of references
        self.example: Optional[str] = None
        self.todo: list = []  # List of TODO items
        self.bug: list = []  # List of bug descriptions
        self.raw_text: str = ""
        
    def __str__(self) -> str:
        """Generate a formatted string representation."""
        parts = []
        if self.brief:
            parts.append(f"Brief: {self.brief}")
        if self.detailed:
            parts.append(f"Detailed: {self.detailed}")
        if self.params:
            params_str = ", ".join([f"{name}: {desc}" for name, desc in self.params])
            parts.append(f"Parameters: {params_str}")
        if self.returns:
            parts.append(f"Returns: {self.returns}")
        if self.deprecated:
            parts.append(f"Deprecated: {self.deprecated}")
        if self.since:
            parts.append(f"Since: {self.since}")
        return " | ".join(parts) if parts else self.raw_text
    
    def get_summary(self) -> str:
        """Get a concise summary of the comment."""
        return self.brief or self.detailed or self.raw_text
    
    def has_content(self) -> bool:
        """Check if the comment has any meaningful content."""
        return bool(self.brief or self.detailed or self.params or self.returns or 
                   self.deprecated or self.note or self.warning or self.example)
    
    def to_markdown(self) -> str:
        """Convert the Doxygen comment to Markdown format."""
        md_parts = []
        
        if self.brief:
            md_parts.append(self.brief)
        
        if self.detailed and self.detailed != self.brief:
            md_parts.append(f"\n{self.detailed}")
        
        if self.params:
            md_parts.append("\n**Parameters:**")
            for param_name, param_desc in self.params:
                md_parts.append(f"- `{param_name}`: {param_desc}")
        
        if self.returns:
            md_parts.append(f"\n**Returns:** {self.returns}")
        
        if self.throws:
            md_parts.append("\n**Throws:**")
            for exc_type, exc_desc in self.throws:
                md_parts.append(f"- `{exc_type}`: {exc_desc}")
        
        if self.deprecated:
            md_parts.append(f"\n> **Deprecated:** {self.deprecated}")
        
        if self.note:
            md_parts.append(f"\n> **Note:** {self.note}")
        
        if self.warning:
            md_parts.append(f"\n> **Warning:** {self.warning}")
        
        if self.example:
            md_parts.append(f"\n**Example:**\n```c\n{self.example}\n```")
        
        if self.see_also:
            md_parts.append("\n**See also:** " + ", ".join(self.see_also))
        
        if self.todo:
            md_parts.append("\n**TODO:**")
            for todo_item in self.todo:
                md_parts.append(f"- {todo_item}")
        
        return "".join(md_parts) if md_parts else self.raw_text


def parse_doxygen_comment(comment: Optional[str]) -> DoxygenComment:
    """
    Parse a Doxygen-style comment and extract structured information.
    
    Supports common Doxygen tags:
    - @brief, @param, @return/@returns, @throw/@throws
    - @since, @deprecated, @author, @version, @date
    - @note, @warning, @see, @example, @todo, @bug
    """
    result = DoxygenComment()
    
    if not comment:
        return result
        
    # Clean the comment first
    cleaned = clean_comment_text(comment)
    if not cleaned:
        return result
        
    result.raw_text = cleaned
    
    # Split into lines for processing, preserving line breaks within content
    lines = cleaned.split('\n') if '\n' in cleaned else [cleaned]
    
    current_tag = None
    current_content = []
    
    def save_current_tag():
        """Save the current tag and its content."""
        if current_tag and current_content:
            content = ' '.join(current_content).strip()
            
            if current_tag == 'brief':
                result.brief = content
            elif current_tag == 'detailed':
                result.detailed = content
            elif current_tag.startswith('param'):
                # Handle @param[in], @param[out], @param[in,out] variants
                if '[' in current_tag:
                    # Extract direction from @param[in] or @param[out]
                    direction_match = current_tag.split('[', 1)
                    if len(direction_match) > 1 and ']' in direction_match[1]:
                        direction = direction_match[1].split(']')[0]
                        content = f"[{direction}] {content}"
                
                # Extract parameter name from @param name description
                parts = content.split(None, 1)
                param_name = parts[0] if parts else ""
                param_desc = parts[1] if len(parts) > 1 else ""
                result.params.append((param_name, param_desc))
            elif current_tag in ['return', 'returns', 'retval']:
                result.returns = content
            elif current_tag in ['throw', 'throws', 'exception']:
                # Extract exception type from @throw ExceptionType description
                parts = content.split(None, 1)
                exception_type = parts[0] if parts else ""
                exception_desc = parts[1] if len(parts) > 1 else ""
                result.throws.append((exception_type, exception_desc))
            elif current_tag == 'since':
                result.since = content
            elif current_tag in ['deprecated', 'obsolete']:
                result.deprecated = content
            elif current_tag == 'author':
                result.author = content
            elif current_tag == 'version':
                result.version = content
            elif current_tag == 'date':
                result.date = content
            elif current_tag in ['note', 'remark']:
                result.note = content
            elif current_tag in ['warning', 'attention']:
                result.warning = content
            elif current_tag in ['see', 'sa', 'seealso']:
                result.see_also.append(content)
            elif current_tag in ['example', 'code']:
                result.example = content
            elif current_tag == 'todo':
                result.todo.append(content)
            elif current_tag == 'bug':
                result.bug.append(content)
    
    # Process each line
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line can separate different sections, but continue processing
            if current_tag and current_content:
                current_content.append("")  # Preserve paragraph breaks
            continue
            
        # Check if this line starts with a Doxygen tag
        if line.startswith('@') or line.startswith('\\'):
            # Save previous tag
            save_current_tag()
            
            # Parse new tag - handle complex tags like @param[in]
            tag_part = line[1:]  # Remove @ or \
            
            # Handle tags with brackets like @param[in] name description
            import re
            tag_match = re.match(r'^(\w+(?:\[[^\]]*\])?)\s*(.*)', tag_part)
            
            if tag_match:
                current_tag = tag_match.group(1).lower()
                remaining_content = tag_match.group(2).strip()
                current_content = [remaining_content] if remaining_content else []
            else:
                # Fallback to simple split for malformed tags
                tag_split = tag_part.split(None, 1)
                if tag_split:
                    current_tag = tag_split[0].lower()
                    current_content = [tag_split[1]] if len(tag_split) > 1 else []
                else:
                    current_tag = None
                    current_content = []
        else:
            # This is continuation of current tag or detailed description
            if current_tag:
                # Remove empty strings that were added as paragraph separators
                if current_content and current_content[-1] == "" and line:
                    current_content[-1] = line
                else:
                    current_content.append(line)
            else:
                # No tag yet, this is detailed description
                if not result.detailed:
                    current_tag = 'detailed'
                    current_content = [line]
                else:
                    # Already have detailed, append to it
                    current_content.append(line)
    
    # Save the last tag
    save_current_tag()
    
    # If we only have detailed content and no brief, try to extract brief from first sentence
    if result.detailed and not result.brief:
        detailed_text = result.detailed
        # Look for first sentence (ending with . ! or ?)
        import re
        first_sentence = re.split(r'[.!?]\s+', detailed_text, 1)
        if len(first_sentence) > 1:
            result.brief = first_sentence[0].strip()
            # Remove the brief part from detailed and clean up
            remaining = detailed_text[len(first_sentence[0]):].strip(' .!?')
            result.detailed = remaining if remaining else None
        else:
            # No sentence break found, use first part as brief if it's short
            if len(detailed_text) <= 100:
                result.brief = detailed_text
                result.detailed = None
    
    # Clean up empty content
    if result.brief == "":
        result.brief = None
    if result.detailed == "":
        result.detailed = None
    
    return result


def parse_doxygen_comment_simple(comment: Optional[str]) -> str:
    """
    Simple Doxygen comment parser that returns a clean, readable description.
    Useful when you just want the main description without full parsing.
    """
    if not comment:
        return ""
        
    doxy = parse_doxygen_comment(comment)
    
    # Build a simple description
    parts = []
    if doxy.brief:
        parts.append(doxy.brief)
    if doxy.detailed and doxy.detailed != doxy.brief:
        parts.append(doxy.detailed)
    
    # Add deprecation warning if present
    if doxy.deprecated:
        parts.append(f"[DEPRECATED: {doxy.deprecated}]")
    
    return " ".join(parts) if parts else doxy.raw_text


def get_macro_definition(macro_cursor: "cindex.Cursor") -> str:
    """Extract macro definition text."""
    # This is a simplified approach - you might want to use 
    # the preprocessing record for more accurate macro expansion
    try:
        # Get the macro tokens if available
        tokens = list(macro_cursor.get_tokens())
        if len(tokens) > 1:
            # Skip the macro name token, join the rest
            definition_tokens = tokens[1:]
            return " ".join([token.spelling for token in definition_tokens])
        return ""
    except:
        return ""


def get_preceding_comment_for_macro_simple(tu: "cindex.TranslationUnit", macro_cursor: "cindex.Cursor") -> Optional[str]:
    """
    Simple approach: read the source file and look for comments before the macro line.
    """
    try:
        loc = macro_cursor.location
        if not loc or not loc.file:
            return None
            
        # Read the source file
        file_path = str(loc.file)
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        macro_line = loc.line - 1  # Convert to 0-based indexing
        if macro_line < 0 or macro_line >= len(lines):
            return None
            
        # Look backwards from the macro line for comments
        comment_lines = []
        for i in range(macro_line - 1, -1, -1):
            line = lines[i].strip()
            
            # If it's a comment line
            if line.startswith('/*') or line.startswith('//') or line.startswith('*'):
                comment_lines.insert(0, line)
            elif line == '':
                # Empty line, continue looking
                continue
            else:
                # Non-comment, non-empty line, stop
                break
                
        if comment_lines:
            # Join all comment lines and clean them up
            full_comment = '\n'.join(comment_lines)
            return clean_comment_text(full_comment)
            
    except Exception:
        pass
        
    return None


def get_preceding_comment_for_macro(tu: "cindex.TranslationUnit", macro_cursor: "cindex.Cursor") -> Optional[str]:
    """
    Extract comment that appears immediately before a macro definition.
    This requires parsing the source file and looking for comments preceding the macro location.
    """
    # Try the simple file-reading approach first
    simple_comment = get_preceding_comment_for_macro_simple(tu, macro_cursor)
    if simple_comment:
        return simple_comment
        
    # Fall back to token-based approach
    try:
        # Get the macro location
        loc = macro_cursor.location
        if not loc or not loc.file:
            return None
            
        # Get all tokens from the translation unit using the cursor's extent
        if tu.cursor and tu.cursor.extent:
            tokens = list(tu.get_tokens(extent=tu.cursor.extent))
        else:
            return None
        
        # Find the macro token
        macro_token_index = None
        for i, token in enumerate(tokens):
            if (token.kind == cindex.TokenKind.IDENTIFIER and 
                token.spelling == macro_cursor.spelling and
                token.location.line == loc.line and
                token.location.column == loc.column):
                macro_token_index = i
                break
        
        if macro_token_index is None:
            return None
            
        # Look backwards for comments before this macro
        comment_parts = []
        for i in range(macro_token_index - 1, -1, -1):
            token = tokens[i]
            
            # If we hit a non-comment, non-whitespace token that's not on adjacent lines, stop
            if token.kind == cindex.TokenKind.COMMENT:
                # Check if this comment is close to our macro (within a few lines)
                line_diff = loc.line - token.location.line
                if line_diff <= 3:  # Allow up to 3 lines between comment and macro
                    comment_parts.insert(0, token.spelling)
                else:
                    break
            elif token.kind not in (cindex.TokenKind.COMMENT, cindex.TokenKind.LITERAL):
                # If we encounter other tokens that are far from the macro, stop
                line_diff = loc.line - token.location.line
                if line_diff > 1:
                    break
                    
        if comment_parts:
            # Join all comment parts and clean them up
            full_comment = " ".join(comment_parts)
            return clean_comment_text(full_comment)
            
    except Exception as e:
        # If anything goes wrong, just return None
        pass
        
    return None


def get_comment_text(cursor: "cindex.Cursor") -> Optional[str]:
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
    return None


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
    Extract struct, variable, function, enum, union, typedef, and macro declarations from the translation unit.
    
    Returns:
        dict: {
            'structs': [StructDecl, ...],
            'variables': [VarDecl, ...], 
            'functions': [FuncDecl, ...],
            'enums': [EnumDecl, ...],
            'unions': [UnionDecl, ...],
            'typedefs': [TypedefDecl, ...],
            'macros': [MacroDecl, ...]
        }
    """
    structs = []
    variables = []
    functions = []
    enums = []
    unions = []
    typedefs = []
    macros = []
    
    def traverse(cursor):
        # Filter to main file if requested
        if main_file_only and cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
            if not in_main_file_only(tu, cursor):
                return
        
        # Get comment for the current cursor
        comment = clean_comment_text(get_comment_text(cursor))
        
        if cursor.kind == cindex.CursorKind.STRUCT_DECL:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            fields = extract_struct_fields(cursor)
            structs.append(StructDecl(name, location, fields, comment))
            
        elif cursor.kind == cindex.CursorKind.VAR_DECL:
            name = cursor.spelling or "<anon>"
            type_name = cursor.type.spelling
            location = format_loc(cursor)
            initializer = get_initializer_text(cursor)
            variables.append(VarDecl(name, type_name, location, initializer, comment))
            
        elif cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            name = cursor.spelling or "<anon>"
            return_type = cursor.result_type.spelling
            location = format_loc(cursor)
            parameters = extract_function_parameters(cursor)
            functions.append(FuncDecl(name, return_type, location, parameters, comment))
            
        elif cursor.kind == cindex.CursorKind.ENUM_DECL:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            enumerators = extract_enum_constants(cursor)
            enums.append(EnumDecl(name, location, enumerators, comment))
            
        elif cursor.kind == cindex.CursorKind.UNION_DECL:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            fields = extract_union_fields(cursor)
            unions.append(UnionDecl(name, location, fields, comment))
            
        elif cursor.kind == cindex.CursorKind.TYPEDEF_DECL:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            underlying_type = cursor.underlying_typedef_type.spelling
            typedefs.append(TypedefDecl(name, location, underlying_type, comment))
            
        elif cursor.kind == cindex.CursorKind.MACRO_DEFINITION:
            name = cursor.spelling or "<anon>"
            location = format_loc(cursor)
            definition = get_macro_definition(cursor)
            # Try to get comment from cursor first, then try preceding comment extraction
            comment = clean_comment_text(get_comment_text(cursor))
            if not comment:
                comment = get_preceding_comment_for_macro(tu, cursor)
            macros.append(MacroDecl(name, location, definition, comment))
        
        # Recursively traverse children
        for child in cursor.get_children():
            traverse(child)
    
    traverse(tu.cursor)
    
    return {
        'structs': structs,
        'variables': variables,
        'functions': functions,
        'enums': enums,
        'unions': unions,
        'typedefs': typedefs,
        'macros': macros
    }


def print_extracted_declarations(declarations: dict):
    """Pretty print extracted declarations."""
    print("=== STRUCT DECLARATIONS ===")
    for struct in declarations['structs']:
        print(struct)
    
    print("\n=== UNION DECLARATIONS ===")
    for union in declarations['unions']:
        print(union)
    
    print("\n=== ENUM DECLARATIONS ===")
    for enum in declarations['enums']:
        print(enum)
    
    print("\n=== TYPEDEF DECLARATIONS ===")
    for typedef in declarations['typedefs']:
        print(typedef)
    
    print("\n=== VARIABLE DECLARATIONS ===")
    for var in declarations['variables']:
        print(var)
    
    print("\n=== FUNCTION DECLARATIONS ===")
    for func in declarations['functions']:
        print(func)
    
    print("\n=== MACRO DEFINITIONS ===")
    for macro in declarations['macros']:
        print(macro)


def generate_markdown_report(declarations: dict, source_file: str = "") -> str:
    """Generate a Markdown report of all declarations."""
    md_content = []
    
    # Header
    md_content.append("# C/C++ Code Analysis Report")
    if source_file:
        md_content.append(f"\n**Source File:** `{source_file}`")
    md_content.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append("\n---\n")
    
    # Table of Contents
    md_content.append("## Table of Contents")
    md_content.append("- [Structs](#structs)")
    md_content.append("- [Unions](#unions)")
    md_content.append("- [Enums](#enums)")
    md_content.append("- [Typedefs](#typedefs)")
    md_content.append("- [Variables](#variables)")
    md_content.append("- [Functions](#functions)")
    md_content.append("- [Macros](#macros)")
    md_content.append("\n---\n")
    
    # Structs
    md_content.append("## Structs")
    if declarations['structs']:
        for struct in declarations['structs']:
            md_content.append(f"\n### `{struct.name}`")
            
            # Use Doxygen markdown formatting if available
            if struct.doxygen.has_content():
                md_content.append(f"\n{struct.doxygen.to_markdown()}")
            elif struct.comment:
                md_content.append(f"\n**Description:** {struct.comment}")
            
            md_content.append(f"\n**Location:** `{struct.location}`")
            
            if struct.fields:
                md_content.append("\n**Fields:**")
                md_content.append("| Field Name | Type | Comment |")
                md_content.append("|------------|------|---------|")
                for field_name, field_type, field_comment in struct.fields:
                    comment_cell = field_comment if field_comment else "-"
                    md_content.append(f"| `{field_name}` | `{field_type}` | {comment_cell} |")
            md_content.append("")
    else:
        md_content.append("\n*No struct declarations found.*\n")
    
    # Unions
    md_content.append("## Unions")
    if declarations['unions']:
        for union in declarations['unions']:
            md_content.append(f"\n### `{union.name}`")
            if union.comment:
                md_content.append(f"\n**Description:** {union.comment}")
            md_content.append(f"\n**Location:** `{union.location}`")
            
            if union.fields:
                md_content.append("\n**Fields:**")
                md_content.append("| Field Name | Type |")
                md_content.append("|------------|------|")
                for field_name, field_type in union.fields:
                    md_content.append(f"| `{field_name}` | `{field_type}` |")
            md_content.append("")
    else:
        md_content.append("\n*No union declarations found.*\n")
    
    # Enums
    md_content.append("## Enums")
    if declarations['enums']:
        for enum in declarations['enums']:
            md_content.append(f"\n### `{enum.name}`")
            if enum.comment:
                md_content.append(f"\n**Description:** {enum.comment}")
            md_content.append(f"\n**Location:** `{enum.location}`")
            
            if enum.enumerators:
                md_content.append("\n**Enumerators:**")
                md_content.append("| Name | Value |")
                md_content.append("|------|-------|")
                for enum_name, enum_value in enum.enumerators:
                    value_cell = enum_value if enum_value is not None else "auto"
                    md_content.append(f"| `{enum_name}` | `{value_cell}` |")
            md_content.append("")
    else:
        md_content.append("\n*No enum declarations found.*\n")
    
    # Typedefs
    md_content.append("## Typedefs")
    if declarations['typedefs']:
        md_content.append("| Name | Underlying Type | Comment | Location |")
        md_content.append("|------|-----------------|---------|----------|")
        for typedef in declarations['typedefs']:
            comment_cell = typedef.comment if typedef.comment else "-"
            md_content.append(f"| `{typedef.name}` | `{typedef.underlying_type}` | {comment_cell} | `{typedef.location}` |")
        md_content.append("")
    else:
        md_content.append("\n*No typedef declarations found.*\n")
    
    # Variables
    md_content.append("## Variables")
    if declarations['variables']:
        md_content.append("| Name | Type | Initializer | Comment | Location |")
        md_content.append("|------|------|-------------|---------|----------|")
        for var in declarations['variables']:
            init_cell = var.initializer if var.initializer else "-"
            comment_cell = var.comment if var.comment else "-"
            md_content.append(f"| `{var.name}` | `{var.type_name}` | `{init_cell}` | {comment_cell} | `{var.location}` |")
        md_content.append("")
    else:
        md_content.append("\n*No variable declarations found.*\n")
    
    # Functions
    md_content.append("## Functions")
    if declarations['functions']:
        for func in declarations['functions']:
            md_content.append(f"\n### `{func.name}`")
            
            # Use Doxygen markdown formatting if available
            if func.doxygen.has_content():
                md_content.append(f"\n{func.doxygen.to_markdown()}")
            elif func.comment:
                md_content.append(f"\n**Description:** {func.comment}")
            
            md_content.append(f"\n**Return Type:** `{func.return_type}`")
            md_content.append(f"\n**Location:** `{func.location}`")
            
            if func.parameters:
                md_content.append("\n**Parameters:**")
                md_content.append("| Name | Type |")
                md_content.append("|------|------|")
                for param_name, param_type in func.parameters:
                    md_content.append(f"| `{param_name}` | `{param_type}` |")
            else:
                md_content.append("\n**Parameters:** None")
            md_content.append("")
    else:
        md_content.append("\n*No function declarations found.*\n")
    
    # Macros (only show main file macros to avoid clutter)
    md_content.append("## Macros")
    main_file_macros = [m for m in declarations['macros'] if m.location and not m.location.startswith("")]
    if main_file_macros:
        md_content.append("| Name | Definition | Location |")
        md_content.append("|------|------------|----------|")
        for macro in main_file_macros:
            definition = macro.definition if macro.definition else ""
            # Escape markdown special characters in definition
            definition = definition.replace("|", "\\|").replace("\n", " ")
            if len(definition) > 50:
                definition = definition[:47] + "..."
            md_content.append(f"| `{macro.name}` | `{definition}` | `{macro.location}` |")
        md_content.append("")
    else:
        md_content.append("\n*No macro definitions found in main file.*\n")
    
    return "\n".join(md_content)
