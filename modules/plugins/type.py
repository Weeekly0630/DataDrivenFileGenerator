from dataclasses import dataclass, field, asdict
from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
    UserFunctionHandlerType,
)
from typing import List, Union, Any, Callable, Dict, Tuple


class MetaBase:
    def to_dict(self):
        return asdict(self)

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class FunctionCallInfo:
    name: str
    args: List[str] = field(default_factory=list)


def auto_register_factories(cls) -> List[UserFunctionInfo]:
    info_funcs: List[UserFunctionInfo] = []
    function_call_info_dict: Dict[str, FunctionCallInfo] = {}

    def get_function_name(attr_name: str) -> str:
        return f"{cls.__name__.lower()}_{attr_name.lower()}_create"
    
    # 遍历类的所有属性
    for attr_name in dir(cls):
        if attr_name.startswith("__") and attr_name.endswith("__"):
            # Skip built-in attributes
            continue

        try:
            attr = getattr(cls, attr_name)
        except Exception:
            # Unable to getattr, skip this attribute
            continue

        if isinstance(attr, type) and hasattr(attr, "MetaData"):

            def field_metadata(subcls) -> Dict:
                return subcls.MetaData.__dataclass_fields__

            # Find nested classes with MetaData
            def gather_functions(
                subcls, metadata_fields: List
            ) -> Tuple[UserFunctionHandlerType, Union[UserFunctionValidator, None]]:
                args: List[str] = []
                nonlocal function_name
                
                if hasattr(subcls, "create"):
                    handler = getattr(subcls, "create")
                    # 只在子类中查找 validator，不自动创建
                    if hasattr(subcls, "validator") and callable(
                        getattr(subcls, "validator")
                    ):
                        validator = getattr(subcls, "validator")()
                    
                else:
                    # 用 *args 按字段顺序传参
                    handler = lambda *args, **kwargs: subcls.MetaData(
                        **{k: v for k, v in zip(metadata_fields, args)}, **kwargs
                    )
                    # 自动创建 validator
                    validator = UserFunctionValidator()
                    # 参数数量等于字段数量
                    validator.add_param_check_validator(
                        min_args=len(metadata_fields), max_args=len(metadata_fields)
                    )

                # 注册函数调用信息
                function_call_info_dict[function_name] = FunctionCallInfo(
                    name=function_name, args=args
                )
                return (handler, validator)

            def gather_description(subcls) -> str:
                if subcls.MetaData.__doc__:
                    return subcls.MetaData.__doc__
                else:
                    return f"自动生成的{attr.MetaData.__name__}工厂函数"

            def register_function_call_template(
                func_name: str,
            ):
                """注册函数调用模板"""

            function_name = get_function_name(attr_name)
            metadata_fields = field_metadata(attr)
            handler, validator = gather_functions(attr, metadata_fields)
            description = gather_description(attr)

            info_funcs.append(
                UserFunctionInfo(
                    name=function_name,
                    handler=handler,
                    validator=validator,
                    description=description,
                )
            )

    return info_funcs
