import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

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
class ParameterInfo:
    """参数信息"""
    name: str
    type_name: str  # 类型名称，如 'str', 'int', 'bool' 或自定义类型
    is_plugin_type: bool = False  # 是否为插件自定义类型
    type_description: str = ""  # 类型描述
    related_function: Optional[str] = None  # 关联的函数名（如果是插件类型）

@dataclass
class FunctionSignature:
    """函数签名信息"""
    name: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    description: str = ""
    source_class: str = ""  # 来源类名
    
    def get_parameter_by_name(self, param_name: str) -> Optional[ParameterInfo]:
        """根据参数名获取参数信息"""
        for param in self.parameters:
            if param.name == param_name:
                return param
        return None

class FunctionRegistry:
    """函数注册表，用于存储和管理所有函数信息"""
    
    def __init__(self):
        self.functions: Dict[str, FunctionSignature] = {}
        self.type_mappings: Dict[str, str] = {}  # 参数名 -> 函数名的映射
    
    def register_function(self, signature: FunctionSignature) -> None:
        """注册一个函数"""
        self.functions[signature.name] = signature
        
        # 更新类型映射
        for param in signature.parameters:
            if param.is_plugin_type and param.related_function:
                self.type_mappings[param.name] = param.related_function
    
    def get_function(self, name: str) -> Optional[FunctionSignature]:
        """获取函数信息"""
        return self.functions.get(name)
    
    def get_all_functions(self) -> Dict[str, FunctionSignature]:
        """获取所有函数"""
        return self.functions.copy()
    
    def find_related_function(self, param_name: str) -> Optional[str]:
        """查找参数相关的函数名"""
        return self.type_mappings.get(param_name)
    
    def get_functions_by_source(self, source_class: str) -> List[FunctionSignature]:
        """根据来源类获取函数列表"""
        return [func for func in self.functions.values() if func.source_class == source_class]
    
    def print_summary(self) -> None:
        """打印函数注册表摘要"""
        print(f"函数注册表摘要:")
        print(f"  总函数数: {len(self.functions)}")
        print(f"  类型映射数: {len(self.type_mappings)}")
        
        # 按来源类分组显示
        source_classes = set(func.source_class for func in self.functions.values())
        for source_class in source_classes:
            funcs = self.get_functions_by_source(source_class)
            print(f"  来源类 {source_class}: {len(funcs)} 个函数")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "functions": {
                name: {
                    "name": func.name,
                    "parameters": [
                        {
                            "name": param.name,
                            "type_name": param.type_name,
                            "is_plugin_type": param.is_plugin_type,
                            "type_description": param.type_description,
                            "related_function": param.related_function
                        }
                        for param in func.parameters
                    ],
                    "description": func.description,
                    "source_class": func.source_class
                }
                for name, func in self.functions.items()
            },
            "type_mappings": self.type_mappings
        }


def print_registry_info(registry: FunctionRegistry) -> None:
    """打印注册表详细信息"""
    print("=== 函数注册表详细信息 ===\n")
    
    for func_name, func_sig in registry.get_all_functions().items():
        print(f"函数: {func_name}")
        print(f"  来源类: {func_sig.source_class}")
        print(f"  描述: {func_sig.description}")
        print(f"  参数:")
        
        for param in func_sig.parameters:
            type_desc = f"{param.type_name}"
            if param.is_plugin_type:
                type_desc += f" (Plugin: {param.related_function})"
            else:
                type_desc += f" ({param.type_description})"
            print(f"    - {param.name}: {type_desc}")
        print()

def auto_register_factories(cls) -> Tuple[List[UserFunctionInfo], FunctionRegistry]:
    """
    自动注册工厂函数并收集函数信息
    
    Returns:
        Tuple[List[UserFunctionInfo], FunctionRegistry]: 用户函数信息列表和函数注册表
    """
    info_funcs: List[UserFunctionInfo] = []
    registry = FunctionRegistry()

    def get_function_name(attr_name: str) -> str:
        return f"{cls.__name__.lower()}_{attr_name.lower()}_create"
    
    def analyze_parameter_type(param_name: str, all_functions: Dict[str, List[str]]) -> ParameterInfo:
        """分析参数类型信息"""
        
        # 检查是否有对应的 Plugin 函数
        corresponding_func = None
        for func_name, func_params in all_functions.items():
            if (param_name in ["type", "ref", "typeref"] and "typeref" in func_name) or \
               (param_name == "modifier" and "typemodifier" in func_name) or \
               (param_name == "fields" and "field" in func_name) or \
               (param_name == "attributes" and "attr" in func_name):
                corresponding_func = func_name
                break
        
        if corresponding_func:
            # Plugin 自定义类型
            return ParameterInfo(
                name=param_name,
                type_name=corresponding_func,
                is_plugin_type=True,
                type_description=f"Plugin function: {corresponding_func}",
                related_function=corresponding_func
            )
        else:
            # Python 基本类型
            if param_name == "name":
                type_info = ("str", "名称字符串")
            elif param_name in ["qualifiers"]:
                type_info = ("str", "限定符字符串")
            elif param_name in ["fields", "attributes", "array_dims"]:
                type_info = ("List", "列表类型")
            elif param_name in ["is_pointer", "is_array"]:
                type_info = ("bool", "布尔值")
            elif param_name in ["pointer_level", "bitfield_width"]:
                type_info = ("int", "整数值")
            elif param_name == "init_expr":
                type_info = ("Any", "初始化表达式")
            else:
                type_info = ("Any", "任意类型")
            
            return ParameterInfo(
                name=param_name,
                type_name=type_info[0],
                is_plugin_type=False,
                type_description=type_info[1]
            )
    
    # 第一遍扫描：收集所有函数名和参数列表
    all_functions: Dict[str, List[str]] = {}
    
    # 遍历类的所有属性
    for attr_name in dir(cls):
        if attr_name.startswith("__") and attr_name.endswith("__"):
            continue

        try:
            attr = getattr(cls, attr_name)
        except Exception:
            continue

        if isinstance(attr, type) and hasattr(attr, "MetaData"):
            function_name = get_function_name(attr_name)
            metadata_fields = list(attr.MetaData.__dataclass_fields__.keys())
            all_functions[function_name] = metadata_fields
    
    # 第二遍扫描：创建完整的函数信息
    for attr_name in dir(cls):
        if attr_name.startswith("__") and attr_name.endswith("__"):
            continue

        try:
            attr = getattr(cls, attr_name)
        except Exception:
            continue

        if isinstance(attr, type) and hasattr(attr, "MetaData"):
            function_name = get_function_name(attr_name)
            metadata_fields = list(attr.MetaData.__dataclass_fields__.keys())
            
            # 创建参数信息
            parameters = []
            for field_name in metadata_fields:
                param_info = analyze_parameter_type(field_name, all_functions)
                parameters.append(param_info)
            
            # 创建函数签名
            description = attr.MetaData.__doc__ if attr.MetaData.__doc__ else f"自动生成的{attr.MetaData.__name__}工厂函数"
            signature = FunctionSignature(
                name=function_name,
                parameters=parameters,
                description=description,
                source_class=cls.__name__
            )
            
            # 注册到注册表
            registry.register_function(signature)
            
            # 创建处理器和验证器
            def gather_functions(
                subcls, metadata_fields: List[str], func_name: str
            ) -> Tuple[UserFunctionHandlerType, Union[UserFunctionValidator, None]]:
                
                if hasattr(subcls, "create"):
                    handler = getattr(subcls, "create")
                    if hasattr(subcls, "validator") and callable(getattr(subcls, "validator")):
                        validator = getattr(subcls, "validator")()
                    else:
                        validator = None
                else:
                    # 用 *args 按字段顺序传参
                    handler = lambda *args, **kwargs: subcls.MetaData(
                        **{k: v for k, v in zip(metadata_fields, args[1:])}, **kwargs
                    )
                    # 自动创建 validator
                    validator = UserFunctionValidator()
                    validator.add_param_check_validator(
                        min_args=len(metadata_fields), max_args=len(metadata_fields)
                    )

                return (handler, validator)

            handler, validator = gather_functions(attr, metadata_fields, function_name)
            
            info_funcs.append(
                UserFunctionInfo(
                    name=function_name,
                    handler=handler,
                    validator= None, # validator
                    description=description,
                )
            )

    return info_funcs, registry


# 使用示例和测试
if __name__ == "__main__":
    
    # 假设有一个 Decl 类用于测试
    class MockDecl:
        class TypeRef:
            @dataclass
            class MetaData:
                ref: str
        
        class Variable:
            @dataclass  
            class MetaData:
                name: str
                modifier: str
                type: "MockDecl.TypeRef.MetaData"
                init_expr: str = ""
    
    print("测试函数信息收集...")
    
    try:
        # 收集函数信息
        user_funcs, registry = auto_register_factories(MockDecl)
        
        # 显示注册表信息
        registry.print_summary()
        print("\n")
        print_registry_info(registry)
        
        # 展示字典格式
        print("\n=== 字典格式输出 ===")
        import json
        print(json.dumps(registry.to_dict(), indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()