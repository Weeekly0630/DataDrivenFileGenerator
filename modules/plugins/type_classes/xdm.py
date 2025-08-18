from typing import List, Dict, Any, Union, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from modules.plugins.type import MetaBase
from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)

from enum import Enum


class XmlNode:

    @dataclass
    class MetaData(MetaBase):
        """XML节点的元数据"""

        namespace: Optional[str]  # 命名空间
        attributes: Dict[str, str] = field(default_factory=dict)  # 节点属性
        tag: str = ""  # 节点名
        text: str = ""  # 节点文本内容
        children: List["XmlNode.MetaData"] = field(default_factory=list)  # 子节点列表

        def __str__(self) -> str:
            """
            美化打印XML节点树形结构，支持层级缩进和兄弟节点美化。
            """
            lines = []
            nodes = []

            def format_attrs(attrs):
                return " ".join(f'{k}="{v}"' for k, v in attrs.items())

            def collect(node, depth):
                ns_prefix = f"{node.namespace}:" if node.namespace else ""
                attrs_str = format_attrs(node.attributes)
                desc = f"<{ns_prefix}{node.tag}"
                if attrs_str:
                    desc += f" {attrs_str}"
                desc += ">"
                if node.text:
                    desc += f" {node.text}"
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


class Xdm:
    """XDM规范的XML节点定义"""

    # 命名空间定义
    Ns: Dict[str, List[str]] = {
        "mt": ["multitest.xsd"],
        "icc": ["implconfigclass.xsd"],
        "ad": ["admindata.xsd"],
        "default": ["root.xsd"],
        "a": ["attribute.xsd"],
        "d": ["data.xsd"],
        "v": ["schema.xsd"],
    }

    # Tag定义
    Tag: List[str] = ["datamodel", "ctr", "var", "lst", "chc", "ref"]

    # Type定义

    Type: Tuple[str] = (
        "AR-PACKAGE",
        "MODULE-DEF",
        "ENUMERATION",
        "IDENTIFIABLE",
        "MAP",
        "INTEGER",
        "BOOLEAN",
        "FUNCTION-NAME",
        "REFERENCE",
        "BOOLEAN_LABEL",
        "INTEGER_LABEL",
        "STRING_LABEL",
        "SYMBOLIC-NAME-REFERENCE",
        "AR-ELEMENT",
        "INTEGER",
        "RECOMMENDED_CONFIGURATION",
        "PRE_CONFIGURED_CONF",
        "FLOAT",
        "CHOICE-REFERENCE",
        "IDENTIFIABLE",
        "STRING",
        "FOREIGN-REFERENCE",
        "INSTANCE",
        "MODULE-CONFIGURATION",
        "ENUMERATION",
        "IDENTIFIABLE",
        "FLOAT",
        "REFERENCE",
        "FUNCTION-NAME",
        "IDENTIFIABLE",
        "BOOLEAN",
        "STRING",
        "FLOAT_LABEL",
        "MULTIPLE-CONFIGURATION-CONTAINER",
        "ENUMERATION_LABEL",
    )
    @staticmethod
    def _ns_check(ns: str) -> None:
        if ns not in Xdm.Ns:
            raise ValueError(f"未知命名空间: {ns}. 可选值: {list(Xdm.Ns.keys())}")

    @staticmethod
    def _tag_check(tag: str) -> None:
        if tag not in Xdm.Tag:
            raise ValueError(f"未知tag: {tag}. 可选值: {Xdm.Tag}")

    @staticmethod
    def _type_check(type: str) -> None:
        if type not in Xdm.Type:
            raise ValueError(f"未知type: {type}. 可选值: {Xdm.Type}")
    
    # 结构化生成 符合Xdm的XmlNode, 并注册到 UserFunctionResolver
    @staticmethod
    def create_xdm_node(
        context: Optional[UserFunctionContext] = None,
        ns: str = "",
        tag: str = "",
        type: str = "",
        config: Optional["XmlNode.MetaData"] = None,
    ) -> XmlNode.MetaData:
        """
        创建一个符合XDM规范的XML节点。
        """
        # Check ns
        Xdm._ns_check(ns)
        # Check tag
        Xdm._tag_check(tag)
        # Check type
        Xdm._type_check(type)