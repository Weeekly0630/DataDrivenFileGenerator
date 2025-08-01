from modules.core import DataHandler
from modules.core.user_function_resolver import UserFunctionInfo, UserFunctionContext, FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Any, Tuple

class AutosarPlugin(FunctionPlugin):
    """Autosar模板插件，提供AUTOSAR相关的Jinja用户函数"""


    @staticmethod
    def version_check_info_init(
        context: UserFunctionContext,
        current_file_name: str,
        reference_file_name_list: List[str],
    ) -> Any:
        """
        初始化Autosar版本检查信息数据结构。

        Args:
            context: 用户函数上下文
            current_file_name: 当前文件名
            reference_file_name: 参考文件名

        Returns:
            dict: 包含三组条件和内容的宏结构
        """
        from modules.plugins.c import CPlugin
        current_file_name = context.cur_node.data.get("file_name", current_file_name)
        def _version(file_name: str) -> Tuple[str, str]:
            base, ext = file_name.rsplit(".", 1)
            prefix = base.upper()
            suffix = "_C" if ext == "c" else ""
            return (prefix, suffix)

        def vender_id_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_VENDOR_ID{suffix}"

        def ar_release_major_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_AR_RELEASE_MAJOR_VERSION{suffix}"

        def ar_release_minor_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_AR_RELEASE_MINOR_VERSION{suffix}"

        def ar_release_revision_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_AR_RELEASE_REVISION_VERSION{suffix}"

        def sw_major_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_SW_MAJOR_VERSION{suffix}"

        def sw_minor_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_SW_MINOR_VERSION{suffix}"

        def sw_patch_version_macro(prefix: str, suffix: str) -> str:
            return f"{prefix}_SW_PATCH_VERSION{suffix}"
        
        # 标准文件版本比较特殊
        skip_compare_headers = ("Dem.h", "Det.h", "Std_Types.h", "StdRegMacros.h")
        results = []
        for reference_file_name in reference_file_name_list:
            cur_prefix, cur_suffix = _version(current_file_name)
            ref_prefix, ref_suffix = _version(reference_file_name)
            if reference_file_name in skip_compare_headers:
                # 仅进行Autosar版本检查，不进行供应商ID和软件版本检查，同时prefix进行映射处理
                prefix_mapping = {
                    "Dem.h": "DEM",
                    "Det.h": "DET",
                    "Std_Types.h": "STD_TYPES",
                    "StdRegMacros.h": "STD_REG_MACROS",
                }
                results.append({
                "vender": CPlugin.macro_if_info_init(
                    context=context,
                    conditions=[],
                    contents=[],
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
                "sw": CPlugin.macro_if_info_init(
                    context=context,
                    conditions=[],
                    contents=[],
                ),
            })
                continue
            
            results.append({
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
            })
        return results


    @staticmethod
    def version_info_init(
        context: UserFunctionContext,
        file_name: str = "",
        vender_id: int = -1,
        autosar_release_major_version: int = -1,
        autosar_release_minor_version: int = -1,
        autosar_release_revision_version: int = -1,
        software_major_version: int = -1,
        software_minor_version: int = -1,
        software_revision_version: int = -1,
    ) -> Any:
        """
        初始化Autosar版本信息数据结构, 用于存储指定文件的Autosar版本信息。

        Args:
            context: 用户函数上下文
            file_name: 文件名
            vender_id: 供应商ID
            autosar_release_major_version: AUTOSAR主版本号
            autosar_release_minor_version: AUTOSAR次版本号
            autosar_release_revision_version: AUTOSAR修订版本号
            software_major_version: 软件主版本号
            software_minor_version: 软件次版本号
            software_revision_version: 软件修订版本号

        Returns:
            dict: 包含所有版本相关宏定义的数据结构
        """
        from modules.plugins.c import CPlugin
        file_name = context.cur_node.data.get("file_name", file_name)
        vender_id = context.cur_node.data.get("vender_id", vender_id)
        autosar_release_major_version = context.cur_node.data.get(
            "autosar_release_major_version", autosar_release_major_version
        )
        autosar_release_minor_version = context.cur_node.data.get(
            "autosar_release_minor_version", autosar_release_minor_version
        )
        autosar_release_revision_version = context.cur_node.data.get(
            "autosar_release_revision_version", autosar_release_revision_version
        )
        software_major_version = context.cur_node.data.get(
            "software_major_version", software_major_version
        )
        software_minor_version = context.cur_node.data.get(
            "software_minor_version", software_minor_version
        )
        software_revision_version = context.cur_node.data.get(
            "software_revision_version", software_revision_version
        )
        prefix, suffix = file_name.rsplit(".", 1)
        prefix = prefix.upper()
        suffix = "_C" if suffix == "c" else ""
        return {
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


    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:
        """
        返回所有可用的AUTOSAR用户函数信息。
        """
        return [
            UserFunctionInfo(
                name="autosar:version_info_init",
                description="初始化Autosar版本信息数据结构",
                handler=cls.version_info_init,
            ),
            UserFunctionInfo(
                name="autosar:version_check_info_init",
                description="初始化Autosar版本检查信息数据结构",
                handler=cls.version_check_info_init,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
