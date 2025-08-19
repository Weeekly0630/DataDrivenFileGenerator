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

from modules.utils.type_classes.xml import XmlNode

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
            name = name.strip().lower().replace('-', '_')
            generator = getattr(XdmAttribute, f"create_{name}", None)
            if not generator:
                raise ValueError(f"Unsupported Xdm Attribute: {name}")
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
    def create_uuid(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a UUID attribute node"""
        # Check if the required metadata is present
        if "value" not in metadata:
            raise ValueError("UUID metadata must contain 'value' key")
        if "namespace" not in metadata:
            raise ValueError("UUID metadata must contain 'namespace' key")

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace=metadata["namespace"],
            attributes={
                "name": "UUID",
                "value": metadata["value"],
            },
            tag="a",
            children=[],
        )
        return node


class XdmA:
    """Xdm Advanced Model"""

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
            refind_module_def_value: str

            @staticmethod
            def create(
                context: UserFunctionContext,
                name: str,
                release_attr_xml: XmlNode.MetaData,
                admin_data_attr_xml: XmlNode.MetaData,
                postbuildvariantsupport_attr_xml: XmlNode.MetaData,
                desc_attr_xml: XmlNode.MetaData,
                lower_multiplicity_attr_xml: XmlNode.MetaData,
                upper_multiplicity_attr_xml: XmlNode.MetaData,
                uuid_attr_xml: XmlNode.MetaData,
                refind_module_def_value: str,
            ) -> "XdmA.ModuleDefBlock.MetaData": ...
    class EcuParamDefBlock:
        @dataclass
        class MetaData(MetaBase): ...

    class BswModuleDescBlock:
        @dataclass
        class MetaData(MetaBase): ...

    class Table:
        """Xdm Table Information"""

        @dataclass
        class MetaData(MetaBase): ...

    class TableRow:
        """Xdm Table Row Information"""

        @dataclass
        class MetaData(MetaBase): ...

    class Field:
        """Xdm Field Information"""

        @dataclass
        class MetaData(MetaBase): ...

    class FieldMeta:
        """Xdm Field Metadata Information"""

        @dataclass
        class MetaData(MetaBase): ...

    class ReferenceField:
        @dataclass
        class MetaData(MetaBase): ...

# TODO:
## a/da 直接使用文档中的值
"""
- 下拉
- 输入
- 勾选
- 表
"""