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


class XdmTagType(Enum):

    CTR = "ctr"
    VAR = "var"
    LST = "lst"
    REF = "ref"
    CHC = "chc"
    # 可根据需要继续扩展


class XdmNsType(Enum):
    """XDM节点的命名空间类型"""

    DATA = "http://www.tresos.de/_projects/DataModel2/06/data.xsd"
    ATTRIBUTE = "http://www.tresos.de/_projects/DataModel2/08/attribute.xsd"
    V = "http://www.tresos.de/_projects/DataModel2/06/schema.xsd"


class XdmElementType(Enum):
    AR_PACKAGE = "AR-PACKAGE"
    MODULE_DEF = "MODULE-DEF"


XDM_CONTENT_RULES: Dict[Tuple[str, str, str], dict] = {
    (XdmNsType.DATA.value, XdmTagType.CTR.value, XdmElementType.AR_PACKAGE.value): {
        "attributes": {"required": ["name"], "optional": []},
        "children": {"required": ["UUID"], "optional": []},
    },
    (XdmNsType.V.value, XdmTagType.CTR.value, XdmElementType.MODULE_DEF.value): {
        "attributes": {"required": [], "optional": []},
        "children": {
            "required": [
                "ADMIN-DATA",
                "DESC",
                "LOWER-MULTIPLICITY",
                "POSTBUILDVARIANTSUPPORT",
                "RELEASE",
                "UPPER-MULTIPLICITY",
                "UUID",
            ],
            "optional": [],
        },
    },
    # 其它规则...
}


class XdmNode:
    @staticmethod
    def get_admin_data_node(data: dict) -> XmlNode.MetaData:
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={"name": "ADMIN-DATA", **{k: str(v) for k, v in data.items()}},
            text="",
            children=[],
        )

    @staticmethod
    def get_desc_node(data: dict) -> XmlNode.MetaData:
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={"name": "DESC", **{k: str(v) for k, v in data.items()}},
            text="",
            children=[],
        )

    @staticmethod
    def get_lower_multiplicity_node(data: dict) -> XmlNode.MetaData:
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={
                "name": "LOWER-MULTIPLICITY",
                **{k: str(v) for k, v in data.items()},
            },
            text="",
            children=[],
        )

    @staticmethod
    def get_postbuildvariantsupport_node(data: dict) -> XmlNode.MetaData:
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={
                "name": "POSTBUILDVARIANTSUPPORT",
                **{k: str(v) for k, v in data.items()},
            },
            text="",
            children=[],
        )

    @staticmethod
    def get_release_node(data: dict) -> XmlNode.MetaData:
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={"name": "RELEASE", **{k: str(v) for k, v in data.items()}},
            text="",
            children=[],
        )

    @staticmethod
    def get_upper_multiplicity_node(data: dict) -> XmlNode.MetaData:
        value = data.get("value", data)
        if not isinstance(value, int):
            raise ValueError("Upper multiplicity value must be an integer")

        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={"name": "UPPER-MULTIPLICITY", "value": f'"{str(value)}"'},
            text="",
            children=[],
        )

    @staticmethod
    def get_uuid_node(data: dict) -> XmlNode.MetaData:
        uuid_value = data.get("value", data)
        if not isinstance(uuid_value, str):
            raise ValueError("UUID value must be a string")

        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes={"name": "UUID", "value": uuid_value},
            text="",
            children=[],
        )

    @staticmethod
    def get_default_node(child_name: str, data: dict) -> XmlNode.MetaData:
        attrs = {"name": child_name}
        if isinstance(data, dict):
            attrs.update({k: str(v) for k, v in data.items()})
        else:
            attrs["value"] = str(data)
        return XmlNode.MetaData(
            namespace=XdmNsType.ATTRIBUTE.value,
            tag="a",
            attributes=attrs,
            text="",
            children=[],
        )

    @dataclass
    class MetaData(MetaBase):
        """XDM节点的元数据，支持分类和type分组"""

        xml_meta: XmlNode.MetaData  # XML元数据
        config: Optional[Dict[str, Any]] = None  # 可选的配置项

        @property
        def namespace(self) -> Optional[str]:
            """获取XML节点的命名空间"""
            return self.xml_meta.namespace

        @property
        def tag(self) -> str:
            """获取XML节点的标签名"""
            return self.xml_meta.tag

        @property
        def type(self) -> str:
            """获取XDM节点的type属性"""
            return self.xml_meta.attributes.get("type", "")

    @staticmethod
    def create(
        context: UserFunctionContext,
        ns: str,
        tag: str,
        type: str,
        content: Dict[str, Any] = {},
    ) -> "XdmNode.MetaData":
        key = (ns, tag, type)
        rules = XDM_CONTENT_RULES.get(key)
        if not rules:
            raise ValueError(f"不支持的XDM节点类型: {key}")

        # 构造 attributes
        attr_required = rules.get("attributes", {}).get("required", [])
        attr_optional = rules.get("attributes", {}).get("optional", [])
        attributes = {}
        for attr in attr_required:
            if attr not in content:
                raise ValueError(f"缺少必填属性: {attr}")
            attributes[attr] = str(content[attr])
        for attr in attr_optional:
            if attr in content:
                attributes[attr] = str(content[attr])

        # 构造 children
        child_required = rules.get("children", {}).get("required", [])
        child_optional = rules.get("children", {}).get("optional", [])
        children = []
        for child_tag in child_required + child_optional:
            if child_tag in content:
                data = content[child_tag]
                func_name = f"get_{child_tag.lower().replace('-', '_')}_node"
                generator = getattr(XdmNode, func_name, None)
                if generator is None:
                    raise ValueError(f"未定义的子节点生成器: {func_name}")
                    generator = lambda d: XdmNode.get_default_node(child_tag, d)
                if not isinstance(data, dict):
                    data = {"value": data}
                child_node = generator(data)
                children.append(child_node)

        xml_meta = XmlNode.MetaData(
            namespace=ns,
            tag=tag,
            attributes=attributes,
            text="",
            children=children,
        )
        return XdmNode.MetaData(xml_meta=xml_meta)


if __name__ == "__main__":
    # 测试：生成一个 <v:ctr type="MODULE-DEF">，包含所有required子节点
    test_content = {
        "ADMIN-DATA": {"value": "admin-data-value"},
        "DESC": {"value": "desc-value"},
        "LOWER-MULTIPLICITY": {"value": "1"},
        "POSTBUILDVARIANTSUPPORT": {"value": "support-value"},
        "RELEASE": {"value": "release-value"},
        "UPPER-MULTIPLICITY": {"value": "10"},
        "UUID": {"value": "ECUC:xxxx"},
    }
    node = XdmNode.create(
        context=None,
        ns=XdmNsType.V.value,
        tag=XdmTagType.CTR.value,
        type=XdmElementType.MODULE_DEF.value,
        content=test_content,
    )
    print("生成的MODULE-DEF节点结构：")
    print(node.xml_meta)
