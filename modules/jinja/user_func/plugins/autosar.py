from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any

from modules.jinja.user_func.plugins.c import CPlugin

class AutosarPlugin(FunctionPlugin):
    """Autosar模板插件"""

    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:

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
            base, ext = os.path.splitext(file_name)
            prefix = base.upper()
            suffix = "_C" if ext == ".c" else ""
            version_info = {
                "macros": [
                    CPlugin.macro_define_init(context, f"{prefix}_VENDER_ID{suffix}", str(vender_id)),
                    CPlugin.macro_define_init(context, f"{prefix}_AR_RELEASE_MAJOR_VERSION{suffix}", str(autosar_release_major_version)),
                    CPlugin.macro_define_init(context, f"{prefix}_AR_RELEASE_MINOR_VERSION{suffix}", str(autosar_release_minor_version)),
                    CPlugin.macro_define_init(context, f"{prefix}_AR_RELEASE_REVISION_VERSION{suffix}", str(autosar_release_revision_version)),
                    CPlugin.macro_define_init(context, f"{prefix}_SW_MAJOR_VERSION{suffix}", str(software_major_version)),
                    CPlugin.macro_define_init(context, f"{prefix}_SW_MINOR_VERSION{suffix}", str(software_minor_version)),
                    CPlugin.macro_define_init(context, f"{prefix}_SW_PATCH_VERSION{suffix}", str(software_revision_version)),
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
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
