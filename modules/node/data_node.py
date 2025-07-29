"""
通用数据节点类，用于表示数据结构中的节点。
该类可以包含任意类型的数据，并且可以添加子节点。
它主要用于处理数据结构中的目录和文件节点。
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

from .file_node import FileType, FileNode, DirectoryNode


class DataNode:
    """通用数据节点类，用于表示数据结构中的节点。
    该类可以包含任意类型的数据，并且可以添加子节点。"""

    def __init__(
        self,
        data: Dict[str, Any],
        name: str,
        obj: Any = None,
        parent: Optional["DataNode"] = None,
    ):
        self._parent: DirectoryNode = DirectoryNode(
            dir_name=name, parent=parent, obj=obj if obj else self, children=[]
        )
        self.data = data
        self.group_number: List[int] = []  # 组成员个数列表，用来记录每个组的成员数量

    def append_child(self, child: "DataNode") -> None:
        """添加子节点"""
        if not isinstance(child, DataNode):
            raise TypeError("Child must be an instance of DataNode")

        self._parent.append_child(child._parent)

    def post_traverse(self, func: Callable[["DataNode"], None]) -> None:
        """后序遍历节点，执行给定函数"""
        self._parent._parent.post_traversal(
            func,
        )

    def serialze(self, indent: int = 0) -> str:
        """序列化目录树为字符串"""
        result = []

        def visitor(node: DataNode, depth: int) -> None:
            # BaseNode Pre-order traversal Callback
            if not isinstance(node, DataNode):
                raise TypeError("Node must be an instance of DataNode")
            # 打印当前节点信息
            result.append(" " * (depth) + node._parent.meta_data.name)

        self._parent._parent.pre_traversal(visitor)

        return "\n".join(result)
