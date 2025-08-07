from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any

class TemplatePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""
    
    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """
        自动注册机制说明：
        1. 自动递归遍历 TemplatePlugin 及其所有嵌套类，收集所有以 _create 结尾的静态方法。
        2. 自动查找同名 _validator 方法（只在 TemplatePlugin 本身查找），如有则注册为 validator。
        3. 注册时函数名为 "templateplugin_嵌套类名_方法名"，保证唯一性。
        4. 支持多级嵌套，新增类型无需修改注册逻辑。
        5. validator 必须为 UserFunctionValidator 实例或 None。
        """
        info_funcs = []

        def register_create_functions(obj, prefix=cls.__name__.lower() + "_"):
            for name in dir(obj):
                if name.startswith("__") and name.endswith("__"):
                    continue  # 跳过内置属性
                try:
                    attr = getattr(obj, name)
                except Exception:
                    continue  # 跳过无法 getattr 的属性
                if callable(attr) and name.endswith("_create"):
                    validator_name = name.replace("_create", "_validator")
                    validator = getattr(cls, validator_name, None)
                    if callable(validator):
                        validator_instance = validator()
                    else:
                        validator_instance = validator
                    if (
                        isinstance(validator_instance, UserFunctionValidator)
                        or validator_instance is None
                    ):
                        info_funcs.append(
                            UserFunctionInfo(
                                name=f"{prefix}{name}" if prefix else name,
                                handler=attr,
                                validator=validator_instance,
                                description=attr.__doc__ or "",
                            )
                        )
                    else:
                        raise TypeError(
                            f"Validator for {prefix}{name} is not a UserFunctionValidator instance or None."
                        )
                elif isinstance(attr, type):
                    register_create_functions(attr, prefix=f"{prefix}{attr.__name__.lower()}_")

        register_create_functions(cls)
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
