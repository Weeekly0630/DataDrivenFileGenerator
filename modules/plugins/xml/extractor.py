import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Protocol, Tuple
from dataclasses import dataclass, field
from enum import IntFlag
import sys
import os

# 自动添加项目根目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.plugins.type_classes.xdm import XmlNode


class ElementVisitorResult(IntFlag):
    CONTINUE = 0  # 继续遍历子节点
    SKIP_VISITOR = 1  # 跳过后续访问器
    SKIP_CHILDREN = 2  # 跳过子节点, 用于控制当前节点的子节点访问
    BREAK_CHILDREN = 4  # 跳过兄弟节点，用于返回给父节点，使其跳过兄弟节点


@dataclass
class ElementVisitorContext:
    depth: int  # 当前节点深度


class ElementVisitor(Protocol):
    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        """访问XML元素"""
        ...


class ElementVisitorChain:
    """访问者链，用于处理XML元素的不同类型"""

    def __init__(self, visitors: List[ElementVisitor]):
        self.visitors = visitors

    def traverse(self, elem: ET.Element) -> None:
        self._traverse(elem, ElementVisitorContext(depth=0))

    def _traverse(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        """遍历AST节点，按顺序调用每个访问器"""
        visit_result: ElementVisitorResult = ElementVisitorResult.CONTINUE

        for visitor in self.visitors:
            result = visitor.visit(elem, context)
            visit_result |= result
            if result & ElementVisitorResult.SKIP_VISITOR:
                break

        if visit_result & ElementVisitorResult.SKIP_CHILDREN:
            return visit_result

        children = list(elem)
        for i, child in enumerate(children):
            child_result = self._traverse(
                child,
                ElementVisitorContext(depth=context.depth + 1),
            )
            if child_result & ElementVisitorResult.BREAK_CHILDREN:
                break

        return visit_result


def get_namespace_and_tag(elem: ET.Element) -> tuple[str, str]:
    """Extract namespace and tag from element"""
    if "}" in elem.tag:
        ns, tag = elem.tag[1:].split("}", 1)
        return ns, tag
    return "", elem.tag


def format_element_info(elem: ET.Element) -> str:
    namespace, tag = get_namespace_and_tag(elem)

    # Format information
    tag_info = f"{tag}"
    ns_info = f"[ns:{namespace}]" if namespace else ""
    attr_info = f"[attr:{dict(elem.attrib)}]" if elem.attrib else ""
    text_info = f"[text:{elem.text.strip()}]" if elem.text and elem.text.strip() else ""
    tail_info = f"[tail:{elem.tail.strip()}]" if elem.tail and elem.tail.strip() else ""
    # Print current node
    info_parts = [
        part for part in [tag_info, ns_info, attr_info, text_info, tail_info] if part
    ]
    info_str = " ".join(info_parts)

    return info_str


class ElementFilterVisitor(ElementVisitor):
    """过滤XML元素的访问器, 提取出想要的节点"""

    def __init__(
        self,
        included_tags: Optional[List[str]] = None,
        excluded_tags: Optional[List[str]] = None,
    ) -> None:
        self.included_tags = included_tags if included_tags is not None else []
        self.excluded_tags = excluded_tags if excluded_tags is not None else []

    def _filter_by_tag(self, elem: ET.Element) -> bool:
        _, tag = get_namespace_and_tag(elem)
        if self.included_tags and tag not in self.included_tags:
            return False
        if self.excluded_tags and tag in self.excluded_tags:
            return False
        return True

    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        if not self._filter_by_tag(elem):
            return (
                ElementVisitorResult.SKIP_CHILDREN | ElementVisitorResult.SKIP_VISITOR
            )

        return ElementVisitorResult.CONTINUE


class ElementPrinterVisitor(ElementVisitor):
    """打印XML元素信息的访问器"""

    def __init__(self) -> None:
        self.nodes: List[Tuple[int, str]] = []

    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        """Print XML tree structure using ET.Element directly"""
        depth = context.depth
        node_info = format_element_info(elem)
        self.nodes.append((depth, node_info))
        return ElementVisitorResult.CONTINUE

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


@dataclass
class PlaceholderNode:
    """占位符节点，用于标记嵌套的目标节点"""
    element_id: str  # 唯一标识符
    element: ET.Element  # 原始XML元素引用


class ElementExtractVisitor(ElementVisitor):
    """提取XML元素信息的访问器，支持嵌套目标节点的占位符处理"""

    def __init__(self) -> None:
        self.result: List[XmlNode.MetaData] = []
        self.target_tags = {"ctr", "var", "lst", "chc", "ref"}
        self.placeholder_map: Dict[str, ET.Element] = {}  # 占位符映射表
        self._id_counter = 0

    def _generate_placeholder_id(self) -> str:
        """生成唯一占位符ID"""
        self._id_counter += 1
        return f"__PLACEHOLDER_{self._id_counter}__"

    def _extract_node_with_placeholders(self, elem: ET.Element) -> XmlNode.MetaData:
        """递归提取节点，对嵌套的目标节点使用占位符"""
        ns, tag = get_namespace_and_tag(elem)
        
        children = []
        for child in elem:
            child_ns, child_tag = get_namespace_and_tag(child)
            if child_tag in self.target_tags:
                # 为嵌套的目标节点创建占位符
                placeholder_id = self._generate_placeholder_id()
                self.placeholder_map[placeholder_id] = child
                placeholder = XmlNode.MetaData(
                    namespace="__PLACEHOLDER__",
                    tag="placeholder",
                    attributes={"id": placeholder_id, "original_tag": child_tag},
                    text="",
                    children=[],
                )
                children.append(placeholder)
            else:
                # 递归处理非目标节点
                children.append(self._extract_node_with_placeholders(child))
        
        return XmlNode.MetaData(
            namespace=ns,
            tag=tag,
            attributes=elem.attrib,
            text=elem.text.strip() if elem.text else "",
            children=children,
        )

    def _resolve_placeholders(self, node: XmlNode.MetaData) -> XmlNode.MetaData:
        """递归解析占位符，替换为实际的目标节点"""
        if node.namespace == "__PLACEHOLDER__" and node.tag == "placeholder":
            # 这是一个占位符，需要替换
            placeholder_id = node.attributes.get("id", "")
            if placeholder_id in self.placeholder_map:
                original_elem = self.placeholder_map[placeholder_id]
                # 递归提取原始元素，但不再创建新的占位符
                return self._extract_node_recursive(original_elem)
            else:
                # 占位符未找到，返回原节点
                return node
        else:
            # 递归处理子节点
            resolved_children = [self._resolve_placeholders(child) for child in node.children]
            return XmlNode.MetaData(
                namespace=node.namespace,
                tag=node.tag,
                attributes=node.attributes,
                text=node.text,
                children=resolved_children,
            )

    def _extract_node_recursive(self, elem: ET.Element) -> XmlNode.MetaData:
        """递归提取节点，不使用占位符（用于占位符解析阶段）"""
        ns, tag = get_namespace_and_tag(elem)
        children = [self._extract_node_recursive(child) for child in elem]
        return XmlNode.MetaData(
            namespace=ns,
            tag=tag,
            attributes=elem.attrib,
            text=elem.text.strip() if elem.text else "",
            children=children,
        )

    def postprocess(self) -> List[XmlNode.MetaData]:
        """后处理：解析所有占位符，生成完整的节点树"""
        return [self._resolve_placeholders(node) for node in self.result]

    def postprocess_to_xdm(self) -> List[Any]:
        """后处理：转换为XdmNode.MetaData"""
        from modules.plugins.type_classes.xdm import XdmNode
        processed_nodes = self.postprocess()
        
        def convert_to_xdm(node: XmlNode.MetaData):
            # 递归转换子节点 - 保持XmlNode.MetaData类型
            converted_children = [convert_xml_children(child) for child in node.children]
            # 创建新的XmlNode.MetaData，包含处理后的子节点
            xml_meta = XmlNode.MetaData(
                namespace=node.namespace,
                tag=node.tag,
                attributes=node.attributes,
                text=node.text,
                children=converted_children,
            )
            return XdmNode.MetaData(xml_meta=xml_meta, config=None)
        
        def convert_xml_children(node: XmlNode.MetaData) -> XmlNode.MetaData:
            # 递归处理子节点，保持XmlNode.MetaData类型
            converted_children = [convert_xml_children(child) for child in node.children]
            return XmlNode.MetaData(
                namespace=node.namespace,
                tag=node.tag,
                attributes=node.attributes,
                text=node.text,
                children=converted_children,
            )
        
        return [convert_to_xdm(node) for node in processed_nodes]

    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        ns, tag = get_namespace_and_tag(elem)
        
        if tag in self.target_tags:
            # 提取目标节点，使用占位符处理嵌套
            node = self._extract_node_with_placeholders(elem)
            self.result.append(node)
            return ElementVisitorResult.SKIP_CHILDREN
        
        return ElementVisitorResult.CONTINUE

    def print_summary(self) -> None:
        """打印提取结果的摘要"""
        print("\n--- Extracted Elements ---")
        processed = self.postprocess()
        for item in processed:
            print(f"{item}")

    def get_child_a_da_summary_dict(self) -> Dict[Tuple[str, str, Tuple[Tuple[str, str], ...]], set]:
        """
        返回每个父节点(ctr, var, lst, chc, ref)下的所有a, da子节点类型(namespace, tag, name)集合的字典
        """
        parent_a_da_map = dict()
        processed_nodes = self.postprocess()

        for item in processed_nodes:
            parent_tag = item.tag
            parent_ns = item.namespace if item.namespace else ""
            if parent_tag not in self.target_tags:
                continue
            
            parent_attrs_tuple = tuple(sorted(item.attributes.items()))
            parent_key = (parent_ns, parent_tag, parent_attrs_tuple)
            
            for child in item.children:
                if child.tag in ("a", "da"):
                    ns = child.namespace if child.namespace else ""
                    name = child.attributes.get("name", "")
                    key = (ns, child.tag, name)
                    if parent_key not in parent_a_da_map:
                        parent_a_da_map[parent_key] = set()
                    parent_a_da_map[parent_key].add(key)
        return parent_a_da_map


data = """
<root>
    <var name="Speed" value="100" type="int"/>
    <ctr name="Config">
        <var name="Enable" value="true" type="bool"/>
        <lst name="Items">
            ITEMS TEXT
            <var name="Item1" value="A"/>
            <var name="Item2" value="B"/>
        </lst>
        LST TAIL
    </ctr>
    <chc name="Mode" default="auto">
        aa
        <var name="Manual"/>
        aa
        <var name="Auto"/>
        aa
    </chc>
    <ref name="Ref1" target="Speed"/>
</root>
"""


def get_namespaces(xml_file):
    namespaces = {}
    for event, elem in ET.iterparse(xml_file, events=('start-ns',)):
        prefix, uri = elem
        namespaces[prefix] = uri
    return namespaces

if __name__ == "__main__":
    # 测试数据：包含嵌套目标节点
    test_data = """
    <root xmlns:d="http://www.tresos.de/_projects/DataModel2/06/data.xsd"
          xmlns:a="http://www.tresos.de/_projects/DataModel2/08/attribute.xsd">
        <d:var name="Speed" value="100" type="int"/>
        <d:ctr name="Config">
            <a:a name="UUID" value="12345"/>
            <d:var name="Enable" value="true" type="bool"/>
            <d:lst name="Items">
                <a:a name="DESC" value="Items list"/>
                <d:var name="Item1" value="A"/>
                <d:var name="Item2" value="B"/>
                <d:ctr name="NestedConfig">
                    <a:a name="NESTED_UUID" value="67890"/>
                    <d:var name="NestedVar" value="nested"/>
                </d:ctr>
            </d:lst>
        </d:ctr>
        <d:chc name="Mode" default="auto">
            <d:var name="Manual"/>
            <d:var name="Auto"/>
        </d:chc>
        <d:ref name="Ref1" target="Speed"/>
    </root>
    """

    print("=== 测试嵌套目标节点的占位符提取 ===")
    
    # 解析XML
    root = ET.fromstring(test_data)
    
    # 创建访问器链
    filter_visitor = ElementFilterVisitor(
        included_tags=["root", "var", "ctr", "lst", "chc", "ref"]
    )
    extract_visitor = ElementExtractVisitor()
    
    visitor_chain = ElementVisitorChain([filter_visitor, extract_visitor])
    
    # 执行遍历
    visitor_chain.traverse(root)
    
    print(f"\n提取到 {len(extract_visitor.result)} 个目标节点")
    
    # 显示原始结果（包含占位符）
    print("\n--- 原始结果（包含占位符） ---")
    for i, node in enumerate(extract_visitor.result):
        print(f"节点 {i+1}: {node.tag} (namespace: {node.namespace})")
        print(f"  属性: {node.attributes}")
        print(f"  子节点数: {len(node.children)}")
        for j, child in enumerate(node.children):
            if child.namespace == "__PLACEHOLDER__":
                print(f"    子节点 {j+1}: [占位符] -> {child.attributes.get('original_tag', 'unknown')}")
            else:
                print(f"    子节点 {j+1}: {child.tag} (ns: {child.namespace})")
    
    # 后处理：解析占位符
    print("\n--- 后处理结果（占位符已解析） ---")
    processed_nodes = extract_visitor.postprocess()
    for i, node in enumerate(processed_nodes):
        print(f"节点 {i+1}: {node}")
    
    # 转换为XdmNode
    print("\n--- 转换为XdmNode ---")
    xdm_nodes = extract_visitor.postprocess_to_xdm()
    for i, xdm_node in enumerate(xdm_nodes):
        print(f"XdmNode {i+1}: tag={xdm_node.tag}, type={xdm_node.type}")
        print(f"  XML结构: {xdm_node.xml_meta}")
    
    # 统计a/da子节点
    print("\n--- a/da子节点统计 ---")
    summary_dict = extract_visitor.get_child_a_da_summary_dict()
    for parent_key, child_set in summary_dict.items():
        parent_ns, parent_tag, parent_attrs = parent_key
        parent_attrs_dict = dict(parent_attrs)
        print(f"父节点: {parent_tag} (ns: {parent_ns}, attrs: {parent_attrs_dict})")
        for child_ns, child_tag, child_name in sorted(child_set):
            print(f"  -> {child_tag}:{child_name} (ns: {child_ns})")
    
    print("\n=== 测试完成 ===")
    
