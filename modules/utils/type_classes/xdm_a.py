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
    def _init_implementationconfigclass_type(
        meta_data: Dict[str, Any],
    ) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'IMPLEMENTATIONCONFIGCLASS'
        metadata: {
            ...
            }
        """
        results: List[XmlNode.MetaData] = []
        meta: List[Dict[str, Any]]

        # Convert meta_data to List if not already
        if not isinstance(meta_data, List):
            meta = [meta_data]

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
    def _init_xpath_type(meta_data: Dict[str, Any]) -> List[XmlNode.MetaData]:
        """Initialize any attribute which has type 'XPath'
        metadata: {
            ...
            tst: # List of test conditions or single test condition
                -   expr: str,  # XPath expression
                    true: Optional[str],  # Value if true
                    false: Optional[str],  # Value if false
            ...
            }
        """
        results: List[XmlNode.MetaData] = []
        if "tst" not in meta_data:
            raise ValueError("XPath type metadata must contain 'tst' key")

        tst = meta_data["tst"]

        # Convert tst to List
        if not isinstance(tst, List):
            tst = [tst]
        for i, item in enumerate(tst):
            # Check if item is a dict
            if not isinstance(item, dict):
                raise ValueError(
                    f"metadata 'tst' item {i} must be a dict, got {type(item)}"
                )
            # Check if item has required keys
            if "expr" not in item:
                raise ValueError(f"metadata 'tst' item {i} must contain 'expr' key")
            expr = item["expr"]
            true = item.get("true")
            false = item.get("false")

            attributes = {
                "expr": expr,
            }
            if true is not None:
                attributes["true"] = true
            if false is not None:
                attributes["false"] = false

            results.append(
                XmlNode.MetaData(
                    namespace="a",
                    attributes=attributes,
                    tag="tst",
                )
            )
        return results

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
        if "value" not in metadata:
            raise ValueError("CALCULATION-FORMULA metadata must contain 'value' key")
        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "CALCULATION-FORMULA",
                "value": metadata["value"],
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
        if "value" not in metadata:
            raise ValueError("CALCULATION-LANGUAGE metadata must contain 'value' key")
        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "CALCULATION-LANGUAGE",
                "value": metadata["value"],
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
        if "value" not in metadata:
            raise ValueError("DERIVED metadata must contain 'value' key")

        value = metadata["value"]
        if isinstance(value, str):
            # Ensure the value is a boolean string
            if value.lower() not in ["true", "false"]:
                raise ValueError(
                    "DERIVED value must be a boolean string ('true' or 'false')"
                )
            value = value.lower() == "true"  # Convert to boolean

        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "DERIVED",
                "value": str(value).upper(),  # Ensure the value is in uppercase
            },
            tag="a",
            children=[],
        )

    # DESC
    @staticmethod
    def create_desc(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a DESC attribute node with a child <a:v>"""
        if "text" not in metadata:
            raise ValueError("DESC metadata must contain 'text' key")
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
                    text=metadata["text"],
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
        # Check if the required metadata is present
        if "type" not in metadata:
            raise ValueError("EDITABLE metadata must contain 'type' key")

        type_str = str(metadata["type"]).lower()

        if type_str not in ["true", "false", "xpath"]:
            raise ValueError("EDITABLE type must be 'true', 'false', or 'xpath'")

        # TODO: Use "a" or "da" tag?
        # Try to get namespace and attributes
        namespace = metadata.get("namespace", "a")  # Default to "a" namespace
        tag = metadata.get("tag", "a")  # Default to "a" tag

        node: XmlNode.MetaData

        if type_str == "xpath":  # XPATH
            tst_nodes: List[XmlNode.MetaData] = XdmAttribute._init_xpath_type(
                meta_data=metadata
            )

            node = XmlNode.MetaData(
                namespace=namespace,
                attributes={
                    "name": "EDITABLE",
                    "value": "XPath",
                },
                tag=tag,
                children=tst_nodes,
            )
        else:  # True or False
            if "value" not in metadata:
                raise ValueError(
                    "EDITABLE metadata with type 'true' or 'false' must contain 'value' key"
                )
            value = metadata["value"]
            node = XmlNode.MetaData(
                namespace=namespace,
                attributes={
                    "name": "EDITABLE",
                    "value": value,
                },
                tag=tag,
                children=[],
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
    # LABEL
    @staticmethod
    def create_label(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a LABEL attribute node"""
        # Check if the required metadata is present
        if "value" not in metadata:
            raise ValueError("LABEL metadata must contain 'value' key")
        return XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "LABEL",
                "value": metadata["value"],
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
        if "value" not in metadata:
            raise ValueError("LOWER-MULTIPLICITY metadata must contain 'value' key")
        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "LOWER-MULTIPLICITY",
                "value": metadata["value"],
            },
            tag="a",
            children=[],
        )
        return node

    # OPTIONAL
    # ORIGIN
    # POSTBUILDVARIANTSUPPORT
    @staticmethod
    def create_postbuildvariantsupport(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a POSTBUILDVARIANTSUPPORT attribute node"""
        if "value" not in metadata:
            raise ValueError(
                "POSTBUILDVARIANTSUPPORT metadata must contain 'value' key"
            )
        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "POSTBUILDVARIANTSUPPORT",
                "value": metadata["value"],
            },
            tag="a",
            children=[],
        )
        return node

    # POSTBUILDVARIANTMULTIPLICITY
    # POSTBUILDVARIANTVALUE
    # READONLY
    # SCOPE
    # SYMBOLICNAMEVALUE
    # UUID
    @staticmethod
    def create_uuid(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a UUID attribute node"""
        # Check if the required metadata is present
        if "value" not in metadata:
            raise ValueError("UUID metadata must contain 'value' key")

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace=metadata.get("namespace", "a"),  # Default to "a" namespace
            attributes={
                "name": "UUID",
                "value": metadata["value"],
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
        if "value" not in metadata:
            raise ValueError("UPPER-MULTIPLICITY metadata must contain 'value' key")
        node = XmlNode.MetaData(
            namespace="a",
            attributes={
                "name": "UPPER-MULTIPLICITY",
                "value": metadata["value"],
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
        if "value" not in metadata:
            raise ValueError("DEFAULT metadata must contain 'value' key")
        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace="a",  # metadata["namespace"],
            attributes={
                "name": "DEFAULT",
                "value": metadata["value"],
            },
            tag="a",
            children=[],
        )
        return node

    # EDITABLE
    # ENABLE
    # INVALID
    # OPTIONAL
    # RANGE
    @staticmethod
    def create_range(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a RANGE attribute node
        List of strings or list of xpath conditions"""
        type_str = metadata.get("type", "").lower()

        if type_str not in ["xpath", ""]:
            raise ValueError("RANGE type must be 'XPath' or omitted")

        if type_str == "xpath":
            # XPATH
            child_nodes: List[XmlNode.MetaData] = XdmAttribute._init_xpath_type(
                meta_data=metadata
            )
            node = XmlNode.MetaData(
                namespace="a",
                attributes={
                    "name": "RANGE",
                    "value": "XPath",
                },
                tag="da",
                children=child_nodes,
            )
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
                attributes={
                    "name": "RANGE",
                },
                tag="da",
                children=child_nodes,
            )
        return node

    # READONLY
    # RELEASE
    @staticmethod
    def create_release(
        context: UserFunctionContext, metadata: Dict[str, Any]
    ) -> XmlNode.MetaData:
        """Create a Release attribute node"""
        # Check if the required metadata is present
        if "value" not in metadata:
            raise ValueError("Release metadata must contain 'value' key")

        # Create the XML node with the provided metadata
        node = XmlNode.MetaData(
            namespace="a",  # metadata["namespace"],
            attributes={
                "name": "RELEASE",
                "value": metadata["value"],
            },
            tag="a",
            children=[],
        )
        return node

    # WARNING
    # WIDTH


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
            #
            refind_module_def_value: str
        # @staticmethod
        # def create(
        #     context: UserFunctionContext,
        #     name: str,
        #     release_attr_xml: XmlNode.MetaData,
        #     admin_data_attr_xml: XmlNode.MetaData,
        #     postbuildvariantsupport_attr_xml: XmlNode.MetaData,
        #     desc_attr_xml: XmlNode.MetaData,
        #     lower_multiplicity_attr_xml: XmlNode.MetaData,
        #     upper_multiplicity_attr_xml: XmlNode.MetaData,
        #     uuid_attr_xml: XmlNode.MetaData,
        #     refind_module_def_value: str,
        # ) -> "XdmA.ModuleDefBlock.MetaData": ...

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
