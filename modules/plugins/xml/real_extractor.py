import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Protocol, Tuple, Union
from dataclasses import dataclass, field
from enum import IntFlag
import sys
import os
import yaml


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


    def save_node_to_yaml_tree(self, out_dir: str) -> None:
        """将节点保存为一个yaml文件树，文件名优先用attributes['name']，否则用unnamed_<tag>.yaml"""
        root_node = self.result[0] if self.result else None

        if root_node is None:
            print("No nodes to save.")
            return

        os.makedirs(out_dir, exist_ok=True)
        
        # 使用扁平化结构避免路径过长
        self.flat_mode = True  # 启用扁平化模式
        self.saved_files = {}  # 记录已保存的文件，避免重复
        
        self._save_node_recursive(root_node, out_dir)

    def _get_safe_filename(self, node: XmlNode.MetaData, parent_path: str = "") -> str:
        """获取安全的文件名，避免路径过长"""
        name = node.attributes.get("name")
        if name:
            base_name = name
        else:
            base_name = f"unnamed_{node.tag}"
        
        # 在扁平化模式下，使用父路径信息作为前缀
        if hasattr(self, 'flat_mode') and self.flat_mode and parent_path:
            # 将路径层级信息编码到文件名中
            path_hash = abs(hash(parent_path)) % 10000  # 4位数字避免冲突
            safe_name = f"{path_hash:04d}_{base_name}"
        else:
            safe_name = base_name
            
        return f"{safe_name}.yaml"

    def _get_node_filename(self, node: XmlNode.MetaData) -> str:
        """获取节点的yaml文件名"""
        name = node.attributes.get("name")
        if name:
            return f"{name}.yaml"
        else:
            return f"unnamed_{node.tag}.yaml"

    def _resolve_filename_conflicts(self, node: XmlNode.MetaData) -> None:
        """解决子节点中的文件名冲突问题"""
        # 收集无name属性的重名节点
        unnamed_nodes = {}
        for child in node.children:
            if hasattr(child, "tag") and child.tag not in ["a", "da"]:
                fname = self._get_node_filename(child)
                if fname.startswith("unnamed_"):
                    unnamed_nodes.setdefault(fname, []).append(child)

        # 为重名节点添加索引后缀
        for fname, nodes in unnamed_nodes.items():
            if len(nodes) > 1:
                for i, n in enumerate(nodes):
                    n.attributes["name"] = f"{n.tag}_{i+1}"

    def _validate_no_duplicates(self, node: XmlNode.MetaData, cur_dir: str) -> None:
        """验证没有重复的yaml文件名"""
        filename_count = {}
        for child in node.children:
            if hasattr(child, "tag") and child.tag not in ["a", "da"]:
                fname = self._get_node_filename(child)
                filename_count[fname] = filename_count.get(fname, 0) + 1

        duplicate_files = [fname for fname, count in filename_count.items() if count > 1]
        if duplicate_files:
            raise RuntimeError(f"Duplicate yaml filenames detected in directory '{cur_dir}': {duplicate_files}. Please check node names or tags.")

    def _process_a_da_nodes(self, node: XmlNode.MetaData) -> List[Dict[str, Any]]:
        """处理a/da节点，将其转换为字典格式"""
        a_da_list = []
        for child in node.children:
            if hasattr(child, "tag") and child.tag in ["a", "da"]:
                a_da_list.append({
                    "namespace": child.namespace,
                    "tag": child.tag,
                    "attributes": child.attributes,
                    "text": child.text,
                    "children": [
                        {
                            "namespace": gc.namespace,
                            "tag": gc.tag,
                            "attributes": gc.attributes,
                            "text": gc.text,
                        }
                        for gc in child.children
                    ],
                })
        return a_da_list

    def _get_children_directory(self, node: XmlNode.MetaData, cur_dir: str) -> Optional[str]:
        """获取子节点目录路径，如果没有非a/da子节点则返回None"""
        has_child_nodes = any(hasattr(child, "tag") and child.tag not in ["a", "da"] for child in node.children)
        if not has_child_nodes:
            return None
        
        # 扁平化模式：所有文件都保存在根目录，不创建子目录
        if hasattr(self, 'flat_mode') and self.flat_mode:
            return cur_dir
            
        parent_yaml_name = self._get_node_filename(node)
        parent_folder_name = os.path.splitext(parent_yaml_name)[0] + "_children"
        children_dir = os.path.join(cur_dir, parent_folder_name)
        
        # 确保所有父目录都存在
        try:
            os.makedirs(children_dir, exist_ok=True)
            return children_dir
        except Exception as e:
            print(f"Failed to create directory {children_dir}: {e}")
            print(f"Current directory: {cur_dir}")
            print(f"Parent exists: {os.path.exists(cur_dir)}")
            raise RuntimeError(f"Cannot create children directory {children_dir}: {e}")

    def _save_node_recursive(self, node: XmlNode.MetaData, cur_dir: str, parent_path: str = "") -> None:
        """递归保存节点及其子节点"""
        # 1. 解决文件名冲突
        self._resolve_filename_conflicts(node)
        
        # 2. 验证没有重复文件名（扁平化模式下跳过）
        if not (hasattr(self, 'flat_mode') and self.flat_mode):
            self._validate_no_duplicates(node, cur_dir)

        # 3. 处理a/da节点
        a_da_list = self._process_a_da_nodes(node)

        # 4. 准备children目录
        children_dir = self._get_children_directory(node, cur_dir)

        # 5. 构建yaml数据结构
        yaml_dict: Dict[str, Any] = {
            "namespace": node.namespace,
            "tag": node.tag,
            "attributes": node.attributes,
            "text": node.text,
            "CHILDREN_PATH": [],
        }

        if a_da_list:
            yaml_dict["a_da"] = a_da_list

        # 6. 递归处理非a/da子节点
        if children_dir:
            for child in node.children:
                if hasattr(child, "tag") and child.tag not in ["a", "da"]:
                    # 扁平化模式：使用安全文件名
                    if hasattr(self, 'flat_mode') and self.flat_mode:
                        child_path = f"{parent_path}/{node.tag}" if parent_path else node.tag
                        child_filename = self._get_safe_filename(child, child_path)
                        
                        # 检查文件是否已存在，避免重复保存
                        if child_filename not in self.saved_files:
                            child_yaml_path = os.path.join(children_dir, child_filename)
                            yaml_dict["CHILDREN_PATH"].append(child_filename)
                            self.saved_files[child_filename] = True
                            self._save_node_recursive(child, children_dir, child_path)
                        else:
                            yaml_dict["CHILDREN_PATH"].append(child_filename)
                    else:
                        child_yaml_path = os.path.join(children_dir, self._get_node_filename(child))
                        yaml_dict["CHILDREN_PATH"].append(os.path.relpath(child_yaml_path, cur_dir))
                        self._save_node_recursive(child, children_dir, parent_path)

        # 7. 保存当前节点的yaml文件
        if hasattr(self, 'flat_mode') and self.flat_mode:
            out_file = os.path.join(cur_dir, self._get_safe_filename(node, parent_path))
        else:
            out_file = os.path.join(cur_dir, self._get_node_filename(node))
        
        # 确保输出文件的目录存在
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                yaml.dump(yaml_dict, f, allow_unicode=True, default_flow_style=False)
            print(f"Saved: {out_file}")
        except Exception as e:
            print(f"Error saving file: {out_file}")
            print(f"Directory exists: {os.path.exists(os.path.dirname(out_file))}")
            print(f"Directory path: {os.path.dirname(out_file)}")
            print(f"File path length: {len(out_file)}")
            raise RuntimeError(f"Failed to save yaml file {out_file}: {e}")
        
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

    # 保存为yaml文件
    output_dir = os.path.join(os.path.dirname(xdm_file), "output")
    print(f"\n=== 保存为 YAML 文件到 {output_dir} ===")
    extract_visitor.save_node_to_yaml_tree(output_dir)