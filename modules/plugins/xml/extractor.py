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


class ElementExtractVisitor(ElementVisitor):
    """提取XML元素信息的访问器"""

    def __init__(self) -> None:
        self.result: List[XmlNode.MetaData] = []

    def print_summery(self) -> None:
        """打印提取结果的摘要"""
        print("\n--- Extracted Elements ---")
        for item in self.result:
            print(f"{item}")
    
    def get_child_a_da_summary_dict(self) -> Dict[Tuple[str, str, Tuple[Tuple[str, str], ...]], set]:
        """
        返回每个父节点(ctr, var, lst, chc, ref)下的所有a, da子节点类型(namespace, tag, name)集合的字典
        key: (parent_namespace, parent_tag, parent_attributes_tuple)
        value: set((child_namespace, child_tag, child_name))
        parent_attributes_tuple: ((attr_key, attr_value), ...) 按key排序，便于去重和合并
        """
        parent_a_da_map = dict()
        target_parents = {"ctr", "var", "lst", "chc", "ref"}

        for item in self.result:
            parent_tag = item.tag
            parent_ns = item.namespace if hasattr(item, "namespace") else ""
            if parent_tag not in target_parents:
                continue
            # attributes转为tuple，便于hash和去重
            parent_attrs_tuple = tuple(sorted(item.attributes.items())) if hasattr(item, "attributes") else tuple()
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

    def print_child_a_da_summary(self) -> None:
        """打印每个父节点(ctr, var, lst, chc, ref)下的所有a, da子节点类型(namespace, tag, name)集合"""
        print("\n--- 父节点及其a, da子节点类型统计 ---")
        parent_a_da_map = self.get_child_a_da_summary_dict()
        print("每个父节点的a, da子节点类型(namespace, tag, name)：")
        for parent_tag, a_da_set in parent_a_da_map.items():
            print(f"父节点: {parent_tag}")
            for ns, tag, name in sorted(a_da_set):
                print(f"    子节点: namespace={ns!r}, tag={tag!r}, name={name!r}")
        
    def print_a_da_summary(self) -> None:
        """统计所有唯一的a, da节点(namespace, name)，以及它们可能的父节点tag集合"""
        print("\n--- a, da节点及其父节点统计 ---")
        a_da_parent_map = dict()
        
        for item in extract_visitor.result:
            parent_tag = item.tag
            for child in item.children:
                if child.tag in ("a", "da"):
                    ns = child.namespace if child.namespace else ""
                    name = child.attributes.get("name", "")
                    key = (ns, child.tag, name)
                    if key not in a_da_parent_map:
                        a_da_parent_map[key] = set()
                    a_da_parent_map[key].add(parent_tag)

        print("唯一的a, da节点(namespace, name)，及其父节点tag集合：")
        for (ns, tag, name), parent_tags in a_da_parent_map.items():
            parent_tags_str = ", ".join(sorted(parent_tags))
            print(f"tag={ns!r}:{tag}, name={name!r}, parent_tags=[{parent_tags_str}]")

    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        ns, tag = get_namespace_and_tag(elem)
        child_list: List[XmlNode.MetaData] = []
        # 提取子节点信息
        for child in elem:
            child_ns, child_tag = get_namespace_and_tag(child)
            child_list.append(
                XmlNode.MetaData(
                    namespace=child_ns,
                    tag=child_tag,
                    attributes=child.attrib,
                    text=child.text.strip() if child.text else "",
                    children=[],  # 子节点在这里不展开
                )
            )

        # 提取节点信息
        self.result.append(
            XmlNode.MetaData(
                namespace=ns,
                tag=tag,
                attributes=elem.attrib,
                text=elem.text.strip() if elem.text else "",
                children=child_list,
            )
        )

        return ElementVisitorResult.CONTINUE


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
    # 遍历1目录下所有.xdm文件
    xdm_dir = r"u:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\xml\1"
    all_files = [f for f in os.listdir(xdm_dir) if f.endswith('.xdm')]
    merged_dict = dict()

    for fname in all_files:
        xml_file = os.path.join(xdm_dir, fname)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except Exception as e:
            print(f"解析失败: {xml_file}, 错误: {e}")
            continue

        filter_visitor = ElementFilterVisitor(
            included_tags=["datamodel", "root", "var", "ctr", "lst", "chc", "ref"]
        )
        extract_visitor = ElementExtractVisitor()
        visitor_chain = ElementVisitorChain([
            filter_visitor,
            extract_visitor
        ])
        visitor_chain.traverse(root)

        # 合并字典
        file_dict = extract_visitor.get_child_a_da_summary_dict()
        for parent_key, child_set in file_dict.items():
            if parent_key not in merged_dict:
                merged_dict[parent_key] = set()
            merged_dict[parent_key].update(child_set)

    # 打印并输出到文件
    output_lines = []
    output_lines.append("=== 所有文件合并后的父节点(type分类)及a, da子节点类型统计 ===\n")
    # 仅按type属性分类
    type_grouped = dict()
    for parent_key, a_da_set in merged_dict.items():
        parent_ns, parent_tag, parent_attrs_tuple = parent_key
        parent_attrs = dict(parent_attrs_tuple)
        parent_type = parent_attrs.get("type", "<none>")
        type_key = (parent_ns, parent_tag, parent_type)
        if type_key not in type_grouped:
            type_grouped[type_key] = set()
        type_grouped[type_key].update(a_da_set)

    for (parent_ns, parent_tag, parent_type), a_da_set in type_grouped.items():
        output_lines.append(f"父节点: ns={parent_ns!r}, tag={parent_tag!r}, type={parent_type!r}")
        for ns, tag, name in sorted(a_da_set):
            output_lines.append(f"    子节点: namespace={ns!r}, tag={tag!r}, name={name!r}")
    output_str = "\n".join(output_lines)
    print("\n" + output_str)
    output_file = os.path.join(xdm_dir, "merged_a_da_summary.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_str)
    print(f"统计结果已输出到: {output_file}")
    
