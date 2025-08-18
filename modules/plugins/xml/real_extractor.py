import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Protocol, Tuple, Union
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


class PathResolveVisitor(ElementVisitor):
    def __init__(self):
        self.path_stack = []  # 存储 (tag, index)
        self.current_path = ""
        self.last_depth = -1
        self.sibling_counts = {}  # 按深度记录兄弟节点计数

    def visit(self, elem, context):
        ns, tag = get_namespace_and_tag(elem)
        cur_depth = context.depth

        # 处理深度变化
        if cur_depth <= self.last_depth:
            self.path_stack = self.path_stack[:cur_depth]
            # 清理不需要的兄弟计数
            keys_to_remove = [k for k in self.sibling_counts if k > cur_depth]
            for k in keys_to_remove:
                del self.sibling_counts[k]

        # 计算当前标签在同级的索引
        if cur_depth not in self.sibling_counts:
            self.sibling_counts[cur_depth] = {}
        if tag not in self.sibling_counts[cur_depth]:
            self.sibling_counts[cur_depth][tag] = 0
        else:
            self.sibling_counts[cur_depth][tag] += 1

        index = self.sibling_counts[cur_depth][tag]

        # 更新路径栈
        if cur_depth < len(self.path_stack):
            self.path_stack[cur_depth] = (tag, index)
        else:
            self.path_stack.append((tag, index))

        # 生成路径
        self.current_path = "/" + "/".join(
            [f"{t}[{i}]" for t, i in self.path_stack[: cur_depth + 1]]
        )
        self.last_depth = cur_depth
        return ElementVisitorResult.CONTINUE

    def get_current_path(self) -> str:
        """获取当前解析的路径"""
        return self.current_path if self.current_path else "/"


class ElementExtractVisitor(ElementVisitor):
    """提取XML元素的访问器, 将符合条件的节点转换为 XmlNode"""

    def __init__(self) -> None:
        self.path_visitor = PathResolveVisitor()
        self.result: List[XmlNode.MetaData] = []
        self.all_nodes: Dict[str, XmlNode.MetaData] = {}  # 路径 -> 节点映射表

    def _recursively_parse_a_da(
        self, elem: ET.Element, base_path: str = ""
    ) -> List[XmlNode.MetaData]:
        """递归解析a/da节点的所有子节点"""
        child_list: List[XmlNode.MetaData] = []
        child_tag_counts = {}

        for child in elem:
            child_ns, child_tag = get_namespace_and_tag(child)

            # 计算子节点索引
            if child_tag not in child_tag_counts:
                child_tag_counts[child_tag] = 0
            else:
                child_tag_counts[child_tag] += 1

            child_index = child_tag_counts[child_tag]
            child_path = f"{base_path}/{child_tag}[{child_index}]"

            # 递归解析子节点
            grandchildren = self._recursively_parse_a_da(child, child_path)

            child_meta = XmlNode.MetaData(
                namespace=child_ns,
                tag=child_tag,
                attributes=dict(child.attrib),
                text=child.text.strip() if child.text else "",
                children=grandchildren,
            )
            child_list.append(child_meta)

        return child_list

    def print_summary(self) -> None:
        print(f"Extracted {len(self.result)} XML nodes:")
        print(f"Total nodes in mapping: {len(self.all_nodes)}")

        for node in self.result:
            print(f"{node}")

    def post_process(self) -> None:
        """后处理：用实际节点替换路径引用"""
        print("=== 开始后处理：替换路径引用 ===")

        for path, node in self.all_nodes.items():
            if "_child_refs" in node.__dict__:
                resolved_children = []
                for child_ref in node.__dict__["_child_refs"]:
                    if isinstance(child_ref, str):
                        # 路径引用，查找实际节点
                        if child_ref in self.all_nodes:
                            resolved_children.append(self.all_nodes[child_ref])
                            print(f"Resolved reference: {child_ref}")
                        else:
                            print(f"Warning: 未找到路径引用 {child_ref}")
                    else:
                        # 直接的节点对象（a/da节点）
                        resolved_children.append(child_ref)

                # 更新children
                node.children = resolved_children
                # 清理临时属性
                del node.__dict__["_child_refs"]

        print("=== 后处理完成 ===")

    def visit(
        self, elem: ET.Element, context: ElementVisitorContext
    ) -> ElementVisitorResult:
        # 先解析路径
        self.path_visitor.visit(elem, context)
        # 获取当前路径
        cur_path = self.path_visitor.get_current_path()

        ns, tag = get_namespace_and_tag(elem)
        child_list: List[Union[XmlNode.MetaData, str]] = []  # 子节点或路径引用
        child_tag_counts = {}  # 用于计算子节点的索引

        # 提取子节点信息
        for child in elem:
            child_ns, child_tag = get_namespace_and_tag(child)

            # 计算子节点在兄弟节点中的索引
            if child_tag not in child_tag_counts:
                child_tag_counts[child_tag] = 0
            else:
                child_tag_counts[child_tag] += 1

            child_index = child_tag_counts[child_tag]
            # 生成子节点的唯一路径
            child_path = f"{cur_path}/{child_tag}[{child_index}]"

            # print(f"Processing child: {child_path} (ns={child_ns}, tag={child_tag})")

            # 区分处理：a/da节点递归解析，其他目标节点保存路径引用
            if child_tag in ["a", "da"]:
                # a/da节点：递归解析所有子节点
                grandchildren = self._recursively_parse_a_da(child, child_path)
                child_meta = XmlNode.MetaData(
                    namespace=child_ns,
                    tag=child_tag,
                    attributes=dict(child.attrib),
                    text=child.text.strip() if child.text else "",
                    children=grandchildren,
                )
                child_list.append(child_meta)
            else:  # child_tag in ["datamodel", "ctr", "var", "lst", "chc", "ref"]:
                # 目标节点：保存路径引用，等待后处理
                child_list.append(child_path)
            # 其他非目标节点忽略

        cur_xml_node = XmlNode.MetaData(
            namespace=ns,
            tag=tag,
            attributes=dict(elem.attrib),
            text=elem.text.strip() if elem.text else "",
            children=[],  # 暂时为空，后续通过路径引用替换
        )
        # 将混合的子节点列表（包含路径引用）存储到特殊属性中
        cur_xml_node.__dict__["_child_refs"] = child_list

        # 保存到全局映射表
        self.all_nodes[cur_path] = cur_xml_node
        print(f"Stored node: {cur_path} -> {tag}")

        # 添加到结果列表
        self.result.append(cur_xml_node)

        return ElementVisitorResult.CONTINUE


if __name__ == "__main__":
    xdm_file = rf"U:\Users\Enlink\Documents\code\python\DataDrivenFileGenerator\modules\plugins\xml\Dio.xdm"

    filter_visitor = ElementFilterVisitor(
        included_tags=["datamodel", "ctr", "var", "lst", "chc", "ref"]
    )
    extract_visitor = ElementExtractVisitor()
    visitor_chain = ElementVisitorChain(visitors=[filter_visitor, extract_visitor])

    # 第一阶段：遍历并提取节点（包含占位节点）
    print("=== 第一阶段：节点提取 ===")
    visitor_chain.traverse(ET.parse(xdm_file).getroot())

    # 第二阶段：后处理替换路径引用
    print("\n=== 第二阶段：后处理替换路径引用 ===")
    extract_visitor.post_process()

    # 打印根节点的完整树结构
    if extract_visitor.result:
        print("\n=== 完整树结构 ===")
        print(extract_visitor.result[0])
