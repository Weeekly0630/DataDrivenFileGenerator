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
    """Xdm 基本元素的type类型"""

    AR_PACKAGE = "AR-PACKAGE"
    MODULE_DEF = "MODULE-DEF"


class XdmAttributeNodeType(Enum):
    """XDM节点的属性类型"""

    ADMIN_DATA = "ADMIN-DATA"
    DESC = "DESC"
    LOWER_MULTIPLICITY = "LOWER-MULTIPLICITY"
    UPPER_MULTIPLICITY = "UPPER-MULTIPLICITY"
    POSTBUILDVARIANTSUPPORT = "POSTBUILDVARIANTSUPPORT"
    RELEASE = "RELEASE"
    UUID = "UUID"


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


class XdmAttributeNode:
    """XDM节点的属性节点(a/da)"""

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


class XdmNode:
    """目标Xdm基本元素节点"""

    class Config:
        """XDM节点的配置项"""

        @dataclass
        class MetaData(MetaBase):
            attributes: Dict[str, Any]  # 节点属性
            children: Dict[str, Any]  # 配置a/da子节点配置项

    @dataclass
    class MetaData(MetaBase):
        """XDM节点的元数据，支持分类和type分组"""

        xml_meta: XmlNode.MetaData  # XML元数据

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
    def _get_rules_key(
        ns: str, tag: str, type: str
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """获取当前节点的规则键值
        返回(
            attributes_required,
            attributes_optional,
            children_required,
            children_optional
        )"""
        key = (ns, tag, type)
        rules = XDM_CONTENT_RULES.get(key)
        if not rules:
            raise ValueError(f"不支持的XDM节点类型: {key}")

        attr_required = rules.get("attributes", {}).get("required", [])
        attr_optional = rules.get("attributes", {}).get("optional", [])
        child_required = rules.get("children", {}).get("required", [])
        child_optional = rules.get("children", {}).get("optional", [])

        return (attr_required, attr_optional, child_required, child_optional)

    @staticmethod
    def create(
        context: UserFunctionContext,
        ns: str,
        tag: str,
        type: str,
        config: Optional["XdmNode.Config.MetaData"] = None,
    ) -> "XdmNode.MetaData":
        (attr_required, attr_optional, child_required, child_optional) = (
            XdmNode._get_rules_key(ns, tag, type)
        )

        if config is None and (attr_required or child_required):
            raise ValueError(f"缺少必需的配置项以生成XDM节点: {ns}, {tag}, {type}")

        # 构造 attributes
        attributes = {}
        if config is not None:
            for attr in attr_required:
                if attr not in config.attributes:
                    raise ValueError(f"缺少必填属性: {attr}")
                attributes[attr] = str(config.attributes[attr])
            for attr in attr_optional:
                if attr in config.attributes:
                    attributes[attr] = str(config.attributes[attr])
        else:
            raise ValueError(f"缺少配置项以生成XDM节点: {ns}, {tag}, {type}")

        def create_child_attribute(attr_name: str, value: Any) -> XmlNode.MetaData:
            """创建子节点属性"""
            generator = getattr(
                XdmAttributeNode,
                f"get_{attr_name.lower().replace('-', '_')}_node",
                None,
            )
            if generator is None:
                raise ValueError(f"未定义的属性生成器: {attr_name}")
            # 确保 value 是字典格式
            if not isinstance(value, dict):
                value = {"value": value}
            child_node = generator(value)
            if not isinstance(child_node, XmlNode.MetaData):
                raise ValueError(f"生成的节点不是 XmlNode.MetaData 类型: {child_node}")
            return child_node

        # 构造 children
        children = []
        for child_tag in child_required:
            if child_tag not in config.children:
                raise ValueError(f"缺少必填子节点: {child_tag}")
            data = config.children[child_tag]
            # 下一步创建
            children.append(create_child_attribute(child_tag, data))

        for child_tag in child_optional:
            if child_tag in config.children:
                data = config.children[child_tag]
                # 下一步创建
                children.append(create_child_attribute(child_tag, data))

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
        ns=XdmNsType.DATA.value,
        tag=XdmTagType.CTR.value,
        type=XdmElementType.AR_PACKAGE.value,
        config=XdmNode.Config.MetaData(
            attributes={"name": "NameOfNode"},
            children={
                "UUID": {"value": "ECUC:xxxx"},
            },
        ),
    )
    
    print("生成的MODULE-DEF节点结构：")
    print(node.xml_meta)
