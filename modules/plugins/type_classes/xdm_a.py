import sys
import os
import re

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

from modules.plugins.type_classes.xml import XmlNode

from typing import List, Dict, Any, Union, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class XdmAttribute:
    """Xdm Attribute Node Information"""

    class Node:
        """Xdm Attribute XML Node Metadata"""

        @dataclass
        class MetaData(MetaBase):
            """Xdm Attribute Metadata"""

            name: str  # Attribute name
            metadata: Dict[str, Any] = field(
                default_factory=dict
            )  # Additional metadata

        @staticmethod
        def create(
            context: UserFunctionContext, name: str, metadata: Dict[str, Any]
        ) -> XmlNode.MetaData:
            """Create an Xdm Attribute Metadata node"""
            name = name.strip().lower().replace("-", "_")
            generator = getattr(XdmAttribute, f"create_{name}", None)
            if not generator:
                raise ValueError(f"Unsupported Xdm Attribute: {name}")
            if not isinstance(metadata, dict):
                # Automatically convert metadata to dict if not already
                metadata = {"value": metadata}
            return generator(context, metadata)

    @staticmethod
    def validate(node: XmlNode.MetaData, expect_name: str) -> bool:
        """Check if the XML node is a valid Xdm Attribute with the expected name"""
        if not isinstance(node, XmlNode.MetaData):
            raise TypeError("XdmAttribute node must be an XmlNode.MetaData object")
        if node.attributes.get("name") != expect_name:
            raise ValueError(
                f"XdmAttribute node's name attribute must be '{expect_name}'"
            )
        return True

    @staticmethod
    def _init_implementationconfigclass_type(meta_data: Any) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'IMPLEMENTATIONCONFIGCLASS'
        metadata: {
            ...
            }
        """
        results: List[XmlNode.MetaData] = []
        meta: List[Dict[str, Any]]

        if isinstance(meta_data, dict):
            meta = [meta_data]
        elif isinstance(meta_data, list):
            meta = meta_data

        for i, item in enumerate(meta):
            if "class" not in item:
                raise ValueError(
                    f"IMPLEMENTATIONCONFIGCLASS metadata item {i} must contain 'class' key"
                )
            class_txt = item["class"]
            if "value" not in item:
                raise ValueError(
                    f"IMPLEMENTATIONCONFIGCLASS metadata item {i} must contain 'value' key"
                )
            value_txt = item["value"]
            # try to get class prefix
            class_prefix = item.get("prefix", "")
            results.append(
                XmlNode.MetaData(
                    namespace="icc",
                    attributes={
                        f"{class_prefix}class": class_txt,
                    },
                    tag="v",
                    text=value_txt,
                )
            )
        return results

    @staticmethod
    def _create_tst_nodes(
        tst_list: List[Dict[str, Any]],
        expr_checker: Callable[[str], None],
        namespace: str,
    ) -> List[XmlNode.MetaData]:
        """公共方法：根据tst列表和expr检查器创建tst子节点"""
        results: List[XmlNode.MetaData] = []
        for i, item in enumerate(tst_list):
            if not isinstance(item, dict):
                raise ValueError(
                    f"metadata 'tst' item {i} must be a dict, got {type(item)}"
                )
            if "expr" not in item:
                raise ValueError(f"metadata 'tst' item {i} must contain 'expr' key")
            expr = item["expr"]
            expr_checker(expr)  # 检查表达式合法性
            attributes = {"expr": expr}
            if "true" in item:
                attributes["true"] = item["true"]
            if "false" in item:
                attributes["false"] = item["false"]
            results.append(
                XmlNode.MetaData(
                    namespace=namespace,
                    attributes=attributes,
                    tag="tst",
                )
            )
        return results

    @staticmethod
    def _init_xpath_type(
        meta_data: Dict[str, Any], namespace="a"
    ) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'XPath'"""
        tst = meta_data.get("tst")
        if tst is None:
            raise ValueError("XPath type metadata must contain 'tst' key")
        if not isinstance(tst, list):
            tst = [tst]

        # XPath允许任意表达式，不做限制
        def xpath_checker(expr: str):
            if not isinstance(expr, str) or not expr.strip():
                raise ValueError("XPath expr must be a non-empty string")

        return XdmAttribute._create_tst_nodes(tst, xpath_checker, namespace)

    @staticmethod
    def _init_range_type(
        meta_data: Dict[str, Any], namespace: str = "a"
    ) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'Range'"""
        tst = meta_data.get("tst")
        if tst is None:
            raise ValueError("Range type metadata must contain 'tst' key")
        if not isinstance(tst, list):
            tst = [tst]

        # Range只允许简单数值比较
        def range_checker(expr: str):
            if not isinstance(expr, str) or not expr.strip():
                raise ValueError("Range expr must be a non-empty string")
            # 只允许简单比较表达式
            if not re.match(r"^(<=?|>=?)\s*-?\d+(\.\d+)?$", expr.strip()):
                raise ValueError(
                    f"Range expr '{expr}' is not a valid numeric comparison"
                )

        return XdmAttribute._create_tst_nodes(tst, range_checker, namespace)

    @staticmethod
    def _init_multi_type(meta_data: Dict[str, Any]) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'Multi'"""
        results: List[XmlNode.MetaData] = []

        if "range_tst" not in meta_data:
            raise ValueError("Multi type metadata must contain 'range_tst' key")

        range_tst = meta_data["range_tst"]

        if "xpath_tst" not in meta_data:
            raise ValueError("Multi type metadata must contain 'xpath_tst' key")

        xpath_tst = meta_data["xpath_tst"]

        range_node = XdmAttribute._init_range_type({"tst": range_tst}, namespace="mt")
        xpath_node = XdmAttribute._init_xpath_type({"tst": xpath_tst}, namespace="mt")

        results.extend(range_node)
        results.extend(xpath_node)
        
        return results


    @staticmethod
    def _init_by_type(meta_data: Dict[str, Any]) -> Tuple[List[XmlNode.MetaData], str]:
        """Initialize any attribute by type"""
        if "type" not in meta_data:
            raise ValueError("Metadata must contain 'type' key")
        type_str = str(meta_data["type"]).lower()

        if type_str not in ["range", "xpath", "multi"]:
            raise ValueError("Type must be 'Range', 'XPath', or 'Multi'")

        if type_str == "xpath":
            return (XdmAttribute._init_xpath_type(meta_data), "XPath")
        elif type_str == "range":
            return (XdmAttribute._init_range_type(meta_data), "Range")
        elif type_str == "multi":
            return (XdmAttribute._init_multi_type(meta_data), "Multi")
        else:
            raise ValueError(f"Unsupported type: {type_str}")

    @staticmethod
    def _init_boolean_value(meta_data: Dict[str, Any]) -> bool:
        """
        提取配置字典中的布尔类型值，支持字符串和布尔类型输入
        """
        value = meta_data.get("value")
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                raise ValueError(
                    "Boolean value must be 'true' or 'false' (case-insensitive)"
                )
        raise ValueError("Boolean value must be a bool or a string 'true'/'false'")

    @staticmethod
    def _init_string_value(meta_data: Dict[str, Any]) -> str:
        """
        提取配置字典中的字符串类型值，支持字符串输入
        """
        value = meta_data.get("value")
        if isinstance(value, str):
            return value
        raise ValueError("String value must be of type str")

    # ADMIN_DATA
    @staticmethod
    def create_admin_data(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an AdminData attribute node"""
        # Check if the required metadata is present
        if "revision_label" not in metadata:
            raise ValueError("AdminData metadata must contain 'revision_label' key")
        if "issued_by" not in metadata:
            raise ValueError("AdminData metadata must contain 'issued_by' key")
        if "date" not in metadata:
            raise ValueError("AdminData metadata must contain 'date' key")

        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "ADMIN-DATA",
                "type": "ADMIN-DATA",
            },
            tag="a",
            children=[
                XmlNode.MetaData(
                    namespace="ad",
                    attributes={},
                    tag="ADMIN-DATA",
                    children=[
                        XmlNode.MetaData(
                            namespace="ad",
                            attributes={},
                            tag="DOC-REVISIONS",
                            children=[
                                XmlNode.MetaData(
                                    namespace="ad",
                                    attributes={},
                                    tag="DOC-REVISION",
                                    children=[
                                        XmlNode.MetaData(
                                            namespace="ad",
                                            attributes={},
                                            tag="REVISION-LABEL",
                                            text=metadata["revision_label"],
                                        ),
                                        XmlNode.MetaData(
                                            namespace="ad",
                                            attributes={},
                                            tag="ISSUED-BY",
                                            text=metadata["issued_by"],
                                        ),
                                        XmlNode.MetaData(
                                            namespace="ad",
                                            attributes={},
                                            tag="DATE",
                                            text=metadata["date"],
                                        ),
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        return node

    # CALCULATION-FORMULA
    @staticmethod
    def create_calculation_formula(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a CALCULATION-FORMULA attribute node"""
        value = XdmAttribute._init_string_value(metadata)

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "CALCULATION-FORMULA",
                "value": value,
            },
            tag="a",
            children=[],
        )

    # CALCULATION-LANGUAGE
    @staticmethod
    def create_calculation_language(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a CALCULATION-LANGUAGE attribute node"""
        value = XdmAttribute._init_string_value(metadata)

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "CALCULATION-LANGUAGE",
                "value": value,
            },
            tag="a",
            children=[],
        )

    # DERIVED
    @staticmethod
    def create_derived(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a DERIVED attribute node"""
        value: bool = XdmAttribute._init_boolean_value(metadata)
        value_str = "TRUE" if value else "FALSE"
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "DERIVED", "value": value_str},
            tag="a",
            children=[],
        )

    # DESC
    @staticmethod
    def create_desc(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a DESC attribute node with a child <a:v>"""
        value: str = XdmAttribute._init_string_value(metadata)

        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "DESC",
            },
            tag="a",
            children=[
                XmlNode.MetaData(
                    namespace="a",
                    attributes={},
                    tag="v",
                    text=value,
                    children=[],
                )
            ],
        )
        return node

    # EDITABLE
    @staticmethod
    def create_editable(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an EDITABLE attribute node"""
        tst_nodes = []
        attributes = {"name": "EDITABLE"}

        if "type" in metadata:
            tst_nodes, type_str = XdmAttribute._init_by_type(metadata)
            attributes["type"] = type_str
        else:  # True or False
            value: bool = XdmAttribute._init_boolean_value(metadata)
            if value:
                attributes["value"] = "true"
            else:
                attributes["value"] = "false"

        node = XmlNode.MetaData(
            namespace="a",
            attributes=attributes,
            tag=metadata.get("tag", "da"),  # Default to "a" tag
            children=tst_nodes,
        )
        return node

    # IMPLEMENTATIONCONFIGCLASS
    @staticmethod
    def create_implementationconfigclass(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an IMPLEMENTATIONCONFIGCLASS attribute node"""

        value = metadata.get("value", metadata)

        children_nodes: List[XmlNode.MetaData] = (
            XdmAttribute._init_implementationconfigclass_type(value)
        )

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "IMPLEMENTATIONCONFIGCLASS",
                "type": "IMPLEMENTATIONCONFIGCLASS",
            },
            tag="a",
            children=children_nodes,
        )

    # INVALID
    @staticmethod
    def create_invalid(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an INVALID attribute node"""
        # if "type" not in metadata:
        #     raise ValueError("INVALID metadata must contain 'type' key")
        # type_str = metadata["type"].lower()

        # if type_str not in ["xpath", "range"]:
        #     raise ValueError("INVALID type must be 'XPath' or 'Range'")

        # tag = metadata.get("tag", "da")  # Default to "da" tag

        # if type_str == "xpath":
        #     # XPATH
        #     child_nodes: List[XmlNode.MetaData] = XdmAttribute._init_xpath_type(
        #         meta_data=metadata
        #     )
        #     type_str = "XPath"
        # elif type_str == "range":
        #     # RANGE
        #     child_nodes = XdmAttribute._init_range_type(meta_data=metadata)
        #     type_str = "Range"
        # else:
        #     raise ValueError(f"Unsupported INVALID type: {type_str}")

        child_nodes, type_str = XdmAttribute._init_by_type(metadata)

        tag = metadata.get("tag", "da")  # Default to "da" tag
        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "INVALID",
                "type": type_str,
            },
            tag=tag,
            children=child_nodes,
        )
        return node

    # LABEL
    @staticmethod
    def create_label(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a LABEL attribute node"""
        # Check if the required metadata is present
        value: str = XdmAttribute._init_string_value(metadata)

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "LABEL",
                "value": value,
            },
            tag="a",
            children=[],
        )

    # LOWER-MULTIPLICITY
    @staticmethod
    def create_lower_multiplicity(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a LOWER-MULTIPLICITY attribute node"""
        value = XdmAttribute._init_string_value(metadata)

        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "LOWER-MULTIPLICITY",
                "value": value,
            },
            tag="a",
            children=[],
        )
        return node

    # OPTIONAL
    @staticmethod
    def create_optional(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an OPTIONAL attribute node"""
        # Check if the required metadata is present
        value: bool = XdmAttribute._init_boolean_value(metadata)
        value_str = "true" if value else "false"
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "OPTIONAL", "value": value_str},
            tag="a",
        )

    # ORIGIN
    @staticmethod
    def create_origin(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        value: str = XdmAttribute._init_string_value(metadata)
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "ORIGIN", "value": value},
            tag="a",
        )

    # POSTBUILDVARIANTSUPPORT
    @staticmethod
    def create_postbuildvariantsupport(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a POSTBUILDVARIANTSUPPORT attribute node"""
        value: bool = XdmAttribute._init_boolean_value(metadata)
        # Convert boolean to string representation
        value_str = "true" if value else "false"

        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "POSTBUILDVARIANTSUPPORT",
                "value": value_str,
            },
            tag="a",
            children=[],
        )
        return node

    # POSTBUILDVARIANTMULTIPLICITY
    @staticmethod
    def create_postbuildvariantmultiplicity(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        value: bool = XdmAttribute._init_boolean_value(metadata)
        value_str = "true" if value else "false"
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "POSTBUILDVARIANTMULTIPLICITY", "value": value_str},
            tag="a",
        )

    # POSTBUILDVARIANTVALUE
    @staticmethod
    def create_postbuildvariantvalue(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        value: bool = XdmAttribute._init_boolean_value(metadata)
        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "POSTBUILDVARIANTVALUE",
                "value": "true" if value else "false",
            },
            tag="a",
        )

    # READONLY
    @staticmethod
    def create_readonly(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a READONLY attribute node"""
        value: bool = XdmAttribute._init_boolean_value(metadata)

        # false is
        if value is False:
            raise ValueError("READONLY attribute must be true if present")

        value_str = "true" if value else "false"

        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "READONLY", "value": value_str},
            tag="a",
        )

    # SCOPE
    @staticmethod
    def create_scope(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a SCOPE attribute node"""
        value: str = XdmAttribute._init_string_value(metadata)
        if value not in ["ECU", "LOCAL"]:
            raise ValueError("SCOPE value must be 'ECU' or 'LOCAL'")

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "SCOPE",
                "value": value,
            },
            tag="a",
            children=[],
        )

    # SYMBOLICNAMEVALUE
    @staticmethod
    def create_symbolicnamevalue(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a SYMBOLICNAMEVALUE attribute node"""
        value: bool = XdmAttribute._init_boolean_value(metadata)
        value_str = "true" if value else "false"
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "SYMBOLICNAMEVALUE", "value": value_str},
            tag="a",
        )

    # UUID
    @staticmethod
    def create_uuid(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a UUID attribute node"""
        # Check if the required metadata is present
        value: str = XdmAttribute._init_string_value(metadata)

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace=metadata.get("namespace", "a"),  # Default to "a" namespace
            attributes={
                "name": "UUID",
                "value": value,
            },
            tag="a",
            children=[],
        )
        return node

    # UPPER-MULTIPLICITY
    @staticmethod
    def create_upper_multiplicity(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create an UPPER-MULTIPLICITY attribute node"""
        value: str = XdmAttribute._init_string_value(metadata)

        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "UPPER-MULTIPLICITY",
                "value": value,
            },
            tag="a",
            children=[],
        )
        return node

    # DEFAULT
    @staticmethod
    def create_default(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a DEFAULT attribute node"""
        # Check if the required metadata is present
        value: str = XdmAttribute._init_string_value(metadata)

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace="a",  # metadata["namespace"],
            attributes={
                "name": "DEFAULT",
                "value": value,
            },
            tag="a",
            children=[],
        )
        return node

    # ENABLE
    @staticmethod
    def create_enable(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        value: bool = XdmAttribute._init_boolean_value(metadata)
        value_str = "true" if value else "false"
        return XmlNode.MetaData(
            namespace="a",
            attributes={"name": "ENABLE", "value": value_str},
            tag="da",
            children=[],
        )

    # RANGE
    @staticmethod
    def create_range(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a RANGE attribute node
        List of strings or list of xpath conditions"""
        type_str = metadata.get("type", "").lower()

        child_nodes: List[XmlNode.MetaData] = []
        attributes = {"name": "RANGE"}

        if "type" in metadata:
            child_nodes, type_str = XdmAttribute._init_by_type(metadata)
            attributes["type"] = type_str
        else:
            # List of strings
            if "value" not in metadata:
                raise ValueError("RANGE metadata must contain 'value' key")

            value = metadata["value"]
            # Convert to list
            if not isinstance(value, list):
                value = [value]

            child_nodes: List[XmlNode.MetaData] = []
            for i, item in enumerate(value):
                if not isinstance(item, str):
                    raise ValueError(f"RANGE metadata item {i} must be a string")
                child_nodes.append(
                    XmlNode.MetaData(
                        namespace="a",
                        attributes={},
                        tag="v",
                        text=item,
                    )
                )
        node = XmlNode.MetaData(
            namespace="a",
            attributes=attributes,
            tag="da",
            children=child_nodes,
        )
        return node

    # RELEASE
    @staticmethod
    def create_release(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a Release attribute node"""
        # Check if the required metadata is present
        value: str = XdmAttribute._init_string_value(metadata)

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace="a",  # metadata["namespace"],
            attributes={
                "name": "RELEASE",
                "value": value,
            },
            tag="a",
            children=[],
        )
        return node

    # WARNING
    @staticmethod
    def create_warning(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        child_nodes, type_str = XdmAttribute._init_by_type(metadata)
        attributes = {"name": "WARNING", "type": type_str}

        return XmlNode.MetaData(
            namespace="a",
            attributes=attributes,
            tag="da",
            children=child_nodes,
        )


class XdmA:
    """Xdm Advanced Model"""

    @staticmethod
    def _check_attributes(
        attrs: List[XmlNode.MetaData], allowed: List[Tuple[str, str]]
    ) -> bool:
        for attr in attrs:
            if not isinstance(attr, XmlNode.MetaData):
                raise TypeError("Attributes must be XmlNode.MetaData objects")
            if (attr.tag not in [a[0] for a in allowed]) or (
                attr.attributes.get("name") not in [a[1] for a in allowed]
            ):
                raise ValueError(
                    f"Unsupported attribute: {attr.tag} with name {attr.attributes.get('name')}"
                )
        return True

    ## DATAMODEL
    class MainPage:  # for datamodel
        """Xdm Main Page Information"""

        @dataclass
        class MetaData(MetaBase):
            xml_version: str  # xml version
            namespaces: Dict[str, str]
            project: Optional[str]
            platform: Optional[str]
            peripheral: Optional[str]
            autosar_version: Optional[str]
            build_version: Optional[str]
            copyright: Optional[str]
            ctr_type: str
            ctr_factory: str
            ctr_namespaces: Dict[str, str]
            top_level_package_name: Optional[str]
            top_level_package_type: Optional[str]
            uuid_attr_xml: XmlNode.MetaData  # UUID attribute XML node

            def __str__(self) -> str:
                return super().__str__()

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.MainPage.MetaData":
            """Create a MainPage metadata node, 支持位置参数和命名参数，并检查uuid_attr_xml是否为UUID类型"""
            uuid_node = None
            result = None

            if kwargs:
                uuid_node = kwargs.get("uuid_attr_xml")

                result = XdmA.MainPage.MetaData(**kwargs)
            elif args:
                # 假定最后一个参数是uuid_attr_xml
                if len(args) >= 15:
                    uuid_node = args[14]
                result = XdmA.MainPage.MetaData(*args)
            else:
                raise ValueError(
                    "No arguments provided for MainPage.MetaData initialization"
                )

            if uuid_node is not None:
                XdmAttribute.validate(uuid_node, "UUID")

            return result

    ## AR-ELEMENT
    class ModuleDefBlock:
        """Xdm Module Definition Block Information"""

        @dataclass
        class MetaData(MetaBase):
            name: str
            release_attr_xml: XmlNode.MetaData
            admin_data_attr_xml: XmlNode.MetaData
            postbuildvariantsupport_attr_xml: XmlNode.MetaData
            desc_attr_xml: XmlNode.MetaData
            lower_multiplicity_attr_xml: XmlNode.MetaData
            upper_multiplicity_attr_xml: XmlNode.MetaData
            uuid_attr_xml: XmlNode.MetaData

            # meta for "IMPLEMENTATION_CONFIG_VARIANT" var
            imp_desc_attr_xml: XmlNode.MetaData
            imp_implementationconfigclass_attr_xml: XmlNode.MetaData
            imp_label_attr_xml: XmlNode.MetaData
            imp_uuid_attr_xml: XmlNode.MetaData
            imp_default_attr_xml: XmlNode.MetaData
            imp_range_attr_xml: XmlNode.MetaData

            module_refined_module_def_path: Optional[str] = None

    class EcuParamDefBlock:
        @dataclass
        class MetaData(MetaBase):
            name: str
            uuid_attr_xml: XmlNode.MetaData
            module_ref_path: str

    class BswModuleDescBlock:
        @dataclass
        class MetaData(MetaBase):
            name: str
            module_ref_path: str

    ## Blocks
    class ModuleBlock:
        """Xdm Configuration Block (for v:ctr)"""

        @dataclass
        class MetaData(MetaBase):
            name: str  # Module name
            desc_attr_xml: XmlNode.MetaData  # Description attribute XML node
            uuid_attr_xml: XmlNode.MetaData  # UUID attribute XML node
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.ModuleBlock.MetaData":
            # Check additional attributes

            allowed_attributes = [
                ("a", "DESC"),
                ("a", "EDITABLE"),
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "INVALID"),
                ("a", "LABEL"),
                ("a", "OPTIONAL"),
                ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                ("a", "REQUIRES-INDEX"),
                ("a", "TAB"),
                ("a", "UUID"),
                ("a", "VISIBLE"),
                ("da", "EDITABLE"),
                ("da", "ENABLE"),
                ("da", "INVALID"),
                ("da", "OPTIONAL"),
                ("da", "READONLY"),
                ("da", "TAB"),
            ]

            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[3]), allowed_attributes
            )

            return XdmA.ModuleBlock.MetaData(*args, **kwargs)

    class MapTable:
        """Xdm Map List Information (for v:lst MAP)
        列表
        """

        @dataclass
        class MetaData(MetaBase):
            name: str
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.MapTable.MetaData":
            # Check additional attributes
            allowed_attributes = [
                ("a", "COLUMNS"),
                ("a", "EDITABLE"),
                ("a", "LABEL"),
                ("a", "MAX"),
                ("a", "MIN"),
                ("a", "VISIBLE"),
                ("da", "EDITABLE"),
                ("da", "INVALID"),
                ("da", "MAX"),
                ("da", "MIN"),
                ("da", "READONLY"),
            ]

            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[1]), allowed_attributes
            )

            return XdmA.MapTable.MetaData(*args, **kwargs)

    class OrderedTable:
        """Xdm Ordered List Information (for v:lst)"""

        @dataclass
        class MetaData(MetaBase):
            name: str
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.OrderedTable.MetaData":
            # Check additional attributes
            allowed_attributes = [
                ("a", "EDITABLE"),
                ("da", "INVALID"),
                ("da", "MAX"),
                ("da", "MIN"),  # 注意最后一个是10/attribute.xsd，但元组只保留tag和name
            ]

            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[1]), allowed_attributes
            )

            return XdmA.OrderedTable.MetaData(*args, **kwargs)

    ## Elements
    class ComboBox:
        """Xdm CheckBox Information (for v:var ENUMERATION)
        下拉组件
        """

        @dataclass
        class MetaData(MetaBase):
            name: str
            desc_attr_xml: XmlNode.MetaData  # Description attribute XML node
            label_attr_xml: XmlNode.MetaData  # Label attribute XML node
            uuid_attr_xml: XmlNode.MetaData
            range_attr_xml: XmlNode.MetaData  # Range attribute XML node
            default_attr_xml: XmlNode.MetaData  # Default attribute XML node

            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)
            is_label: bool = False  # 是否是标签类型

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.ComboBox.MetaData":
            # Check additional attributes
            ENUMERATION_ATTRS = [
                ("a", "CALCULATION-FORMULA"),
                ("a", "CALCULATION-LANGUAGE"),
                ("a", "DERIVED"),
                ("a", "DESC"),
                ("a", "EDITABLE"),
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "INVALID"),
                ("a", "LABEL"),
                ("a", "OPTIONAL"),
                ("a", "ORIGIN"),
                ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                ("a", "POSTBUILDVARIANTVALUE"),
                ("a", "READONLY"),
                ("a", "SCOPE"),
                ("a", "SYMBOLICNAMEVALUE"),
                ("a", "UUID"),
                ("da", "DEFAULT"),
                ("da", "EDITABLE"),
                ("da", "ENABLE"),
                ("da", "INVALID"),
                ("da", "OPTIONAL"),
                ("da", "RANGE"),
                ("da", "READONLY"),
                ("da", "WARNING"),
                ("da", "WIDTH"),
            ]
            ENUMERATION_LABEL_ATTRS = [
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "ORIGIN"),
                ("a", "POSTBUILDVARIANTVALUE"),
                ("a", "SCOPE"),
                ("a", "SYMBOLICNAMEVALUE"),
            ]

            allowed_attrs = (
                ENUMERATION_LABEL_ATTRS
                if kwargs.get("is_label", args[7] if len(args) > 7 else False)
                else ENUMERATION_ATTRS
            )

            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[6] if len(args) > 6 else []),
                allowed_attrs,
            )
            return XdmA.ComboBox.MetaData(*args, **kwargs)

    class InputBox:
        """Xdm Input Information (for v:var INTEGER, STRING, FLOAT, FUNCTION-NAME)"""

        @dataclass
        class MetaData(MetaBase):
            name: str
            type: str
            desc_attr_xml: XmlNode.MetaData
            label_attr_xml: XmlNode.MetaData
            uuid_attr_xml: XmlNode.MetaData
            range_attr_xml: XmlNode.MetaData
            default_attr_xml: XmlNode.MetaData
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)
            is_label: bool = False  # 是否是标签类型

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.InputBox.MetaData":
            allowed_types = [
                "INTEGER",
                "FLOAT",
                "STRING",
                "INTEGER_LABEL",
                "FLOAT_LABEL",
                "STRING_LABEL",
                "FUNCTION-NAME",
            ]
            # 获取原始type
            input_type_raw = kwargs.get("type", args[1] if len(args) > 1 else None)

            # 自动判断 is_label，并去除_LABEL后缀
            if input_type_raw and input_type_raw.endswith("_LABEL"):
                input_type = input_type_raw.replace("_LABEL", "")
                is_label = True
            else:
                input_type = input_type_raw
                is_label = kwargs.get("is_label", False)
            if input_type not in allowed_types:
                raise ValueError(
                    f"Unsupported Input type: {input_type_raw}. Allowed types: {allowed_types} or *_LABEL"
                )

            type_optional_attrs = {
                "INTEGER": [
                    ("a", "CALCULATION-FORMULA"),
                    ("a", "CALCULATION-LANGUAGE"),
                    ("a", "DEFAULT_RADIX"),
                    ("a", "DERIVED"),
                    ("a", "EDITABLE"),
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "INVALID"),
                    ("a", "OPTIONAL"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "READONLY"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("a", "WIDTH"),
                    ("da", "DEFAULT"),
                    ("da", "EDITABLE"),
                    ("da", "ENABLE"),
                    ("da", "INVALID"),
                    ("da", "RANGE"),
                    ("da", "READONLY"),
                    ("da", "TOOLTIP"),
                    ("da", "VISIBLE"),
                    ("da", "WARNING"),
                ],
                "INTEGER_LABEL": [
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("da", "DEFAULT"),
                    ("da", "INVALID"),
                    ("da", "READONLY"),
                ],
                "FLOAT": [
                    ("a", "EDITABLE"),
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "INVALID"),
                    ("a", "OPTIONAL"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "RANGE"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("da", "DEFAULT"),
                    ("da", "EDITABLE"),
                    ("da", "ENABLE"),
                    ("da", "INVALID"),
                    ("da", "RANGE"),
                ],
                "FLOAT_LABEL": [
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("da", "DEFAULT"),
                    ("da", "INVALID"),
                    ("da", "READONLY"),
                ],
                "STRING": [
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "OPTIONAL"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("da", "DEFAULT"),
                    ("da", "EDITABLE"),
                    ("da", "ENABLE"),
                    ("da", "INVALID"),
                    ("da", "RANGE"),
                ],
                "STRING_LABEL": [
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "OPTIONAL"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("da", "DEFAULT"),
                    ("da", "EDITABLE"),
                    ("da", "ENABLE"),
                    ("da", "READONLY"),
                ],
                "FUNCTION-NAME": [
                    ("a", "EDITABLE"),
                    ("a", "IMPLEMENTATIONCONFIGCLASS"),
                    ("a", "OPTIONAL"),
                    ("a", "ORIGIN"),
                    ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                    ("a", "POSTBUILDVARIANTVALUE"),
                    ("a", "READONLY"),
                    ("a", "SCOPE"),
                    ("a", "SYMBOLICNAMEVALUE"),
                    ("a", "VISIBLE"),
                    ("da", "DEFAULT"),
                    ("da", "EDITABLE"),
                    ("da", "ENABLE"),
                    ("da", "INVALID"),
                ],
            }
            allowed_attrs = type_optional_attrs[input_type]
            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[7] if len(args) > 7 else []),
                allowed_attrs,
            )
            # 强制赋值
            kwargs["type"] = input_type
            kwargs["is_label"] = is_label
            return XdmA.InputBox.MetaData(*args, **kwargs)

    class CheckBox:
        """勾选框组件 (v:var BOOLEAN)"""

        @dataclass
        class MetaData(MetaBase):
            name: str
            desc_attr_xml: XmlNode.MetaData
            label_attr_xml: XmlNode.MetaData
            uuid_attr_xml: XmlNode.MetaData
            default_attr_xml: XmlNode.MetaData
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)
            is_label: bool = False  # 是否为标签

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.CheckBox.MetaData":
            # 可选属性区分
            BOOLEAN_OPTIONAL_ATTRS = [
                ("a", "EDITABLE"),
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "INVALID"),
                ("a", "OPTIONAL"),
                ("a", "ORIGIN"),
                ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                ("a", "POSTBUILDVARIANTVALUE"),
                ("a", "READONLY"),
                ("a", "SCOPE"),
                ("a", "SYMBOLICNAMEVALUE"),
                ("a", "VISIBLE"),
                ("da", "DEFAULT"),
                ("da", "EDITABLE"),
                ("da", "ENABLE"),
                ("da", "INVALID"),
                ("da", "READONLY"),
                ("da", "VISIBLE"),
                ("da", "WARNING"),
            ]

            BOOLEAN_LABEL_OPTIONAL_ATTRS = [
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "ORIGIN"),
                ("a", "SCOPE"),
                ("a", "SYMBOLICNAMEVALUE"),
                ("a", "VISIBLE"),
                ("da", "DEFAULT"),
            ]

            if kwargs.get("is_label", args[6] if len(args) > 6 else False):
                allowed_attrs = BOOLEAN_LABEL_OPTIONAL_ATTRS
            else:
                allowed_attrs = BOOLEAN_OPTIONAL_ATTRS

            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[6] if len(args) > 6 else []),
                allowed_attrs,
            )
            return XdmA.CheckBox.MetaData(*args, **kwargs)

    class ReferenceBox:
        """Xdm Reference Information (for v:var REFERENCE、SYMBOLIC-NAME-REFERENCE、CHOICE-REFERENCE、FOREIGN-REFERENCE)"""

        @dataclass
        class MetaData(MetaBase):
            name: str
            type: str
            desc_attr_xml: XmlNode.MetaData
            label_attr_xml: XmlNode.MetaData
            uuid_attr_xml: XmlNode.MetaData
            ref_attr_xml: XmlNode.MetaData
            additional_attributes: List[XmlNode.MetaData] = field(default_factory=list)

        @staticmethod
        def create(
            context: UserFunctionContext, *args, **kwargs
        ) -> "XdmA.ReferenceBox.MetaData":
            """Create a ReferenceBox metadata node"""
            allowed_types = [
                "REFERENCE",
                "SYMBOLIC-NAME-REFERENCE",
                "CHOICE-REFERENCE",
                "FOREIGN-REFERENCE",
            ]
            ref_type = kwargs.get("type", args[1] if len(args) > 1 else None)

            if ref_type not in allowed_types:
                raise ValueError(
                    f"Unsupported ReferenceBox type: {ref_type}. Allowed types: {allowed_types}"
                )
            # Check additional attributes
            # 可选属性
            OPTIONAL_ATTRS = [
                ("a", "EDITABLE"),
                ("a", "IMPLEMENTATIONCONFIGCLASS"),
                ("a", "INVALID"),
                ("a", "LABEL"),
                ("a", "OPTIONAL"),
                ("a", "ORIGIN"),
                ("a", "POSTBUILDVARIANTMULTIPLICITY"),
                ("a", "POSTBUILDVARIANTVALUE"),
                ("a", "REQUIRES-INDEX"),
                ("a", "READONLY"),
                ("a", "SCOPE"),
                ("a", "VISIBLE"),
                ("da", "EDITABLE"),
                ("da", "ENABLE"),
                ("da", "INVALID"),
                ("da", "RANGE"),
                ("da", "READONLY"),
            ]
            XdmA._check_attributes(
                kwargs.get("additional_attributes", args[5] if len(args) > 5 else []),
                OPTIONAL_ATTRS,
            )
            return XdmA.ReferenceBox.MetaData(*args, **kwargs)
