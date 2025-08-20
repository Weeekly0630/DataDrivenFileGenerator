from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories, FunctionRegistry
from modules.node.data_node import DataNode
import os
import importlib
import inspect

class FunctionCollectorPlugin(FunctionPlugin):
    """插件函数信息收集"""
    
    class MetaData(MetaBase):
        collects: List[str] = field(default_factory=list)  # 要收集的插件类名列表
    
    @staticmethod
    def discover_plugin_classes() -> List[str]:
        """自动发现插件目录中的所有可用类（递归扫描子目录）"""
        plugin_classes = []
        plugins_dir = os.path.dirname(__file__)
        
        print(f"扫描插件目录: {plugins_dir}")
        
        # 递归扫描所有Python文件
        def scan_directory(current_dir: str, base_module_path: str = "modules.plugins"):
            """递归扫描目录中的Python文件"""
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                
                if os.path.isfile(item_path) and item.endswith('.py') and not item.startswith('__') and item != 'function_collector.py':
                    # 计算相对于plugins目录的模块路径
                    rel_path = os.path.relpath(item_path, plugins_dir)
                    module_parts = rel_path.replace(os.sep, '.').replace('.py', '')
                    module_name = module_parts
                    module_path = f"{base_module_path}.{module_parts}"
                    
                    print(f"扫描模块: {module_name} ({module_path})")
                    
                    try:
                        module = importlib.import_module(module_path)
                        
                        # 查找模块中的所有类
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # 跳过导入的类（不是在当前模块定义的）
                            if obj.__module__ != module_path:
                                continue
                            
                            print(f"  检查类: {name}")
                            
                            # 直接用 auto_register_factories 来检查是否是插件类
                            try:
                                user_funcs, registry = auto_register_factories(obj)
                                if len(user_funcs) > 0:  # 如果能生成函数，说明是有效的插件类
                                    if name not in plugin_classes:
                                        plugin_classes.append(name)
                                        print(f"    ✓ 发现插件类: {name} (生成了 {len(user_funcs)} 个函数)")
                                else:
                                    print(f"    ✗ 不是插件类: {name} (没有生成函数)")
                            except Exception as e:
                                print(f"    ✗ 检查类 {name} 时出错: {type(e).__name__}: {e}")
                                
                    except ImportError as e:
                        print(f"导入模块 {module_name} 失败（ImportError）: {e}")
                        continue
                    except AttributeError as e:
                        print(f"模块 {module_name} 属性错误（AttributeError）: {e}")
                        continue
                    except SyntaxError as e:
                        print(f"模块 {module_name} 语法错误（SyntaxError）: {e}")
                        continue
                    except Exception as e:
                        print(f"扫描模块 {module_name} 时出现未知错误: {type(e).__name__}: {e}")
                        continue
                        
                elif os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                    # 递归扫描子目录
                    print(f"进入子目录: {item}")
                    scan_directory(item_path, base_module_path)
        
        # 开始递归扫描
        scan_directory(plugins_dir)
        
        print(f"总共发现 {len(plugin_classes)} 个插件类: {plugin_classes}")
        return plugin_classes
    
    @staticmethod
    def collect_plugin_functions(plugin_classes: List[str]) -> Dict[str, Any]:
        """收集指定插件类的函数信息"""
        all_registries = {}
        all_user_functions = []
        failed_classes = []
        
        # 注意：这里不再自动发现，由调用方负责传入类列表
        # 如果需要自动发现，应该调用 discover_plugin_classes() 后再传入
        
        for class_name in plugin_classes:
            try:
                # 动态导入插件类
                target_class = None
                
                # 尝试从所有插件模块导入（递归查找）
                plugins_dir = os.path.dirname(__file__)
                
                def find_class_in_directory(current_dir: str, base_module_path: str = "modules.plugins"):
                    """递归查找指定类"""
                    for item in os.listdir(current_dir):
                        item_path = os.path.join(current_dir, item)
                        
                        if os.path.isfile(item_path) and item.endswith('.py') and not item.startswith('__'):
                            # 计算相对于plugins目录的模块路径
                            rel_path = os.path.relpath(item_path, plugins_dir)
                            module_parts = rel_path.replace(os.sep, '.').replace('.py', '')
                            module_path = f"{base_module_path}.{module_parts}"
                            
                            try:
                                module = importlib.import_module(module_path)
                                if hasattr(module, class_name):
                                    candidate_class = getattr(module, class_name)
                                    # 确保这个类是在该模块中定义的
                                    if candidate_class.__module__ == module_path:
                                        print(f"在模块 {module_parts} 中找到类 {class_name}")
                                        return candidate_class
                            except ImportError as e:
                                print(f"导入模块 {module_parts} 失败（ImportError）: {e}")
                                continue
                            except AttributeError as e:
                                print(f"模块 {module_parts} 属性错误（AttributeError）: {e}")
                                continue
                            except SyntaxError as e:
                                print(f"模块 {module_parts} 语法错误（SyntaxError）: {e}")
                                continue
                            except Exception as e:
                                print(f"检查模块 {module_parts} 时出现未知错误: {type(e).__name__}: {e}")
                                continue
                                
                        elif os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                            # 递归查找子目录
                            result = find_class_in_directory(item_path, base_module_path)
                            if result is not None:
                                return result
                    
                    return None
                
                target_class = find_class_in_directory(plugins_dir)
                
                if target_class is None:
                    print(f"未找到类 {class_name}")
                    failed_classes.append(class_name)
                    continue
                
                # 收集函数信息
                try:
                    user_funcs, registry = auto_register_factories(target_class)
                    all_registries[class_name] = registry
                    all_user_functions.extend(user_funcs)
                    print(f"成功收集 {class_name} 类的 {len(user_funcs)} 个函数")
                except Exception as e:
                    print(f"收集 {class_name} 类函数时出错: {type(e).__name__}: {e}")
                    failed_classes.append(class_name)
                    continue
                
            except Exception as e:
                print(f"处理 {class_name} 类时出现未知错误: {type(e).__name__}: {e}")
                failed_classes.append(class_name)
                continue
        
        return {
            "registries": all_registries,
            "user_functions": all_user_functions,
            "total_functions": len(all_user_functions),
            "discovered_classes": plugin_classes,
            "failed_classes": failed_classes,
            "successful_classes": list(all_registries.keys())
        }
    
    @staticmethod
    def create(context: UserFunctionContext, *plugin_classes: str) -> Dict[str, Any]:
        """收集所有插件函数信息"""
        if not plugin_classes:
            # 如果未指定类，自动发现所有插件类
            plugin_classes = tuple(FunctionCollectorPlugin.discover_plugin_classes())
        
        return FunctionCollectorPlugin.collect_plugin_functions(list(plugin_classes))
    
    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """注册函数收集器函数"""
        
        def collect_functions_handler(context: UserFunctionContext, *plugin_classes: str) -> Dict[str, Any]:
            """函数收集处理器 - 返回结构化数据对象"""
            result = cls.create(context, *plugin_classes)
            
            # 转换 FunctionRegistry 对象为可序列化的字典
            serializable_registries = {}
            for class_name, registry in result['registries'].items():
                functions_dict = {}
                for func_name, func_sig in registry.get_all_functions().items():
                    # 转换函数签名为字典
                    functions_dict[func_name] = {
                        'description': func_sig.description,
                        'parameters': [
                            {
                                'name': param.name,
                                'type_name': param.type_name,
                                'type_description': param.type_description,
                                'is_plugin_type': param.is_plugin_type,
                                'related_function': param.related_function
                            }
                            for param in func_sig.parameters
                        ]
                    }
                serializable_registries[class_name] = functions_dict
            
            # 返回完整的结构化数据
            return {
                'registries': serializable_registries,
                'total_functions': result['total_functions'],
                'discovered_classes': result['discovered_classes'],
                'failed_classes': result['failed_classes'],
                'successful_classes': result['successful_classes']
            }
        
        def discover_classes_handler(context: UserFunctionContext) -> str:
            """发现插件类处理器"""
            discovered = cls.discover_plugin_classes()
            summary = f"发现的插件类:\n"
            for class_name in discovered:
                summary += f"- {class_name}\n"
            return summary
        
        # 创建验证器
        collect_validator = UserFunctionValidator()
        collect_validator.add_param_check_validator(min_args=0, max_args=10)
        
        discover_validator = UserFunctionValidator()
        discover_validator.add_param_check_validator(min_args=0, max_args=0)
        
        info_funcs = [
            UserFunctionInfo(
                name="collect_plugin_functions",
                handler=collect_functions_handler,
                validator=collect_validator,
                description="收集指定插件类的函数信息，返回结构化数据对象。可传入类名参数，不传则自动发现所有类"
            ),
            UserFunctionInfo(
                name="discover_plugin_classes",
                handler=discover_classes_handler,
                validator=discover_validator,
                description="自动发现所有可用的插件类"
            )
        ]
        
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
