from dataclasses import dataclass, field, asdict
from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
    UserFunctionHandlerType,
)
from typing import List, Union, Any, Callable, Dict, Tuple, Set, Optional


class MetaBase:
    def to_dict(self):
        return asdict(self)

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class FunctionCallInfo:
    name: str
    args: List[Any] = field(default_factory=list)


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

            def field_metadata(subcls) -> List[str]:
                # 返回字段名列表而不是字段对象字典
                return list(subcls.MetaData.__dataclass_fields__.keys())

            # Find nested classes with MetaData
            def gather_functions(
                subcls, metadata_fields: List[str], func_name: str
            ) -> Tuple[UserFunctionHandlerType, Union[UserFunctionValidator, None]]:
                
                if hasattr(subcls, "create"):
                    handler = getattr(subcls, "create")
                    # 只在子类中查找 validator，不自动创建
                    if hasattr(subcls, "validator") and callable(
                        getattr(subcls, "validator")
                    ):
                        validator = getattr(subcls, "validator")()
                    else:
                        validator = None
                    
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

                # 注册函数调用信息 - 使用传入的func_name
                function_call_info_dict[func_name] = FunctionCallInfo(
                    name=func_name, args=metadata_fields
                )
                return (handler, validator)

            def gather_description(subcls) -> str:
                if subcls.MetaData.__doc__:
                    return subcls.MetaData.__doc__
                else:
                    return f"自动生成的{subcls.MetaData.__name__}工厂函数"

            function_name = get_function_name(attr_name)
            metadata_fields = field_metadata(attr)
            handler, validator = gather_functions(attr, metadata_fields, function_name)
            description = gather_description(attr)

            info_funcs.append(
                UserFunctionInfo(
                    name=function_name,
                    handler=handler,
                    validator=validator,
                    description=description,
                )
            )

    def analyze_parameter_types(func_info: FunctionCallInfo) -> Dict[str, str]:
        """
        分析参数类型，区分 Python 基本类型和 Plugin 自定义类型
        
        Returns:
            Dict[str, str]: 参数名 -> 类型描述的映射
        """
        param_types = {}
        
        for arg in func_info.args:
            # 检查是否有对应的 Plugin 函数
            corresponding_func = None
            for func_name in function_call_info_dict.keys():
                # 检查参数名与函数名的匹配关系
                if (arg in ["type", "ref", "typeref"] and "typeref" in func_name) or \
                   (arg == "modifier" and "typemodifier" in func_name) or \
                   (arg == "fields" and "field" in func_name) or \
                   (arg == "attributes" and "attr" in func_name):
                    corresponding_func = func_name
                    break
            
            if corresponding_func:
                # Plugin 自定义类型，添加锚点链接
                anchor = corresponding_func.replace("_", "-")
                param_types[arg] = f"[{corresponding_func}](#{anchor})"
            else:
                # Python 基本类型，根据参数名推断类型
                if arg == "name":
                    param_types[arg] = "`str` - 名称字符串"
                elif arg in ["qualifiers"]:
                    param_types[arg] = "`str` - 限定符字符串"
                elif arg in ["fields", "attributes", "array_dims"]:
                    param_types[arg] = "`List` - 列表类型"
                elif arg in ["is_pointer", "is_array"]:
                    param_types[arg] = "`bool` - 布尔值"
                elif arg in ["pointer_level", "bitfield_width"]:
                    param_types[arg] = "`int` - 整数值"
                elif arg == "init_expr":
                    param_types[arg] = "`Any` - 初始化表达式"
                else:
                    param_types[arg] = "`Any` - 任意类型"
        
        return param_types

    def generate_simple_template(func_name: str, func_info: FunctionCallInfo) -> str:
        """
        生成简单的顶层函数调用模板（不递归）
        """
        if len(func_info.args) == 0:
            return f"{func_name}()"
        elif len(func_info.args) <= 2:
            # 简单参数，一行显示
            args_str = ", ".join([f"<{arg}_value>" for arg in func_info.args])
            return f"{func_name}({args_str})"
        else:
            # 多参数，多行显示
            template = f"{func_name}(\n"
            for i, arg in enumerate(func_info.args):
                template += f"    <{arg}_value>"
                if i < len(func_info.args) - 1:
                    template += ","
                template += "\n"
            template += ")"
            return template

    def print_function_templates_markdown() -> None:
        """
        打印所有函数的调用模板（Markdown格式，带锚点）
        """
        print("# 函数调用模板文档\n")
        print("本文档列出了所有可用的函数及其调用模板。\n")
        
        # 生成目录
        print("## 目录\n")
        for func_name in function_call_info_dict.keys():
            anchor = func_name.replace("_", "-")
            print(f"- [{func_name}](#{anchor})")
        print("\n---\n")
        
        # 生成函数详情
        for func_name, func_info in function_call_info_dict.items():
            anchor = func_name.replace("_", "-")
            print(f"## {func_name} {{#{anchor}}}\n")
            
            # 分析参数类型
            param_types = analyze_parameter_types(func_info)
            
            if func_info.args:
                print("**参数列表**:")
                for arg in func_info.args:
                    type_desc = param_types.get(arg, "`Any`")
                    print(f"- `{arg}`: {type_desc}")
                print()
            
            # 生成简单模板
            template = generate_simple_template(func_name, func_info)
            print("**调用模板**:")
            print("```")
            print(template)
            print("```\n")
            
            print("---\n")

    # 打印函数模板（Markdown格式，带锚点）
    print_function_templates_markdown()

    return info_funcs