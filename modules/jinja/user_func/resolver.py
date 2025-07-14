from .func_handler import UserFunctionResolver, UserFunctionInfo
from modules.core import DataHandler
from modules.node.data_node import DataNode
from typing import Dict, Callable, List, Type
import importlib
import os
import sys
from pathlib import Path


# 增强版插件接口
class FunctionPlugin:
    """插件基类，支持静态和动态函数"""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """返回插件提供的静态函数列表（与节点无关）"""
        return []

    @classmethod
    def dynamic_functions(cls, node: DataNode) -> List[UserFunctionInfo]:
        """返回插件提供的动态函数列表（需要节点上下文）"""
        return []

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass


# 增强版工厂类
class UserFunctionResolverFactory:
    def __init__(self, plugins_dir: str = str(Path(__file__).parent / "plugins")):
        self.plugins_dir = plugins_dir
        self.plugin_classes: List[Type[FunctionPlugin]] = []
        self.static_functions: Dict[str, UserFunctionInfo] = {}

        # 初始化时加载所有插件
        self._load_plugins()
        # 收集所有静态函数
        self._collect_static_functions()

    @staticmethod
    def _serialize_function_info(info: UserFunctionInfo, indent: int) -> str:
        result: str = (
            f"{' ' * indent}{info.name}[{info.arg_range[0]},{info.arg_range[1]}]: {info.description}"
        )
        return result

    def show_function_info(self) -> str:
        result = ""
        result += f"========Static functions========\n"
        for key, value in self.static_functions.items():
            result += self._serialize_function_info(value, indent=0) + "\n"

        result += f"========Dynamic functions========\n"
        for info in self._create_dynamic_functions(None, None):
            result += self._serialize_function_info(info, indent=0) + "\n"

        return result

    def _load_plugins(self):
        """扫描并加载插件目录中的所有有效插件"""
        plugins_path = Path(self.plugins_dir)

        if not plugins_path.exists():
            os.makedirs(plugins_path, exist_ok=True)
            return

        # 确保插件目录在Python路径中
        if str(plugins_path) not in sys.path:
            sys.path.append(str(plugins_path))

        # 扫描所有.py文件（排除__init__.py）
        loaded_modules = set()
        for file_path in plugins_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            module_name = file_path.stem
            try:
                # 防止重复加载
                if module_name in loaded_modules:
                    continue

                module = importlib.import_module(module_name)
                loaded_modules.add(module_name)
                self._register_plugin(module)
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {str(e)}")

    def _register_plugin(self, module):
        """注册插件模块"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if (
                isinstance(attr, type)
                and issubclass(attr, FunctionPlugin)
                and attr != FunctionPlugin
            ):

                plugin_class = attr
                try:
                    # 调用插件初始化方法
                    plugin_class.on_plugin_load()
                    self.plugin_classes.append(plugin_class)
                    print(f"Loaded plugin: {plugin_class.__name__}")
                except Exception as e:
                    print(
                        f"Error initializing plugin {plugin_class.__name__}: {str(e)}"
                    )

    def _collect_static_functions(self):
        """收集所有插件的静态函数"""
        # 内置静态函数
        # builtin_static = {
        #     "user:double": UserFunctionInfo(
        #         name="user:double",
        #         arg_range=[1, 1],
        #         description="Double the input value",
        #         handler=lambda x: 2 * x.value,
        #     ),
        #     "util:uppercase": UserFunctionInfo(
        #         name="util:uppercase",
        #         arg_range=[1, 1],
        #         description="Convert string to uppercase",
        #         handler=lambda s: s.upper(),
        #     ),
        # }

        # 收集插件静态函数
        plugin_static = {}
        for plugin_class in self.plugin_classes:
            try:
                for func_info in plugin_class.static_functions():
                    # 防止函数名冲突
                    if func_info.name in plugin_static:
                        print(
                            f"Warning: Duplicate static function name '{func_info.name}' in plugin {plugin_class.__name__}"
                        )
                    else:
                        plugin_static[func_info.name] = func_info
            except Exception as e:
                print(
                    f"Error collecting static functions from {plugin_class.__name__}: {str(e)}"
                )

        # 合并所有静态函数
        self.static_functions = {**plugin_static}

    def _create_dynamic_functions(
        self, node: DataNode, data_handler: DataHandler
    ) -> List[UserFunctionInfo]:
        """创建内置和插件的动态函数"""
        # 内置动态函数
        # builtin_dynamic = [
        #     UserFunctionInfo(
        #         name="node:name",
        #         arg_range=[0, 0],
        #         description="Get current node name",
        #         handler=lambda: node.name,
        #     ),
        #     UserFunctionInfo(
        #         name="node:path",
        #         arg_range=[0, 0],
        #         description="Get node absolute path",
        #         handler=lambda: node.get_absolute_path(),
        #     ),
        #     UserFunctionInfo(
        #         name="node:get_rel",
        #         arg_range=[1, 1],
        #         description="Find node by relative path",
        #         handler=lambda x: self.data_handler.find_by_file_path(node, x)[0],
        #     ),
        #     UserFunctionInfo(
        #         name="node:get_attr",
        #         arg_range=[2, 2],
        #         description="Get node attribute",
        #         handler=lambda x, attr: str(x.data.get(attr, "")),
        #     ),
        # ]

        # 插件动态函数
        plugin_dynamic = []
        for plugin_class in self.plugin_classes:
            try:
                # 获取插件的动态函数
                funcs = plugin_class.dynamic_functions(node)
                plugin_dynamic.extend(funcs)
            except Exception as e:
                print(
                    f"Error creating dynamic functions from {plugin_class.__name__}: {str(e)}"
                )

        return plugin_dynamic

    def create_resolver(
        self, node: DataNode, data_handler: DataHandler
    ) -> UserFunctionResolver:
        """创建函数解析器"""
        static_funcs = list(self.static_functions.values())
        dynamic_funcs = self._create_dynamic_functions(node, data_handler)
        return UserFunctionResolver(static_funcs + dynamic_funcs)

    def reload_plugins(self):
        """重新加载所有插件"""
        # 清理现有插件
        for plugin_class in self.plugin_classes:
            try:
                plugin_class.on_plugin_unload()
            except Exception as e:
                print(f"Error unloading plugin {plugin_class.__name__}: {str(e)}")

        self.plugin_classes.clear()
        self._load_plugins()
        self._collect_static_functions()
