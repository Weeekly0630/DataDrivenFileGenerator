from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Tuple
from modules.plugins.c import CPlugin
from modules.plugins.type import MetaBase
from dataclasses import dataclass, field, asdict


class AutosarPlugin(FunctionPlugin):
    """AUTOSAR插件，用于处理AUTOSAR相关的用户函数"""

    class AutosarCopyRight:
        @staticmethod
        def info_create(
            context: UserFunctionContext,
            autosar_version: str,
            autosar_revision: str,
            sw_version: str,
        ) -> Dict[str, Any]:
            return {
                "autosar_version": autosar_version,
                "autosar_revision": autosar_revision,
                "sw_version": sw_version,
            }

    class AutosarVersion:
        @dataclass
        class MetaData(MetaBase):
            # (VersionTag, VersionValue)
            vender_id: Tuple[str, int]
            module_id: Tuple[str, int]
            ar_release_major_version: Tuple[str, int]
            ar_release_minor_version: Tuple[str, int]
            ar_release_revision_version: Tuple[str, int]
            sw_major_version: Tuple[str, int]
            sw_minor_version: Tuple[str, int]
            sw_patch_version: Tuple[str, int]

        @staticmethod
        def get_version_tag(file_name: str) -> "AutosarPlugin.AutosarVersion.MetaData":
            prefix = file_name.split(".")[0].upper() + "_"
            suffix = "_C" if file_name.endswith(".c") else ""
            tag_list = [
                "VENDOR_ID",
                "MODULE_ID",
                "AR_RELEASE_MAJOR_VERSION",
                "AR_RELEASE_MINOR_VERSION",
                "AR_RELEASE_REVISION_VERSION",
                "SW_MAJOR_VERSION",
                "SW_MINOR_VERSION",
                "SW_PATCH_VERSION",
            ]

            return AutosarPlugin.AutosarVersion.MetaData(
                vender_id=(prefix + tag_list[0] + suffix, ),
                module_id=(prefix + tag_list[1] + suffix, ),
                ar_release_major_version=(prefix + tag_list[2] + suffix, ),
                ar_release_minor_version=(prefix + tag_list[3] + suffix, ),
                ar_release_revision_version=(prefix + tag_list[4] + suffix, ),
                sw_major_version=(prefix + tag_list[5] + suffix, ),
                sw_minor_version=(prefix + tag_list[6] + suffix, ),
                sw_patch_version=(prefix + tag_list[7] + suffix, ),
            )

        @staticmethod
        def info_create(
            context: UserFunctionContext,
            file_name: str,
            vender_id: int,
            module_id: int,
            ar_release_major_version: int,
            ar_release_minor_version: int,
            ar_release_revision_version: int,
            sw_major_version: int,
            sw_minor_version: int,
            sw_patch_version: int,
        ) -> List[CPlugin.CDefine.MetaData]:
            version_metadata: AutosarPlugin.AutosarVersion.MetaData = (
                AutosarPlugin.AutosarVersion.get_version_tag(file_name)
            )
            # bind version values to tags
            define_args = [
                (version_metadata.vender_id, vender_id),
                (version_metadata.module_id, module_id),
                (version_metadata.ar_release_major_version, ar_release_major_version),
                (version_metadata.ar_release_minor_version, ar_release_minor_version),
                (
                    version_metadata.ar_release_revision_version,
                    ar_release_revision_version,
                ),
                (version_metadata.sw_major_version, sw_major_version),
                (version_metadata.sw_minor_version, sw_minor_version),
                (version_metadata.sw_patch_version, sw_patch_version),
            ]

            return [
                CPlugin.CDefine.c_define_info_create(
                    context,
                    name=define_info[0],
                    args=[],
                    value=str(define_info[1]),
                )
                for define_info in define_args
            ]

        @staticmethod
        def info_validator() -> UserFunctionValidator:
            validator = UserFunctionValidator()
            validator.add_param_check_validator(1, 1)

            def file_name_validator(
                file_name: str,
            ) -> bool:
                if file_name.endswith(".c") or file_name.endswith(".h"):
                    return True
                else:
                    raise ValueError("File name must end with .c or .h")

            validator.add_validator(file_name_validator)

            return validator

    class AutosarVersionCheck:
        """
        /* Check if current file and I2c_Cfg header file are of the same vendor */
        #if (I2C_TYPES_VENDOR_ID != I2C_VENDOR_ID_CFG)
            #error "I2c_Types.h and CDD_I2c_Cfg.h have different vendor ids"
        #endif
        /* Check if current file and I2c_Cfg header file are of the same Autosar version */
        #if ((I2C_TYPES_AR_RELEASE_MAJOR_VERSION != I2C_AR_RELEASE_MAJOR_VERSION_CFG) ||    \
            (I2C_TYPES_AR_RELEASE_MINOR_VERSION != I2C_AR_RELEASE_MINOR_VERSION_CFG) ||    \
            (I2C_TYPES_AR_RELEASE_REVISION_VERSION != I2C_AR_RELEASE_REVISION_VERSION_CFG) \
            )
            #error "AutoSar Version Numbers of I2c_Types.h and CDD_I2c_Cfg.h are different"
        #endif
        /* Check if current file and I2c_Cfg header file are of the same Software version */
        #if ((I2C_TYPES_SW_MAJOR_VERSION != I2C_SW_MAJOR_VERSION_CFG) || \
            (I2C_TYPES_SW_MINOR_VERSION != I2C_SW_MINOR_VERSION_CFG) || \
            (I2C_TYPES_SW_PATCH_VERSION != I2C_SW_PATCH_VERSION_CFG)    \
            )
        #error "Software Version Numbers of I2c_Types.h and CDD_I2c_Cfg.h are different"
        #endif
        """

        @staticmethod
        def info_create(
            context: UserFunctionContext,
            file_name: str,
            target_file_arg_list: List[Tuple[str, bool, bool, bool]],
        ) -> List[Dict[str, Any]]:
            result: List[Dict[str, Any]] = []
            # 1. get version tags for current file
            cur_tags: List[str] = AutosarPlugin.AutosarVersion.get_version_tag(
                file_name
            )
            for target_file_arg in target_file_arg_list:
                target_file_name, vender_en, ar_en, sw_en = target_file_arg

                # 2. generate version check macros
                if vender_en or ar_en or sw_en:
                    target_tags: List[str] = (
                        AutosarPlugin.AutosarVersion.get_version_tag(target_file_name)
                    )
                if vender_en:
                    # 2.1 vendor id check
                    result.append(
                        CPlugin.CMacroIf.c_macro_if_info_create(
                            context=context,
                            condition=f"({cur_tags[0]} != {target_tags[0]})",
                            content=f'#error "{file_name} and {target_file_name} have different vendor ids"',
                        )
                    )
                if ar_en:
                    # 2.2 ar version check
                    result.append(
                        CPlugin.CMacroIf.c_macro_if_info_create(
                            context=context,
                            condition=" || \\\n    ".join(
                                [
                                    f"({cur_tags[i]} != {target_tags[i]})"
                                    for i in range(1, 4)
                                ]
                            ),
                            content=f'#error "AutoSar Version Numbers of {file_name} and {target_file_name} are different"',
                        )
                    )
                if sw_en:
                    # 2.3 sw version check
                    result.append(
                        CPlugin.CMacroIf.c_macro_if_info_create(
                            context=context,
                            condition=" || \\\n    ".join(
                                [
                                    f"({cur_tags[i]} != {target_tags[i]})"
                                    for i in range(4, 7)
                                ]
                            ),
                            content=f'#error "Software Version Numbers of {file_name} and {target_file_name} are different"',
                        )
                    )

            return result

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return [
            UserFunctionInfo(
                name="autosar_copy_right_info_create",
                description="Create AUTOSAR copyright information",
                handler=cls.AutosarCopyRight.info_create,
            ),
            UserFunctionInfo(
                name="autosar_version_info_create",
                description="Create AUTOSAR version information",
                handler=cls.AutosarVersion.info_create,
                # validator=cls.AutosarVersion.info_validator(),
            ),
            UserFunctionInfo(
                name="autosar_version_check_info_create",
                description="Create AUTOSAR version check information",
                handler=cls.AutosarVersionCheck.info_create,
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
