"""
yaml node处理
通过yaml中的特殊数据节点(CHILDREN)构建一个逻辑YAML树结构
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass

from .file_node import FileType, FileNode, DirectoryNode


class YamlNode:
    def __init__(self, yaml_data: Optional[Dict[str, any]], yaml_name: str):
        # See YamlNode as a DirectoryNode with additional YAML-specific data.
        self._node = DirectoryNode(yaml_name)
        self.data = yaml_data

    def add_child(self, child: "YamlNode") -> None:
        """Add a child YamlNode to this node."""
        if child:
            self._node._add_node(child._node)
