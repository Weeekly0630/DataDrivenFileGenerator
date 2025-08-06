from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase


class CPlugin(FunctionPlugin):
    class CFunction:
        @dataclass
        class MetaData(MetaBase):
            name: str
            return_type: Union[str, "CPlugin.CTypeDef.MetaData"]
            params: List["CPlugin.CVariable.MetaData"] = field(default_factory=list)
            storage: str = ""
            qualifiers: str = ""
            is_inline: bool = False
            is_static: bool = False
            is_extern: bool = False
            body: str = ""

        """C语言函数信息"""

        @staticmethod
        def c_function_info_create(
            context: UserFunctionContext,
            name: str,
            return_type: Union[str, "CPlugin.CTypeDef.MetaData"],
            params: List["CPlugin.CVariable.MetaData"] = [],
            storage: str = "",
            qualifiers: str = "",
            is_inline: bool = False,
            is_static: bool = False,
            is_extern: bool = False,
            body: str = "",
        ) -> "CPlugin.CFunction.MetaData":
            return CPlugin.CFunction.MetaData(
                name=name,
                return_type=return_type,
                params=params,
                storage=storage,
                qualifiers=qualifiers,
                is_inline=is_inline,
                is_static=is_static,
                is_extern=is_extern,
                body=body,
            )

    class CVariable:
        @dataclass
        class MetaData(MetaBase):
            name: str
            type: Union[str, "CPlugin.CTypeDef.MetaData"]
            storage: str = ""
            is_pointer: bool = False
            is_array: bool = False
            array_size: str = ""
            init_value: str = ""
            qualifiers: str = ""

        """C语言变量信息"""

        @staticmethod
        def c_variable_info_create(
            context: UserFunctionContext,
            name: str,
            type: Union[str, "CPlugin.CTypeDef.MetaData"],
            storage: str = "",
            is_pointer: bool = False,
            is_array: bool = False,
            array_size: str = "",
            init_value: str = "",
            qualifiers: str = "",
        ) -> "CPlugin.CVariable.MetaData":
            return CPlugin.CVariable.MetaData(
                name=name,
                type=type,
                storage=storage,
                is_pointer=is_pointer,
                is_array=is_array,
                array_size=array_size,
                init_value=init_value,
                qualifiers=qualifiers,
            )

    class CTypeDef:
        @dataclass
        class MetaData(MetaBase):
            name: str
            original_type: str
            is_pointer: bool = False
            qualifiers: str = ""

            def __str__(self) -> str:
                return self.name
            
        @staticmethod
        def c_typedef_info_create(
            context: UserFunctionContext,
            name: str,
            original_type: str,
            is_pointer: bool = False,
            qualifiers: str = "",
        ) -> "CPlugin.CTypeDef.MetaData":
            return CPlugin.CTypeDef.MetaData(
                name=name,
                original_type=original_type,
                is_pointer=is_pointer,
                qualifiers=qualifiers,
            )

    class CInclude:
        @dataclass
        class MetaData(MetaBase):
            file_name: str
            is_system: bool = False

        """C语言头文件信息"""

        @staticmethod
        def c_include_info_create(
            context: UserFunctionContext,
            file_name: str,
            is_system: bool = False,
        ) -> "CPlugin.CInclude.MetaData":
            return CPlugin.CInclude.MetaData(
                file_name=file_name,
                is_system=is_system,
            )

        @staticmethod
        def c_include_info_validator() -> UserFunctionValidator:
            validator = UserFunctionValidator()
            validator.add_param_check_validator(1, 2)
            return validator

    class CDefine:
        @dataclass
        class MetaData(MetaBase):
            name: str
            args: list = field(default_factory=list)
            value: str = ""

        """C语言宏定义信息"""

        @staticmethod
        def c_define_info_create(
            context: UserFunctionContext,
            name: str,
            args: List[str],
            value: str,
        ) -> "CPlugin.CDefine.MetaData":
            return CPlugin.CDefine.MetaData(
                name=name,
                args=args,
                value=value,
            )

        @staticmethod
        def c_define_info_validator() -> UserFunctionValidator:
            validator = UserFunctionValidator()
            validator.add_param_check_validator(3, 3)
            return validator

    class CMacroIf:
        @dataclass
        class MetaData(MetaBase):
            condition: str
            content: str
            else_objects: list = field(default_factory=list)

        """C语言条件编译宏信息"""

        @staticmethod
        def c_macro_if_info_create(
            context: UserFunctionContext,
            condition: str,
            content: str,
            else_objects: List[Dict[str, str]] = [],
        ) -> "CPlugin.CMacroIf.MetaData":
            return CPlugin.CMacroIf.MetaData(
                condition=condition,
                content=content,
                else_objects=else_objects,
            )

        @staticmethod
        def c_macro_if_info_validator() -> UserFunctionValidator:
            validator = UserFunctionValidator()
            validator.add_param_check_validator(2, 3)

            def check_else_objects(
                condition: str, content: str, else_objects: List[Dict[str, str]]
            ) -> bool:
                if not isinstance(else_objects, list):
                    raise ValueError("else_objects must be a list")
                for obj in else_objects:
                    if not isinstance(obj, dict):
                        raise ValueError("Each else_object must be a dictionary")
                    if "content" not in obj or "condition" not in obj:
                        raise ValueError(
                            "Each else_object must contain 'content' and 'condition' keys"
                        )

                return True

            # 添加对 else_objects 的验证
            validator.add_validator(check_else_objects)

            return validator

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return [
            UserFunctionInfo(
                name="c_define_info_create",
                description="Create a C define info object",
                handler=cls.CDefine.c_define_info_create,
                validator=cls.CDefine.c_define_info_validator(),
            ),
            UserFunctionInfo(
                name="c_include_info_create",
                description="Create a C include info object",
                handler=cls.CInclude.c_include_info_create,
                validator=cls.CInclude.c_include_info_validator(),
            ),
            UserFunctionInfo(
                name="c_macro_if_info_create",
                description="Create a C macro if info object",
                handler=cls.CMacroIf.c_macro_if_info_create,
                validator=cls.CMacroIf.c_macro_if_info_validator(),
            ),
            UserFunctionInfo(
                name="c_variable_info_create",
                description="Create a C variable info object",
                handler=cls.CVariable.c_variable_info_create,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
