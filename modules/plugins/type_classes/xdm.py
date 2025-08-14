from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase

class BasicXMLNode:
    """XML节点信息"""

    @dataclass
    class MetaData(MetaBase):
        """XML节点的元数据"""
        name: str  # 节点名
        attributes: Dict[str, str] = field(default_factory=dict)  # 节点属性
        text: str = ""  # 节点文本内容
        children: List["BasicXMLNode.MetaData"] = field(default_factory=list)  # 子节点列表