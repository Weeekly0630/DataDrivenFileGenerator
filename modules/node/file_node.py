"""
FileNode 模块
提供文件和目录节点的表示和操作。
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union, cast, TypeVar, Generic, Tuple
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import os

T = TypeVar("T", bound="BaseNode")


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FilePathResolver:
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize the file path to a standard format."""
        # 移除开头的./
        if path.startswith("./"):
            path = path[2:]
        # 标准化路径
        path = path.replace("\\", "/").strip("/")
        path = path.replace("//", "/")
        path = path.strip()
        path = path.lower()
        return path


class BaseNode(Generic[T]):
    """节点基类，包含文件和目录共同的属性和方法"""

    def __init__(
        self, name: str, node_type: FileType, parent: Optional[T] = None
    ):
        self.name = name
        self.type = node_type
        self.parent = parent

    def get_absolute_path(self, slice_range: Tuple = (0, None)) -> str:
        """获取节点的绝对路径，始终以/开头
        
        Args:
            slice_range: 路径切片范围 (起始索引, 结束索引)，遵循Python切片规则
                        默认为(0, None)表示完整路径
        
        Returns:
            节点的绝对路径字符串
        """
        # 1. 收集路径节点名称
        path_names = []
        current: Optional["BaseNode"] = self
        
        # 从当前节点向上遍历到根节点
        while current:
            # 跳过根节点（如果根节点名称为空）
            if current.name:
                path_names.append(current.name)
            current = current.parent
        
        # 反转列表，使顺序变为从根节点到当前节点
        path_names.reverse()
        
        # 2. 应用切片范围
        start, end = slice_range
        sliced_names = path_names[start:end]
        
        # 3. 构建路径字符串
        if not sliced_names:
            return "/"
        
        # 创建路径：/root/parent/current
        return "/" + "/".join(sliced_names)

    def get_relative_path(self, from_node: "BaseNode") -> str:
        """计算从一个节点到当前节点的相对路径"""
        # 获取两个节点的绝对路径
        from_parts = from_node.get_absolute_path().split("/")
        to_parts = self.get_absolute_path().split("/")

        # 找到公共前缀
        common_prefix_len = 0
        for i in range(min(len(from_parts), len(to_parts))):
            if from_parts[i] != to_parts[i]:
                break
            common_prefix_len = i + 1

        # 构建相对路径
        up_count = len(from_parts) - common_prefix_len
        up_path = (
            ".."
            if up_count == 1
            else "../" * (up_count - 1) + ".." if up_count > 0 else ""
        )
        down_path = "/".join(to_parts[common_prefix_len:])

        if up_path and down_path:
            return up_path + "/" + down_path
        return up_path or down_path or "."


class FileNode(BaseNode[T]):
    """文件节点"""

    def __init__(self, file_name: str, parent: Optional["DirectoryNode[T]"] = None):
        super().__init__(file_name, FileType.FILE, parent)

    def move_to_directory(self, directory: "DirectoryNode[T]") -> None:
        """将文件移动到指定目录"""
        if not isinstance(directory, DirectoryNode):
            raise TypeError("Expected a DirectoryNode instance.")

        # 从原目录移除
        parent_directory: DirectoryNode = cast(DirectoryNode, self.parent)
        if parent_directory:
            parent_directory.children.remove(self)

        # 添加到新目录
        directory.add_child(self)


class DirectoryNode(BaseNode[T]):
    """目录节点"""

    def __init__(self, dir_name: str, parent: Optional["DirectoryNode[T]"] = None):
        super().__init__(dir_name, FileType.DIRECTORY, parent)
        self.children: List[Union[FileNode[T], "DirectoryNode[T]"]] = []

    def add_child(self, node: Union[FileNode[T], "DirectoryNode[T]"]) -> None:
        """添加子节点"""
        node.parent = self
        self.children.append(node)

    def create_file(self, file_name: str) -> "FileNode[T]":
        """创建文件节点"""
        file_node = FileNode[T](file_name, self)
        self.add_child(file_node)
        return file_node

    def create_directory(self, dir_name: str) -> "DirectoryNode[T]":
        """创建子目录节点"""
        dir_node = DirectoryNode[T](dir_name, self)
        self.add_child(dir_node)
        return dir_node

    def build_tree(
        self, tree_path: str, patterns: Optional[Union[str, List[str]]] = None
    ) -> "DirectoryNode[T]":
        """构建目录树"""
        if isinstance(patterns, str):
            patterns = [patterns]

        if not os.path.isdir(tree_path):
            raise ValueError(f"{tree_path} is not a valid directory path.")

        # 创建目录映射
        dir_nodes: Dict[str, DirectoryNode] = {}
        root_path = Path(tree_path).resolve()

        for root, dirs, files in os.walk(tree_path):
            current_path = Path(root).resolve()
            rel_path = current_path.relative_to(root_path)
            current_dir_path = str(rel_path)

            # 创建或获取目录节点
            if current_dir_path not in dir_nodes:
                if current_dir_path == ".":
                    current_dir = self
                else:
                    parent_path = str(rel_path.parent)
                    parent_dir = dir_nodes[parent_path]
                    current_dir = parent_dir.create_directory(rel_path.name)
                dir_nodes[current_dir_path] = current_dir
            else:
                current_dir = dir_nodes[current_dir_path]

            # 添加文件
            for filename in files:
                normalized_filename = FilePathResolver.normalize_path(filename)
                if not patterns or any(
                    fnmatch(normalized_filename, FilePathResolver.normalize_path(p))
                    for p in patterns
                ):
                    current_dir.create_file(filename)
        # 设置根节点的名称
        # self.name = str(root_path.resolve())
        return self

    def _get_all_nodes(self) -> List[Union[FileNode[T], "DirectoryNode[T]"]]:
        """获取当前目录及其子目录下的所有节点"""
        result = [cast(DirectoryNode[T], self)]
        if not isinstance(self, DirectoryNode):
            pass
        else:
            for child in self.children:
                if isinstance(child, DirectoryNode):
                    result.extend(child._get_all_nodes())
                else:
                    result.append(cast(FileNode[T], child))
        return result

    # def _get_relative_paths(
    #     self, base_dir: "DirectoryNode"
    # ) -> List[tuple[BaseNode, str]]:
    #     """获取相对于指定目录的所有节点路径"""
    #     result = []

    #     # 获取基准路径长度（用于计算相对路径）
    #     base_parts = base_dir.get_absolute_path().rstrip("/").split("/")
    #     base_len = len(base_parts)

    #     for node in self._get_all_nodes():
    #         # 获取节点的绝对路径
    #         abs_parts = node.get_absolute_path().split("/")

    #         # 构建相对路径
    #         if len(abs_parts) <= base_len:
    #             rel_path = ""
    #         else:
    #             rel_path = "/".join(abs_parts[base_len:])

    #         result.append((node, rel_path))

    #     return result

    def find_nodes_by_path(self, path_pattern: str) -> List[Union[FileNode[T], "DirectoryNode[T]"]]:
        """
        通过路径模式查找节点，支持通配符和路径导航

        Args:
            path_pattern: 路径模式，支持：
                - 相对路径: ./config/*.yaml
                - 父目录: ../shared/*.json
                - 绝对路径: /root/config/*.xml
                - 递归查找: **/test/*.py

        Returns:
            匹配的节点列表
        """
        result: List[Union[FileNode[T], "DirectoryNode[T]"]] = []
        # 如果路径模式为空，直接返回空列表
        if path_pattern == "":
            return result

        pattern = FilePathResolver.normalize_path(path_pattern)
        base_directories: List[DirectoryNode] = [self]

        parts = pattern.split("/")
        last_index = len(parts) - 1

        # 处理绝对路径
        if pattern.startswith("/"):
            # 找到根节点
            root = self
            while root.parent:
                root = root.parent
            base_directories = [cast(DirectoryNode[T], root)]
            parts = parts[1:]  # 跳过空的第一个元素
            last_index = len(parts) - 1

        for index, part in enumerate(parts):
            # 为每一层创建新的目录列表
            next_directories: List[DirectoryNode] = []

            for base_dir in base_directories:
                if part == ".":
                    if index == last_index:  # 如果是最后一个部分，添加到结果
                        result.append(base_dir)
                    next_directories.append(base_dir)

                elif part == "..":
                    if base_dir.parent:
                        if index == last_index:  # 如果是最后一个部分，添加到结果
                            result.append(base_dir.parent)
                        next_directories.append(cast(DirectoryNode[T], base_dir.parent))

                elif part == "**":
                    # 收集所有子节点用于继续搜索
                    all_nodes = base_dir._get_all_nodes()
                    for node in all_nodes:
                        if isinstance(node, DirectoryNode):
                            next_directories.append(node)
                        if index == last_index:  # 如果是最后一个部分，所有节点都是结果
                            result.append(node)

                else:
                    # 常规模式匹配
                    for child in base_dir.children:
                        child_name = FilePathResolver.normalize_path(child.name)
                        pattern_name = FilePathResolver.normalize_path(part)
                        if fnmatch(child_name, pattern_name):
                            if isinstance(child, DirectoryNode):
                                next_directories.append(child)
                            if index == last_index:
                                result.append(child)

            # 更新当前搜索的目录列表
            base_directories = list(set(next_directories))  # 去重
            if not base_directories and index < last_index:
                return []  # 如果中途没有找到匹配的目录，提前返回空列表

        return list(set(result))  # 返回去重后的结果

    # def find_nodes_by_path(self, path_pattern: str) -> List[BaseNode]:
    #     """
    #     通过路径模式查找节点，支持通配符和路径导航

    #     Args:
    #         path_pattern: 路径模式，支持：
    #             - 相对路径: ./config/*.yaml
    #             - 父目录: ../shared/*.json
    #             - 绝对路径: /root/config/*.xml
    #             - 递归查找: **/test/*.py

    #     Returns:
    #         匹配的节点列表
    #     """
    #     if path_pattern == "":
    #         return []
    #     pattern = FilePathResolver.normalize_path(path_pattern)
    #     parts = pattern.split("/")
    #     current_nodes = [self]  # 当前层级的节点列表

    #     # 处理绝对路径
    #     if pattern.startswith("/"):
    #         # 找到根节点
    #         root = self
    #         while root.parent:
    #             root = root.parent
    #         current_nodes = [root]
    #         parts = parts[1:]  # 跳过空的第一个元素

    #     # 逐级处理路径
    #     for part in parts:
    #         next_nodes = []  # 下一层级的节点列表

    #         if part == "" or part == ".":
    #             next_nodes = current_nodes[:]  # 复制当前层级节点列表
    #             if len(parts) == 1 and (pattern == "" or pattern == "."):
    #                 # 如果是唯一的路径组件，且模式是空或点，返回一个空名称的目录节点
    #                 next_nodes = [DirectoryNode("")]

    #         elif part == "..":
    #             # 移动到父节点
    #             next_nodes = []
    #             for node in current_nodes:
    #                 if node.parent:
    #                     next_nodes.append(node.parent)
    #                 else:
    #                     return []  # 如果任何节点没有父节点，则回溯失败

    #         elif part == "**":
    #             # 收集所有节点用于后续匹配
    #             next_nodes = []
    #             remaining = parts[parts.index(part) + 1:]  # 获取后续模式
    #             for node in current_nodes:
    #                 if isinstance(node, DirectoryNode):
    #                     # 如果是最后一个模式部分，收集所有节点
    #                     if not remaining:
    #                         next_nodes.extend(node._get_all_nodes())
    #                     else:
    #                         # 否则只收集目录节点供后续匹配
    #                         next_nodes.append(node)
    #                         for child in node._get_all_nodes():
    #                             if isinstance(child, DirectoryNode):
    #                                 next_nodes.append(child)

    #         else:
    #             # 常规模式匹配
    #             for node in current_nodes:
    #                 if isinstance(node, DirectoryNode):
    #                     for child in node.children:
    #                         # 只匹配节点名称
    #                         child_name = FilePathResolver.normalize_path(child.name)
    #                         pattern_name = FilePathResolver.normalize_path(part)
    #                         if fnmatch(child_name, pattern_name):
    #                             next_nodes.append(child)

    #         current_nodes = list(dict.fromkeys(next_nodes))  # 去重
    #         if not current_nodes:
    #             break  # 没有找到匹配节点，提前退出

    #     # 处理特殊情况的返回值
    #     if pattern in ["", ".", "/"]:
    #         return [DirectoryNode("")]

    #     return current_nodes

    # 为了保持兼容性，保留原有方法但使用新的实现
    def find_files(self, pattern: str) -> List[FileNode[T]]:
        """查找匹配指定模式的文件"""
        nodes = self.find_nodes_by_path(pattern)
        return [cast(FileNode[T], node) for node in nodes if isinstance(node, FileNode)]

    def get_node_by_path(self, path: str) -> Optional[Union[FileNode[T], "DirectoryNode[T]"]]:
        """通过路径获取节点（保留用于向后兼容）"""
        nodes = [
            cast(Union[FileNode[T], "DirectoryNode[T]"], node)
            for node in self.find_nodes_by_path(path)
        ]
        return nodes[0] if nodes else None

    def serialize_tree(self, indent: int = 0) -> str:
        """序列化目录树为字符串"""
        result = [" " * indent + self.name + "/"]

        for child in self.children:
            if isinstance(child, DirectoryNode):
                result.append(child.serialize_tree(indent + 2))
            else:
                result.append(" " * (indent + 2) + child.name)

        return "\n".join(result)
