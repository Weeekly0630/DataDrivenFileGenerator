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
        text: Optional[str] = None  # 节点文本内容
        tail: Optional[str] = None  # 节点尾部文本内容
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

    class AttributeNode:
        # a, da属性节点配置
        TagType: List[str] = ["a", "da"]
        # a, da Name分类
        NameType: List[str] = [
            "UUID",
            "ADMIN-DATA",
            "DESC",
            "LOWER-MULTIPLICITY",
            "POSTBUILDVARIANTSUPPORT",
            "RELEASE",
            "UPPER-MULTIPLICITY",
            "CALCULATION-FORMULA",
            "CALCULATION-LANGUAGE",
            "DERIVED",
            "EDITABLE",
            "IMPLEMENTATIONCONFIGCLASS",
            "INVALID",
            "LABEL",
            "OPTIONAL",
            "ORIGIN",
            "POSTBUILDVARIANTMULTIPLICITY",
            "POSTBUILDVARIANTVALUE",
            "READONLY",
            "SCOPE",
            "SYMBOLICNAMEVALUE",
            "DEFAULT",
            "ENABLE",
            "RANGE",
            "WARNING",
            "WIDTH",
            "__ORIGIN",
            "COLUMNS",
            "MAX",
            "MIN",
            "VISIBLE",
            "REQUIRES-INDEX",
            "TAB",
            "DEFAULT_RADIX",
            "TOOLTIP",
            "REF",
            "DEF",
            "IMPORTER_INFO",
        ]
        """a, da子节点配置"""

        # @staticmethod
        # def name_check(name: str) -> None:
        #     if name not in Xdm.AttributeNode.NameType:
        #         raise ValueError(
        #             f"未知a/da节点name属性: {name}. 可选值: {Xdm.AttributeNode.NameType}"
        #         )

        @staticmethod
        def create_node(
            name_type: str, config_data: Dict[str, Any]
        ) -> XmlNode.MetaData:
            tag_type = "a" if name_type.startswith("da") else "da"

            if tag_type not in Xdm.AttributeNode.TagType:
                raise ValueError(
                    f"未知tag_type: {tag_type}. 可选值: {Xdm.AttributeNode.TagType}"
                )
            elif name_type not in Xdm.AttributeNode.NameType:
                raise ValueError(
                    f"未知a/da节点name属性: {name_type}. 可选值: {Xdm.AttributeNode.NameType}"
                )
            # 预处理name_type
            name_type = name_type.lower().replace("-", "_")
            # 获取对应的创建函数
            generator = getattr(Xdm.AttributeNode, f"create_{name_type}_node", None)

            if not generator:
                raise ValueError(
                    f"未知name_type: {name_type}. 可选值: {Xdm.AttributeNode.NameType}"
                )

            return generator(config_data)

        # 为每个NameType创建一个静态占位函数
        @staticmethod
        def create_uuid_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: UUID"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "UUID", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_admin_data_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: ADMIN-DATA"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "ADMIN-DATA", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_desc_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: DESC"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "DESC", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_lower_multiplicity_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: LOWER-MULTIPLICITY"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "LOWER-MULTIPLICITY", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_postbuildvariantsupport_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: POSTBUILDVARIANTSUPPORT"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "POSTBUILDVARIANTSUPPORT", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_release_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: RELEASE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "RELEASE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_upper_multiplicity_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: UPPER-MULTIPLICITY"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "UPPER-MULTIPLICITY", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_calculation_formula_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: CALCULATION-FORMULA"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "CALCULATION-FORMULA", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_calculation_language_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: CALCULATION-LANGUAGE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "CALCULATION-LANGUAGE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_derived_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: DERIVED"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "DERIVED", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_editable_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: EDITABLE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "EDITABLE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_implementationconfigclass_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: IMPLEMENTATIONCONFIGCLASS"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "IMPLEMENTATIONCONFIGCLASS", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_invalid_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: INVALID"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "INVALID", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_label_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: LABEL"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "LABEL", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_optional_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: OPTIONAL"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "OPTIONAL", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_origin_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: ORIGIN"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "ORIGIN", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_postbuildvariantmultiplicity_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: POSTBUILDVARIANTMULTIPLICITY"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "POSTBUILDVARIANTMULTIPLICITY", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_postbuildvariantvalue_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: POSTBUILDVARIANTVALUE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "POSTBUILDVARIANTVALUE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_readonly_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: READONLY"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "READONLY", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_scope_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: SCOPE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "SCOPE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_symbolicnamevalue_node(
            config_data: Dict[str, Any],
        ) -> XmlNode.MetaData:
            """占位: SYMBOLICNAMEVALUE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "SYMBOLICNAMEVALUE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_default_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: DEFAULT"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "DEFAULT", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_enable_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: ENABLE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "ENABLE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_range_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: RANGE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "RANGE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_warning_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: WARNING"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "WARNING", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_width_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: WIDTH"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "WIDTH", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create___origin_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: __ORIGIN"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "__ORIGIN", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_columns_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: COLUMNS"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "COLUMNS", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_max_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: MAX"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "MAX", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_min_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: MIN"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "MIN", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_visible_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: VISIBLE"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "VISIBLE", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_requires_index_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: REQUIRES-INDEX"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "REQUIRES-INDEX", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_tab_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: TAB"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "TAB", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_default_radix_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: DEFAULT_RADIX"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "DEFAULT_RADIX", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_tooltip_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: TOOLTIP"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "TOOLTIP", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_ref_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: REF"""
            return XmlNode.MetaData(
                namespace=None,
                tag="da",
                attributes={"name": "REF", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_def_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: DEF"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "DEF", **config_data},
                text="",
                children=[],
            )

        @staticmethod
        def create_importer_info_node(config_data: Dict[str, Any]) -> XmlNode.MetaData:
            """占位: IMPORTER_INFO"""
            return XmlNode.MetaData(
                namespace=None,
                tag="a",
                attributes={"name": "IMPORTER_INFO", **config_data},
                text="",
                children=[],
            )

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
    Tag: Tuple = ("datamodel", "ctr", "var", "lst", "chc", "ref")

    # Type定义（去重，保持顺序）
    _type_list = [
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
        "RECOMMENDED_CONFIGURATION",
        "PRE_CONFIGURED_CONF",
        "FLOAT",
        "CHOICE-REFERENCE",
        "STRING",
        "FOREIGN-REFERENCE",
        "INSTANCE",
        "MODULE-CONFIGURATION",
        "FLOAT_LABEL",
        "MULTIPLE-CONFIGURATION-CONTAINER",
        "ENUMERATION_LABEL",
    ]
    Type: Tuple = tuple(dict.fromkeys(_type_list))

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
        context: UserFunctionContext,
        ns: str,
        tag: str,
        type: str,
        attribute_config: Dict[str, str],
        children_config: Dict[str, Dict],
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

        attributes = {"type": type}
        children: List[XmlNode.MetaData] = []

        # Update attributes from attribute_config
        if attribute_config:
            attributes.update(attribute_config)

        # Process children_config to create child XmlNode.MetaData
        for attribute_name, child_cfg in children_config.items():
            # Create attribute node
            children.append(Xdm.AttributeNode.create_node(attribute_name, child_cfg))

        return XmlNode.MetaData(
            namespace=ns, tag=tag, attributes=attributes, text="", children=children
        )
