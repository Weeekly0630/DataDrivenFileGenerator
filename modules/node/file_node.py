"""
FileNode 模块
提供文件和目录节点的表示和操作。
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union, cast, Tuple, Callable
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import os


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FilePathResolver:
    """文件路径解析器，用于处理文件路径的标准化和解析"""

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


class BaseNode:
    """N叉树节点基类"""

    def __init__(
        self,
        obj: Any,
        parent: Optional["BaseNode"] = None,
        children: List["BaseNode"] = [],
    ):
        self.parent: Optional["BaseNode"] = parent  # 父节点
        self.children: List[BaseNode] = children  # 子节点列表
        self.mapping_obj: Any = obj  # 将当前BaseNode的节点映射到一个对象上

    def post_traversal(self, func: Callable[..., None], *args, **kwargs) -> None:
        """后续遍历子节点"""
        for child in self.children:
            child.post_traversal(func)
        func(self.mapping_obj, *args, **kwargs)

    def pre_traversal(self, func: Callable[..., None], *args, **kwargs) -> None:
        """前序遍历子节点"""
        func(self.mapping_obj, *args, **kwargs)
        for child in self.children:
            child.pre_traversal(func)


@dataclass
class FildSystemMetaDataNode:
    """文件系统节点元数据"""

    name: str  # 节点名称


class FileTreeHandler:
    """树处理器，用于处理文件系统树的操作"""

    @staticmethod
    def get_abs_path(node: Union["FileNode", "DirectoryNode"]) -> str:
        """获取节点在文件树中的全路径"""
        cur_node: Union["FileNode", "DirectoryNode"] = node
        path_parts = []

        while cur_node._parent.parent:
            path_parts.append(cur_node.meta_data.name)
            cur_node = cur_node._parent.parent.mapping_obj

        # Reverse the path parts to get the correct order
        path_parts.reverse()
        if not path_parts:
            return "/"
        return "/" + "/".join(path_parts)

    @staticmethod
    def get_rel_path(
        node: Union["FileNode", "DirectoryNode"],
        from_node: Union["FileNode", "DirectoryNode"],
    ) -> str:
        """获取节点相对于from_node的相对路径: from_node -> node
        from_node 可以是 DirectoryNode 或 FileNode
        """

        # 获取从根到node的路径
        def get_path_segments(n):
            segments = []
            current = n
            while current is not None:
                segments.append(current.meta_data.name)
                if hasattr(current, "_parent"):
                    current = (
                        current._parent.parent.mapping_obj
                        if current._parent.parent
                        else None
                    )
                else:
                    current = None
            segments.reverse()
            return segments

        node_path = get_path_segments(node)
        # 如果from_node是FileNode，则用其父目录计算路径
        if hasattr(from_node, "_parent") and isinstance(from_node, FileNode):
            if from_node._parent.parent:
                from_path = get_path_segments(from_node._parent.parent.mapping_obj)
            else:
                from_path = []
        else:
            from_path = get_path_segments(from_node)

        # 找到公共前缀长度
        common_len = 0
        for a, b in zip(node_path, from_path):
            if a == b:
                common_len += 1
            else:
                break

        # 需要向上多少层
        up_count = len(from_path) - common_len
        up_parts = [".."] * up_count
        down_parts = node_path[common_len:]

        if up_parts and down_parts:
            return "/".join(up_parts + down_parts)
        elif up_parts:
            return "/".join(up_parts)
        elif down_parts:
            return "/".join(down_parts)
        else:
            return "."


class FileNode:
    def __init__(self, file_name: str, parent: Any, obj: Any = None) -> None:
        self._parent: BaseNode = BaseNode(obj=obj if obj else self, parent=parent)
        self.meta_data: FildSystemMetaDataNode = FildSystemMetaDataNode(name=file_name)

    @property
    def abs_path(self) -> str:
        """获取文件的绝对路径"""
        return FileTreeHandler.get_abs_path(self)

    def rel_path(self, from_node: Union["FileNode", "DirectoryNode"]) -> str:
        """获取文件相对于from_node的相对路径，from_node 可以是目录或文件节点"""
        return FileTreeHandler.get_rel_path(self, from_node)


class DirectoryNode:
    def __init__(
        self, dir_name: str, parent: Any, obj: Any = None, children: List[Any] = []
    ) -> None:
        self._parent: BaseNode = BaseNode(
            obj=obj if obj else self, parent=parent, children=children
        )
        self.meta_data = FildSystemMetaDataNode(name=dir_name)

    @property
    def abs_path(self) -> str:
        """获取文件的绝对路径"""
        return FileTreeHandler.get_abs_path(self)

    def rel_path(self, from_node: Union["FileNode", "DirectoryNode"]) -> str:
        """获取目录相对于from_node的相对路径，from_node 可以是目录或文件节点"""
        return FileTreeHandler.get_rel_path(self, from_node)

    def append_child(self, child: Union[FileNode, "DirectoryNode"]) -> None:
        """添加子节点"""
        if not isinstance(child, (FileNode, DirectoryNode)):
            raise TypeError("Child must be a FileNode or DirectoryNode instance.")

        if child._parent.parent is not None:
            raise ValueError(f"Child {child.meta_data.name} already has a parent.")

        self._parent.children.append(child._parent)
        child._parent.parent = self._parent

    def create_file(self, file_name: str) -> FileNode:
        """创建文件节点并添加到当前目录"""
        file_node = FileNode(file_name, None)
        self.append_child(file_node)
        return file_node

    def cretate_directory(self, dir_name: str) -> "DirectoryNode":
        """创建子目录节点并添加到当前目录"""
        dir_node = DirectoryNode(dir_name, None, [])
        self.append_child(dir_node)
        return dir_node

    def build_tree(
        self, file_sys_path: str, patterns: Optional[Union[str, List[str]]] = None
    ) -> None:
        """在指定file system path下构建一个目录树, 并且通过patterns过滤文件。
        此外当前的DirectoryNode的名字将被修改为指定的file_sys_path。
        Args:
            file_sys_path: 文件系统路径
            patterns: 文件名模式列表或单个模式字符串，支持通配符匹配
        Raises:
            ValueError: 如果file_sys_path不是有效的目录路径
        """
        # 统一化patterns为列表
        if isinstance(patterns, str):
            patterns = [patterns]

        if not os.path.isdir(file_sys_path):
            raise ValueError(f"{file_sys_path} is not a valid directory path.")

        # 设置当前目录的名称为file_sys_path
        self.meta_data.name = FilePathResolver.normalize_path(file_sys_path)

        # 用于跟踪目录节点
        directory_node_map: Dict[str, "DirectoryNode"] = {file_sys_path: self}

        for root, dirs, files in os.walk(file_sys_path):
            current_directory_node: Optional["DirectoryNode"] = directory_node_map.get(
                root
            )
            if current_directory_node is None:
                raise ValueError(f"Directory {root} not found in directory_node_map.")

            # 添加文件夹
            for dir_name in dirs:
                # 文件夹不需要过滤
                normalized_dir_name = FilePathResolver.normalize_path(dir_name)
                current_directory_node.cretate_directory(normalized_dir_name)
                # 以绝对路径为键，存储当前目录节点
                directory_node_map[os.path.join(root, dir_name)] = (
                    current_directory_node
                )

            # 添加文件
            for filename in files:
                normalized_filename = FilePathResolver.normalize_path(filename)
                if not patterns or any(
                    fnmatch(normalized_filename, FilePathResolver.normalize_path(p))
                    for p in patterns
                ):
                    # 创建文件节点并添加到当前目录
                    current_directory_node.create_file(filename)

    def flatten(self) -> Tuple[List[Union[FileNode, "DirectoryNode"]], List[int]]:
        """将目录树扁平化为节点列表, 同时保留子节点个数信息"""
        nodes: List[Union[FileNode, "DirectoryNode"]] = []
        children_group_number_list: List[int] = []

        def visitor(node: Union[FileNode, "DirectoryNode"]) -> None:
            # BaseNode Pre-order traversal Callback
            nodes.append(node)
            children_group_number_list.append(len(node._parent.children))

        self._parent.pre_traversal(visitor)

        return (nodes, children_group_number_list)

    def serialze(self, indent: int = 0) -> str:
        """序列化目录树为字符串"""
        result = []
        cur_indent = [indent]

        def visitor(node: Union[FileNode, "DirectoryNode"]) -> None:
            # BaseNode Pre-order traversal Callback
            if isinstance(node, DirectoryNode):
                cur_indent[0] += 2
                result.append(" " * (cur_indent[0]) + node.meta_data.name + "/")
            elif isinstance(node, FileNode):
                result.append(" " * (cur_indent[0]) + node.meta_data.name)
            else:
                raise TypeError(f"Unsupported node type: {type(node)}")

        self._parent.pre_traversal(visitor)

        return "\n".join(result)

    def _get_root_node(self) -> "DirectoryNode":
        """获取根节点"""
        current_node: Union[FileNode, "DirectoryNode"] = self
        while current_node._parent.parent:
            current_node = current_node._parent.parent.mapping_obj
        return cast(DirectoryNode, current_node)

    def find(self, rel_path: str) -> List[Union[FileNode, "DirectoryNode"]]:
        """通过相对路径查找节点"""
        rel_path = FilePathResolver.normalize_path(rel_path)
        parts = rel_path.split("/")
        results: List[Union[FileNode, "DirectoryNode"]] = []

        # 初始化搜索目录列表
        searching_root_dirs: List[DirectoryNode] = [self]
        parts_count = len(parts)

        # 处理绝对路径，从根节点开始查找
        if rel_path.startswith("/"):
            searching_root_dirs = [self._get_root_node()]

        def find_by_name(
            dir_node: DirectoryNode, pattern: str
        ) -> List[Union[FileNode, "DirectoryNode"]]:
            """根据一个最小路径部分查找节点"""
            results: List[Union[FileNode, "DirectoryNode"]] = []
            # 中间部分，查找子节点
            if pattern == ".":
                results.append(dir_node)
            elif pattern == "..":
                if dir_node._parent.parent:
                    results.append(dir_node._parent.parent.mapping_obj)
                else:
                    results.append(dir_node)
            elif pattern == "**":
                # 平铺子结点
                nodes = dir_node.flatten()[0]
                results.extend(nodes)
            else:
                # 常规模式匹配
                for child in dir_node._parent.children:
                    node = child.mapping_obj
                    child_name = FilePathResolver.normalize_path(node.meta_data.name)
                    if fnmatch(child_name, pattern):
                        results.append(child.mapping_obj)
            return results

        # 逐级查找
        for index, part in enumerate(parts):
            temp_searching_root_dirs = []
            for dir_node in searching_root_dirs:
                find_results = find_by_name(dir_node, part)
                if index == parts_count - 1:
                    # 如果是最后一个部分，直接添加到结果
                    results.extend(find_results)
                else:
                    # 如果不是最后一个部分，更新临时搜索目录列表
                    temp_searching_root_dirs.extend(
                        [
                            cast(DirectoryNode, res)
                            for res in find_results
                            if isinstance(res, DirectoryNode)
                        ]
                    )
            # 更新搜索目录列表
            searching_root_dirs = list(set(temp_searching_root_dirs))  # 去重

        return results


"""Simple test"""
if __name__ == "__main__":
    root = DirectoryNode("root", None, [])
    sub_dir = root.cretate_directory("subdir")
    file1 = root.create_file("file1.txt")
    file2 = sub_dir.create_file("file2.txt")

    print(root.serialze())
    print(sub_dir.serialze())

    searching_patterns = [
        "subdir/file2.txt",
        "file1.txt",
        "subdir/**",
        "subdir/*.txt",
        "**/*.txt",
        "/**/*.txt",
    ]
    for pattern in searching_patterns:
        result = root.find(pattern)
        print("Current pattern:", pattern)
        for node in result:
            if isinstance(node, FileNode):
                print(f"  Found file: {node.meta_data.name}")
            elif isinstance(node, DirectoryNode):
                print(f"  Found directory: {node.meta_data.name}")
            else:
                print("  Unknown node type found.")

    print("Absolute path of file1:", file1.abs_path)
    print("Absolute path of file2:", file2.abs_path)
    print("Absolute path of sub_dir:", sub_dir.abs_path)
    print("Absolute path of root:", root.abs_path)

    print("Relative path of file1 from root:", file1.rel_path(root))
    print("Relative path of file2 from root:", file2.rel_path(root))
    print("Relative path of sub_dir from root:", sub_dir.rel_path(root))
    print("Relative path of root from root:", root.rel_path(root))
    print("Relative path of file1 from sub_dir:", file1.rel_path(sub_dir))
    print("Relative path of file2 from sub_dir:", file2.rel_path(sub_dir))
    print("Relative path of file1 from file2:", file1.rel_path(file2))
