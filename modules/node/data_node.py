"""
通用数据节点类，用于表示数据结构中的节点。
该类可以包含任意类型的数据，并且可以添加子节点。
它主要用于处理数据结构中的目录和文件节点。
"""

from enum import Enum
from typing import Optional, List, Dict, Any, TypeVar, Iterable
from dataclasses import dataclass

from .file_node import FileType, FileNode, DirectoryNode, T


class DataNode(DirectoryNode["DataNode"]):
    def __init__(
        self, data: Dict[str, Any], name: str, parent: Optional["DataNode"] = None
    ):
        super().__init__(name, parent)
        self.data: Dict[str, Any] = data
        self.children_group_number: List[int] = [] # 记录子节点组的数量
        
    def serialize_tree(self, indent: int = 0) -> str:
        """Serialize the data node to a dictionary representation."""
        return f"""
{" " * indent}{{
{"  " * (indent)}"name": {self.name},
{"  " * (indent)}"data": {self.data},
{"  " * (indent)}"children": {''.join([child.serialize_tree(indent + 2) for child in self.children])}
{" " * indent}}}
"""

    def iter_data_nodes(self) -> Iterable["DataNode"]:
        """深度优先遍历所有数据节点"""
        for child in self.children:
            if isinstance(child, DataNode):
                yield from child.iter_data_nodes()
        yield self

    def get_data(self) -> Iterable[Dict[str, Any]]:
        """深度优先遍历，获取所有数据节点的数据"""
        for node in self.iter_data_nodes():
            yield node.data

    from ..jinja.user_func.func_handler import (
        UserFunctionResolver,
        UserFunctionInfo,
    )
