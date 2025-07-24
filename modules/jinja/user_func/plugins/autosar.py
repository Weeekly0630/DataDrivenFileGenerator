from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any, Tuple

from modules.jinja.user_func.plugins.c import CPlugin


class AutosarPlugin(FunctionPlugin):
    """Autosar模板插件"""

    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:

        def _version(file_name: str) -> Tuple[str, str]:
            """根据文件名生成版本前缀"""
            base, ext = file_name.rsplit(".", 1)
            prefix = base.upper()
            suffix = "_C" if ext == "c" else ""
            return (prefix, suffix)

        def version_check_info_init(
            context: UserFunctionContext,
            current_file_name: str,
            reference_file_name: str,
        ) -> Any:
            """初始化Autosar版本检查信息数据结构"""

            def vender_id_macro(prefix: str, suffix: str) -> str:
                """生成Vender ID宏名称"""
                return f"{prefix}_VENDOR_ID{suffix}"

            def ar_release_major_version_macro(prefix: str, suffix: str) -> str:
                """生成AR Release Major Version宏名称"""
                return f"{prefix}_AR_RELEASE_MAJOR_VERSION{suffix}"

            def ar_release_minor_version_macro(prefix: str, suffix: str) -> str:
                """生成AR Release Minor Version宏名称"""
                return f"{prefix}_AR_RELEASE_MINOR_VERSION{suffix}"

            def ar_release_revision_version_macro(prefix: str, suffix: str) -> str:
                """生成AR Release Revision Version宏名称"""
                return f"{prefix}_AR_RELEASE_REVISION_VERSION{suffix}"

            def sw_major_version_macro(prefix: str, suffix: str) -> str:
                """生成SW Major Version宏名称"""
                return f"{prefix}_SW_MAJOR_VERSION{suffix}"

            def sw_minor_version_macro(prefix: str, suffix: str) -> str:
                """生成SW Minor Version宏名称"""
                return f"{prefix}_SW_MINOR_VERSION{suffix}"

            def sw_patch_version_macro(prefix: str, suffix: str) -> str:
                """生成SW Patch Version宏名称"""
                return f"{prefix}_SW_PATCH_VERSION{suffix}"

            cur_prefix, cur_suffix = _version(current_file_name)
            ref_prefix, ref_suffix = _version(reference_file_name)

            return {
                "vender": CPlugin.macro_if_info_init(
                    context=context,
                    conditions=[
                        f"({vender_id_macro(cur_prefix, cur_suffix)} != {vender_id_macro(ref_prefix, ref_suffix)})"
                    ],
                    contents=[
                        f'#error "{current_file_name} and {reference_file_name} have different vendor ids"\n'
                    ],
                ),
                "ar": CPlugin.macro_if_info_init(
                    context=context,
                    conditions=[
                        f"""({ar_release_major_version_macro(cur_prefix, cur_suffix)} != {ar_release_major_version_macro(ref_prefix, ref_suffix)}) || \\
({ar_release_minor_version_macro(cur_prefix, cur_suffix)} != {ar_release_minor_version_macro(ref_prefix, ref_suffix)}) || \\
({ar_release_revision_version_macro(cur_prefix, cur_suffix)} != {ar_release_revision_version_macro(ref_prefix, ref_suffix)})""",
                    ],
                    contents=[
                        f'#error "AutoSar Version Numbers of {current_file_name} and {reference_file_name} are different"\n'
                    ],
                ),
                #                 "ar": {
                #                     "conditions": [
                #                         f"""({ar_release_major_version_macro(cur_prefix, cur_suffix)} != {ar_release_major_version_macro(ref_prefix, ref_suffix)}) || \\
                # ({ar_release_minor_version_macro(cur_prefix, cur_suffix)} != {ar_release_minor_version_macro(ref_prefix, ref_suffix)}) || \\
                # ({ar_release_revision_version_macro(cur_prefix, cur_suffix)} != {ar_release_revision_version_macro(ref_prefix, ref_suffix)})
                # """,
                #                     ],
                #                     "contents": [
                #                         f'#error "AutoSar Version Numbers of {current_file_name} and {reference_file_name} are different"'
                #                     ],
                #                     "else_content": None,
                #                 },
                "sw": CPlugin.macro_if_info_init(
                    context=context,
                    conditions=[
                        f"""({sw_major_version_macro(cur_prefix, cur_suffix)} != {sw_major_version_macro(ref_prefix, ref_suffix)}) || \\
({sw_minor_version_macro(cur_prefix, cur_suffix)} != {sw_minor_version_macro(ref_prefix, ref_suffix)}) || \\
({sw_patch_version_macro(cur_prefix, cur_suffix)} != {sw_patch_version_macro(ref_prefix, ref_suffix)})"""
                    ],
                    contents=[
                        f'#error "Software Version Numbers of {current_file_name} and {reference_file_name} are different"\n'
                    ],
                ),
                #     {
                #     "conditions":
                #     "contents":
                #     "else_content": None,
                # },
            }

        def version_info_init(
            context: UserFunctionContext,
            file_name: str,
            vender_id: int,
            autosar_release_major_version: int,
            autosar_release_minor_version: int,
            autosar_release_revision_version: int,
            software_major_version: int,
            software_minor_version: int,
            software_revision_version: int,
        ) -> Any:
            """初始化Autosar版本信息数据结构, 用于存储指定文件的Autosar版本信息"""
            import os

            prefix, suffix = _version(file_name)
            version_info = {
                "macros": [
                    CPlugin.macro_define_info_init(
                        context, f"{prefix}_VENDER_ID{suffix}", str(vender_id)
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_AR_RELEASE_MAJOR_VERSION{suffix}",
                        str(autosar_release_major_version),
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_AR_RELEASE_MINOR_VERSION{suffix}",
                        str(autosar_release_minor_version),
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_AR_RELEASE_REVISION_VERSION{suffix}",
                        str(autosar_release_revision_version),
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_SW_MAJOR_VERSION{suffix}",
                        str(software_major_version),
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_SW_MINOR_VERSION{suffix}",
                        str(software_minor_version),
                    ),
                    CPlugin.macro_define_info_init(
                        context,
                        f"{prefix}_SW_PATCH_VERSION{suffix}",
                        str(software_revision_version),
                    ),
                ],
            }
            return version_info

        return [
            UserFunctionInfo(
                name="autosar:version_info_init",
                arg_range=(8, 8),
                description="初始化Autosar版本信息数据结构",
                handler=version_info_init,
            ),
            UserFunctionInfo(
                name="autosar:version_check_info_init",
                arg_range=(2, 2),
                description="初始化Autosar版本检查信息数据结构",
                handler=version_check_info_init,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
