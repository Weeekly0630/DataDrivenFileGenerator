from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase

from enum import Enum

class XmlNode:
    
    @dataclass
    class MetaData(MetaBase):
        """XML节点的元数据"""

        namespace: Optional[str]  # 命名空间
        tag: str  # 节点名
        attributes: Dict[str, str] = field(default_factory=dict)  # 节点属性
        text: str = ""  # 节点文本内容
        children: List["XmlNode.MetaData"] = field(
            default_factory=list
        )  # 子节点列表

        def __str__(self) -> str:
            """
            美化打印XML节点树形结构，支持层级缩进和兄弟节点美化。
            """
            lines = []
            nodes = []

            def collect(node, depth):
                desc = (
                    f"<{str(node.namespace)+":" if node.namespace else ""}{node.tag}"
                    + (f" {node.attributes}" if node.attributes else "")
                )
                if node.text:
                    desc += f" text='{node.text}'"
                desc += ">"
                nodes.append((depth, desc))
                for child in node.children:
                    collect(child, depth + 1)

            collect(self, 0)

            n = len(nodes)

            def has_sibling_at_depth(i, d):
                for j in range(i + 1, n):
                    check_depth = nodes[j][0]
                    if check_depth < d:
                        break
                    elif check_depth == d:
                        return True
                return False

            for i, (depth, desc) in enumerate(nodes):
                is_last = True
                for j in range(i + 1, n):
                    next_depth = nodes[j][0]
                    if next_depth < depth:
                        break
                    elif next_depth == depth:
                        is_last = False
                        break

                prefix = ""
                for d in range(depth):
                    if has_sibling_at_depth(i, d):
                        prefix += "│   "
                    else:
                        prefix += "    "
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{desc}")
            return "\n".join(lines)


class XdmElementType(Enum):

    CTR = "ctr"
    VAR = "var"
    LST = "lst"
    REF = "ref"
    CHC = "chc"
    # 可根据需要继续扩展


class XdmNode:
    
    @dataclass
    class MetaData(MetaBase):
        """XDM节点的元数据，支持分类和type分组"""
        xml_meta: XmlNode.MetaData  # XML元数据

        @property
        def tag(self) -> str:
            """获取XML节点的标签名"""
            return self.xml_meta.tag
        
        