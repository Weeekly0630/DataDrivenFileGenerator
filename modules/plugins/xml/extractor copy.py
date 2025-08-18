import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# 基础节点类型定义
@dataclass
class XmlVar:
    """Variable node - 变量节点"""
    name: str
    value: Optional[str] = None
    type_name: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass 
class XmlCtr:
    """Container node - 容器节点"""
    name: str
    children: List[Any] = field(default_factory=list)  # Can contain var, ctr, lst, chc, ref
    attributes: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class XmlLst:
    """List node - 列表节点"""
    name: str
    items: List[Any] = field(default_factory=list)
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class XmlChc:
    """Choice node - 选择节点"""
    name: str
    options: List[Any] = field(default_factory=list)
    default_option: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class XmlRef:
    """Reference node - 引用节点"""
    name: str
    target: str
    ref_type: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

# 节点类型映射
NODE_TYPES = {
    'var': XmlVar,
    'ctr': XmlCtr, 
    'lst': XmlLst,
    'chc': XmlChc,
    'ref': XmlRef
}

def get_namespace_and_tag(elem: ET.Element) -> tuple[str, str]:
    """Extract namespace and tag from element"""
    if "}" in elem.tag:
        ns, tag = elem.tag[1:].split("}", 1)
        return ns, tag
    return "", elem.tag

def parse_structured_xml(elem: ET.Element) -> Any:
    """Parse ET.Element into structured node objects (var, ctr, lst, chc, ref)"""
    namespace, tag = get_namespace_and_tag(elem)
    name = elem.get('name', tag)  # Use 'name' attribute or tag as name
    attributes = dict(elem.attrib)
    description = elem.get('desc') or elem.get('description')
    
    # Determine node type based on tag or explicit type attribute
    node_type = elem.get('type', tag.lower())
    
    if node_type == 'var' or tag.lower() == 'var':
        return XmlVar(
            name=name,
            value=elem.text.strip() if elem.text else elem.get('value'),
            type_name=elem.get('type') or elem.get('datatype'),
            attributes=attributes,
            description=description
        )
    
    elif node_type == 'ctr' or tag.lower() == 'ctr' or tag.lower() == 'container':
        children = [parse_structured_xml(child) for child in elem]
        return XmlCtr(
            name=name,
            children=children,
            attributes=attributes,
            description=description
        )
    
    elif node_type == 'lst' or tag.lower() == 'lst' or tag.lower() == 'list':
        items = [parse_structured_xml(child) for child in elem]
        min_val = elem.get('min')
        max_val = elem.get('max')
        return XmlLst(
            name=name,
            items=items,
            min_items=int(min_val) if min_val else None,
            max_items=int(max_val) if max_val else None,
            attributes=attributes,
            description=description
        )
    
    elif node_type == 'chc' or tag.lower() == 'chc' or tag.lower() == 'choice':
        options = [parse_structured_xml(child) for child in elem]
        return XmlChc(
            name=name,
            options=options,
            default_option=elem.get('default'),
            attributes=attributes,
            description=description
        )
    
    elif node_type == 'ref' or tag.lower() == 'ref' or tag.lower() == 'reference':
        return XmlRef(
            name=name,
            target=elem.get('target') or elem.get('ref') or elem.text.strip() if elem.text else "",
            ref_type=elem.get('reftype') or elem.get('ref-type'),
            attributes=attributes,
            description=description
        )
    
    else:
        # 默认作为容器处理
        children = [parse_structured_xml(child) for child in elem]
        return XmlCtr(
            name=name,
            children=children,
            attributes=attributes,
            description=description
        )

def print_structured_tree(node: Any, depth: int = 0, is_last: bool = True, prefix: str = ""):
    """Print structured node tree"""
    connector = "└── " if is_last else "├── "
    
    if isinstance(node, XmlVar):
        info = f"VAR {node.name}"
        if node.value:
            info += f" = {node.value}"
        if node.type_name:
            info += f" ({node.type_name})"
    elif isinstance(node, XmlCtr):
        info = f"CTR {node.name} [{len(node.children)} children]"
    elif isinstance(node, XmlLst):
        info = f"LST {node.name} [{len(node.items)} items]"
        if node.min_items is not None or node.max_items is not None:
            info += f" (min:{node.min_items}, max:{node.max_items})"
    elif isinstance(node, XmlChc):
        info = f"CHC {node.name} [{len(node.options)} options]"
        if node.default_option:
            info += f" (default:{node.default_option})"
    elif isinstance(node, XmlRef):
        info = f"REF {node.name} -> {node.target}"
        if node.ref_type:
            info += f" ({node.ref_type})"
    else:
        info = f"UNK {type(node).__name__}"
    
    if hasattr(node, 'description') and node.description:
        info += f" | {node.description}"
    
    print(f"{prefix}{connector}{info}")
    
    # Print children/items/options
    child_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
    children = []
    
    if isinstance(node, XmlCtr):
        children = node.children
    elif isinstance(node, XmlLst):
        children = node.items
    elif isinstance(node, XmlChc):
        children = node.options
    
    for i, child in enumerate(children):
        print_structured_tree(child, depth + 1, i == len(children) - 1, child_prefix)

def print_xml_tree(elem: ET.Element, depth: int = 0, is_last: bool = True, prefix: str = ""):
    """Print XML tree structure using ET.Element directly"""
    connector = "└── " if is_last else "├── "
    namespace, tag = get_namespace_and_tag(elem)
    
    # Format information
    ns_info = f"[ns:{namespace}]" if namespace else ""
    attr_info = f"[attr:{dict(elem.attrib)}]" if elem.attrib else ""
    text_info = f"[text:{elem.text.strip()}]" if elem.text and elem.text.strip() else ""
    tail_info = f"[tail:{elem.tail.strip()}]" if elem.tail and elem.tail.strip() else ""
    
    # Print current node
    info_parts = [part for part in [ns_info, attr_info, text_info, tail_info] if part]
    info_str = " ".join(info_parts)
    print(f"{prefix}{connector}{tag} {info_str}")
    
    # Print children
    children = list(elem)
    child_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
    for i, child in enumerate(children):
        print_xml_tree(child, depth + 1, i == len(children) - 1, child_prefix)

def xml_tree_to_lines(elem: ET.Element, depth: int = 0, is_last: bool = True, prefix: str = "") -> List[str]:
    """Convert XML tree to list of strings using ET.Element directly"""
    connector = "└── " if is_last else "├── "
    namespace, tag = get_namespace_and_tag(elem)
    
    # Format information
    ns_info = f"[ns:{namespace}]" if namespace else ""
    attr_info = f"[attr:{dict(elem.attrib)}]" if elem.attrib else ""
    text_info = f"[text:{elem.text.strip()}]" if elem.text and elem.text.strip() else ""
    tail_info = f"[tail:{elem.tail.strip()}]" if elem.tail and elem.tail.strip() else ""
    
    # Create line
    info_parts = [part for part in [ns_info, attr_info, text_info, tail_info] if part]
    info_str = " ".join(info_parts)
    line = f"{prefix}{connector}{tag} {info_str}"
    lines = [line]
    
    # Process children
    children = list(elem)
    child_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
    for i, child in enumerate(children):
        lines.extend(xml_tree_to_lines(child, depth + 1, i == len(children) - 1, child_prefix))
    
    return lines

def save_xml_tree_to_file(elem: ET.Element, file_path: str):
    """Save XML tree structure to file using ET.Element directly"""
    lines = xml_tree_to_lines(elem)
    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def extract_xml_structure(xml_path: str) -> ET.Element:
    """Load XML file and return root element"""
    tree = ET.parse(xml_path)
    return tree.getroot()

# 示例用法
if __name__ == "__main__":
    xml_file = r"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\xml\Dio.xdm"
    output_file = r"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\xml\Dio_tree.txt"
    root_elem = extract_xml_structure(xml_file)
    print_xml_tree(root_elem)
    save_xml_tree_to_file(root_elem, output_file)
    print(f"XML tree structure saved to: {output_file}")
    
    # 直接使用 ET.Element 的示例
    print("\n--- Direct access to ET.Element properties ---")
    print(f"Root tag: {root_elem.tag}")
    print(f"Root attrib: {root_elem.attrib}")
    print(f"Root text: {repr(root_elem.text)}")
    print(f"Root tail: {repr(root_elem.tail)}")
    print(f"Children count: {len(root_elem)}")
    
    # 遍历所有子节点
    for i, child in enumerate(root_elem):
        print(f"Child {i}: tag={child.tag}, attrib={child.attrib}")