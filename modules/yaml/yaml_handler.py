import yaml
from typing import Optional, List, Dict, Any, Iterator, cast, Union
from dataclasses import dataclass
from pathlib import Path

# from ..node.expr_node import ExprASTParser, ExprPrintVistor

from ..node.data_node import DataNode
from ..node.file_node import DirectoryNode, FileNode, BaseNode
from ..core import DataHandler


@dataclass
class YamlConfig:
    """YAML配置，包含模板和子节点路径的保留键"""

    file_root_path: str
    file_pattern: List[str]
    encoding: str

    @classmethod
    def validate(cls, config: Dict[str, Any]) -> "YamlConfig":
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        if "file_root_path" not in config or not isinstance(
            config["file_root_path"], str
        ):
            raise ValueError("Config must contain 'file_root_path' as a string")

        return cls(
            file_root_path=config.get("file_root_path", ""),
            file_pattern=config.get("file_pattern", []),
            encoding=config.get("encoding", "utf-8"),
        )


class _YamlFileHandler:
    """内部使用的YAML文件处理类"""

    @staticmethod
    def _load_yaml_file(yaml_path: str) -> Dict:
        """加载YAML文件并返回字典数据

        Args:
            yaml_path: YAML文件的路径

        Returns:
            dict: YAML文件的内容

        Raises:
            YamlLoadError: 如果文件不存在或格式错误
        """
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    return {}
                elif isinstance(data, dict):
                    return data
                else:
                    return {"data": data}  # 如果不是字典，封装为{"data": ...}
        except (IOError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to load YAML file: {yaml_path}") from e


class YamlDataTreeHandler(DataHandler):
    """YAML数据树处理器

    实现了DataHandler协议的YAML处理器，提供以下功能：
    - create_data_tree: 从指定模式创建YAML数据树
    - get_data_nodes: 根据文件路径模式查找数据节点
    - get_absolute_path: 获取节点的绝对路径

    主要用于管理YAML配置文件的层级结构，支持模板引用和子节点包含。
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """初始化处理器

        Args:
            config: 配置字典，参见YamlConfig的文档

        Raises:
            YamlConfigError: 配置验证失败
        """
        self.config: YamlConfig = YamlConfig.validate(config)

        self._node_paths: List[str] = []  # 用于检测循环引用
        # 节点双向映射表
        self._file_node_mapping: Dict[DataNode, FileNode] = {}
        self._data_node_mapping: Dict[FileNode, DataNode] = {}

        # 初始化文件树
        self.file_tree: DirectoryNode = DirectoryNode(
            dir_name=self.config.file_root_path, parent=None, obj=None, children=[]
        )
        # 构建文件树
        self.file_tree.build_tree(self.config.file_root_path, self.config.file_pattern)
        # 打印文件树
        print("==============Serialized File Tree==============")
        print(self.file_tree.serialze())
        # 为每一个目标FileNode创建对应的DataNode
        # self._data_node_init(self.file_tree)
        # 不在一开始Init, 而是在过程中动态创建DataNode

    def _get_mapping(
        self, node: Union[DataNode, FileNode]
    ) -> Optional[Union[DataNode, FileNode]]:
        """获取节点的映射关系"""
        if isinstance(node, DataNode):
            return self._file_node_mapping.get(node)
        elif isinstance(node, FileNode):
            result = self._data_node_mapping.get(node)
            if result is None:
                # 如果没有映射关系，尝试创建DataNode
                return self._data_node_create(node)
            else:
                return result
        else:
            return None

    def _init_mapping(self) -> None:
        """初始化映射"""
        self._file_node_mapping.clear()
        self._data_node_mapping.clear()

    def _add_mapping(self, data_node: DataNode, file_node: FileNode) -> None:
        self._file_node_mapping[data_node] = file_node
        self._data_node_mapping[file_node] = data_node

    def _clear_mapping(self) -> None:
        self._file_node_mapping.clear()
        self._data_node_mapping.clear()

    def find_node_by_path(self, data_node: DataNode, pattern: str) -> List[DataNode]:
        """根据路径模式查找数据节点"""
        results: List[DataNode] = []
        # 获取匹配的文件节点
        file_node = self._get_mapping(data_node)
        if isinstance(file_node, FileNode):
            parent_base_node = file_node._parent.parent
            if parent_base_node:
                dir_node = parent_base_node.mapping_obj
                if isinstance(dir_node, DirectoryNode):
                    matching_files = dir_node.find(pattern)
                    for matching_file in matching_files:
                        if isinstance(matching_file, FileNode):
                            # Get DataNode from mapping
                            child_data_node = self._get_mapping(matching_file)
                            if (
                                isinstance(child_data_node, DataNode)
                                and child_data_node is not None
                            ):
                                # 添加parent
                                if child_data_node.add_parent(data_node) is True:
                                    results.append(child_data_node)
        return results
    
    def _build_tree(self, data_node: DataNode, children_key: str) -> None:
        """构建数据节点树"""
        # 遍历所有children_key路径
        patterns = data_node.data.get(children_key)
        # 处理 patterns 为 None 的情况
        if patterns == None:
            return

        def append_child_by_path(data_node: DataNode, pattern: str) -> List:
            find_results: List[DataNode] = self.find_node_by_path(data_node, pattern)
            # Transfer results to BaseNode children
            results = [each._parent._parent for each in find_results if each is not None]
            # Recursively build tree for each found node
            for each in find_results:
                if isinstance(each, DataNode):
                    self._build_tree(each, children_key)
                    
            # # 获取匹配的文件节点
            # file_node = self._get_mapping(data_node)
            # if isinstance(file_node, FileNode):
            #     parent_base_node = file_node._parent.parent
            #     if parent_base_node:
            #         dir_node = parent_base_node.mapping_obj
            #         if isinstance(dir_node, DirectoryNode):
            #             matching_files = dir_node.find(pattern)
            #             for matching_file in matching_files:
            #                 if isinstance(matching_file, FileNode):
            #                     # Get DataNode from mapping
            #                     child_data_node = self._get_mapping(matching_file)
            #                     if (
            #                         isinstance(child_data_node, DataNode)
            #                         and child_data_node is not None
            #                     ):
            #                         # 添加parent
            #                         if child_data_node.add_parent(data_node) is True:
            #                             results.append(child_data_node._parent._parent)
            #                         # 递归处理子节点
            #                         self._build_tree(child_data_node, children_key)
            return results

        # 遍历每个模式

        def handle_any(
            cur_data_node: DataNode, patterns: Any
        ) -> Union[BaseNode, List, Dict, None]:
            result: Union[BaseNode, List, Dict, None] = None

            if isinstance(patterns, List):
                # 初始化data_node的base node children为列表
                result = [None] * len(patterns)
                for index, pattern in enumerate(patterns):
                    result[index] = handle_any(cur_data_node, pattern)
            elif isinstance(patterns, str):
                result = []
                result.extend(append_child_by_path(cur_data_node, patterns))
            elif isinstance(patterns, Dict):
                # inline dict，创建匿名DataNode并递归处理
                inline_data_node = DataNode(
                    data=patterns, name=patterns.get("name", "inline_child")
                )

                # 添加parent
                if inline_data_node.add_parent(cur_data_node) is True:
                    result = inline_data_node._parent._parent
                # 递归处理子节点
                self._build_tree(inline_data_node, children_key)
            return result

        data_node._parent._parent.children = handle_any(data_node, patterns)

    def create_data_tree(self, *args, **kvargs) -> List[DataNode]:
        """根据预留的pattern作为入口文件，以预留children_key建立文件树"""
        # Check if required keys are present
        results: List[DataNode] = []

        keys = ["pattern", "preserved_children_key"]
        for key in keys:
            if key not in kvargs:
                raise ValueError(f"Missing required key: {key}")
        # Extract parameters
        pattern = kvargs["pattern"]
        preserved_children_key = kvargs["preserved_children_key"]

        # 1. Get Entry FileNode
        entry_file_node = self.file_tree.find(pattern)
        for file_node in entry_file_node:
            if isinstance(file_node, FileNode):
                # 2. Get DataNode from FileNode
                data_node = self._get_mapping(file_node)
                if data_node is None:
                    print(
                        f"FileNode {file_node.meta_data.name} has no corresponding DataNode."
                    )
                elif isinstance(data_node, DataNode):
                    # 3. Build DataNode tree
                    self._build_tree(data_node, preserved_children_key)
                    # 4. Add DataNode to results
                    results.append(data_node)
        return results

    # def get_absolute_path(self, node: DataNode) -> str:
    #     """获取节点的文件绝对路径

    #     Args:
    #         node: 数据节点

    #     Returns:
    #         str: 节点的绝对路径
    #     """
    #     file_node = self.data_node_to_file_node(node)
    #     if file_node:
    #         return self._get_full_path(file_node)
    #     else:
    #         return "

    # def find_by_file_path(self, node: DataNode, pattern: str) -> List[DataNode]:
    #     """根据文件路径模式查找数据节点

    #     Args:
    #         pattern: 文件路径模式，如 "*.yaml" 或 "**/config/*.yaml"

    #     Returns:
    #         List[DataNode]: 匹配的数据节点列表
    #     """
    #     # Get file node from mapping
    #     file_node: Optional[FileNode] = self._file_node_mapping.get(node, None)
    #     if file_node is None:
    #         pass

    #     found_node = cast(DirectoryNode, file_node.parent).find_nodes_by_path(pattern)
    #     result: List[DataNode] = []
    #     for found in found_node:
    #         if isinstance(found, FileNode):
    #             # Get data node from mapping
    #             data_node = self._data_node_mapping.get(found)
    #             if data_node:
    #                 result.append(data_node)
    #     return result

    # def _data_node_init(self, root: DirectoryNode) -> None:
    #     """给每一个匹配的FileNode创建对应的DataNode"""
    #     for child in root._parent.children:
    #         node = child.mapping_obj
    #         if isinstance(node, DirectoryNode):
    #             self._data_node_init(node)
    #         elif isinstance(node, FileNode):
    #             self._data_node_create(node)

    def _data_node_create(self, file_node: FileNode) -> DataNode:
        """从FileNode读取Yaml数据并创建DataNode"""

        file_system_path: str = file_node.get_abs_path()

        data = _YamlFileHandler._load_yaml_file(file_system_path)
        if data:
            # 创建数据节点并存入映射
            data_node = DataNode(data=data, name=file_node.meta_data.name)

            # Add data node to file node mapping
            self._add_mapping(data_node, file_node)
        else:
            raise ValueError(f"Data in file {file_system_path} is empty or invalid")
        return data_node

    # def preprocess_expr(self, data_node: DataNode) -> None:
    #     """预处理表达式"""
    #     # 遍历所有DataNode
    #     parser = ExprASTParser()

    #     node_resolver = self._resolver_factory.create_resolver(data_node, self)

    #     def preprocess_data(data) -> Any:
    #         """预处理数据，转换expr字典转换为ExprNode, 并最后转换为字符串替换原有的表达式"""
    #         if isinstance(data, Dict):
    #             # 先递归解析子节点
    #             # 检查是否需要解析为ExprNode
    #             for key, value in data.items():
    #                 result_obj = preprocess_data(value)  # 递归处理子字典
    #                 if result_obj != None:
    #                     data[key] = result_obj

    #             expr_node = parser.parse(data)
    #             if expr_node != data:  # 如果解析结果不是原始数据，说明是一个表达式
    #                 # 使用ExprPrintVisitor将ExprNode转换为字符串
    #                 result_obj = expr_node.accept(ExprPrintVistor(node_resolver))
    #                 return result_obj
    #             else:
    #                 return None
    #         elif isinstance(data, list):
    #             # 处理列表中的每个元素
    #             for index, item in enumerate(data):
    #                 if isinstance(item, dict):
    #                     result_obj = preprocess_data(item)
    #                     if result_obj != "":
    #                         data[index] = result_obj
    #             return data
    #         else:
    #             return None

    #     # 预处理数据，转换expr表达式
    #     preprocess_data(data_node.data)

    # def _get_full_path(self, file_node: FileNode) -> str:
    #     """获取文件节点的全路径(绝对路径)"""
    #     return str(self.config.root_path) + file_node.get_absolute_path(
    #         slice_range=(1, None)
    #     )

    # def file_node_to_data_node(self, file_node: FileNode) -> Optional[DataNode]:
    #     return self._data_node_mapping.get(file_node)

    # def data_node_to_file_node(self, data_node: DataNode) -> Optional[FileNode]:
    #     return self._file_node_mapping.get(data_node)

    # def _build_data_tree(self, file_node: FileNode, ancestors=None) -> DataNode:
    #     """构建DataTree, 返回根节点（支持递归链路检测循环引用）"""
    #     if ancestors is None:
    #         ancestors = set()
    #     data_node = self.file_node_to_data_node(file_node)
    #     if data_node is None:
    #         raise ValueError(f"{file_node.name}'s data node not found?")

    #     # 检查递归链路上的循环引用
    #     node_id = id(data_node)
    #     if node_id in ancestors:
    #         raise YamlStructureError.circular_reference(self._get_full_path(file_node))
    #     ancestors.add(node_id)

    #     # 处理子节点
    #     children_path = data_node.data[self.preserved_children_key]

    #     if children_path == "":  # 空字符串视为空列表
    #         children_path = []
    #     if children_path:
    #         if isinstance(children_path, str):
    #             children_path = [children_path]  # 转换单个字符串为列表
    #         elif isinstance(children_path, list):
    #             pass  # 已经是列表

    #         # 为每个模式创建子节点, 同时将他们分组
    #         for paths in children_path:
    #             if not paths:  # 跳过空路径
    #                 continue
    #             # 支持三种情况：str（路径）、dict（inline）、list（混合）
    #             if isinstance(paths, dict):
    #                 # 直接作为子节点
    #                 child_node = DataNode(
    #                     data=paths,
    #                     name=paths.get(self.preserved_template_key, "inline_child"),
    #                 )
    #                 # 递归处理其子节点
    #                 self._build_data_tree_for_inline(child_node, ancestors.copy())
    #                 data_node.add_child(child_node)
    #                 data_node.children_group_number.append(1)
    #             elif isinstance(paths, list):
    #                 current_group_number = 0
    #                 for item in paths:
    #                     if isinstance(item, dict):
    #                         child_node = DataNode(
    #                             data=item,
    #                             name=item.get(
    #                                 self.preserved_template_key, "inline_child"
    #                             ),
    #                         )
    #                         self._build_data_tree_for_inline(
    #                             child_node, ancestors.copy()
    #                         )
    #                         data_node.add_child(child_node)
    #                         current_group_number += 1
    #                     elif isinstance(item, str):
    #                         # 兼容原有路径逻辑，支持顺序控制和组内去重
    #                         if not item:
    #                             continue
    #                         group_member_set = set()
    #                         if file_node.parent:
    #                             matching_files = cast(
    #                                 DirectoryNode, file_node.parent
    #                             ).find_nodes_by_path(item)
    #                             for matching_file in matching_files:
    #                                 if isinstance(matching_file, FileNode):
    #                                     if matching_file in group_member_set:
    #                                         continue
    #                                     group_member_set.add(matching_file)
    #                                     try:
    #                                         child_node = self.file_node_to_data_node(
    #                                             matching_file
    #                                         )
    #                                         if not child_node:
    #                                             raise ValueError(
    #                                                 f"{self.get_absolute_path}'s data node not found?"
    #                                             )
    #                                         # 检查递归链路上的循环引用
    #                                         if id(child_node) in ancestors:
    #                                             raise YamlStructureError.circular_reference(
    #                                                 self._get_full_path(matching_file)
    #                                             )
    #                                         self._build_data_tree(
    #                                             matching_file, ancestors.copy()
    #                                         )
    #                                         data_node.add_child(child_node)
    #                                         current_group_number += 1
    #                                     except YamlError as e:
    #                                         raise YamlStructureError(
    #                                             e.error_type,
    #                                             f"Error processing child {matching_file.name}: {str(e)}",
    #                                             str(matching_file.get_absolute_path()),
    #                                         ) from e
    #                     else:
    #                         raise YamlStructureError.invalid_children(
    #                             f"Invalid children path specification: {item}",
    #                             self._get_full_path(file_node),
    #                         )
    #                 data_node.children_group_number.append(current_group_number)
    #             elif isinstance(paths, str):
    #                 # 原有单路径逻辑
    #                 if not paths:
    #                     continue
    #                 current_group_number = 0
    #                 if file_node.parent:
    #                     matching_files = cast(
    #                         DirectoryNode, file_node.parent
    #                     ).find_nodes_by_path(paths)
    #                     for matching_file in matching_files:
    #                         if isinstance(matching_file, FileNode):
    #                             try:
    #                                 child_node = self.file_node_to_data_node(
    #                                     matching_file
    #                                 )
    #                                 if not child_node:
    #                                     raise ValueError(
    #                                         f"{self.get_absolute_path}'s data node not found?"
    #                                     )
    #                                 # 检查递归链路上的循环引用
    #                                 if id(child_node) in ancestors:
    #                                     raise YamlStructureError.circular_reference(
    #                                         self._get_full_path(matching_file)
    #                                     )
    #                                 self._build_data_tree(
    #                                     matching_file, ancestors.copy()
    #                                 )
    #                                 data_node.add_child(child_node)
    #                                 current_group_number += 1
    #                             except YamlError as e:
    #                                 raise YamlStructureError(
    #                                     e.error_type,
    #                                     f"Error processing child {matching_file.name}: {str(e)}",
    #                                     str(matching_file.get_absolute_path()),
    #                                 ) from e
    #                 data_node.children_group_number.append(current_group_number)
    #             else:
    #                 raise YamlStructureError.invalid_children(
    #                     f"Invalid children path specification: {paths}",
    #                     self._get_full_path(file_node),
    #                 )

    #     ancestors.remove(node_id)
    #     return data_node

    # # 新增辅助方法，递归处理 inline dict 子节点
    # def _build_data_tree_for_inline(self, data_node: DataNode, ancestors=None) -> None:
    #     if ancestors is None:
    #         ancestors = set()
    #     node_id = id(data_node)
    #     if node_id in ancestors:
    #         raise YamlStructureError.circular_reference(data_node.name)
    #     ancestors.add(node_id)

    #     children_path = data_node.data.get(self.preserved_children_key, [])
    #     if children_path == "":
    #         children_path = []
    #     if children_path:
    #         if isinstance(children_path, str):
    #             children_path = [children_path]
    #         elif isinstance(children_path, list):
    #             pass
    #         else:
    #             raise YamlStructureError.invalid_children(
    #                 f"Invalid children path specification: {children_path}",
    #                 data_node.name,
    #             )
    #         for paths in children_path:
    #             if not paths:
    #                 continue
    #             if isinstance(paths, dict):
    #                 child_node = DataNode(
    #                     data=paths,
    #                     name=paths.get(self.preserved_template_key, "inline_child"),
    #                 )
    #                 self._build_data_tree_for_inline(child_node, ancestors.copy())
    #                 data_node.add_child(child_node)
    #                 data_node.children_group_number.append(1)
    #             elif isinstance(paths, list):
    #                 current_group_number = 0
    #                 for item in paths:
    #                     if isinstance(item, dict):
    #                         child_node = DataNode(
    #                             data=item,
    #                             name=item.get(
    #                                 self.preserved_template_key, "inline_child"
    #                             ),
    #                         )
    #                         self._build_data_tree_for_inline(
    #                             child_node, ancestors.copy()
    #                         )
    #                         data_node.add_child(child_node)
    #                         current_group_number += 1
    #                     else:
    #                         continue
    #                 data_node.children_group_number.append(current_group_number)
    #             else:
    #                 continue
    #     ancestors.remove(node_id)
    #     return

    # def create_data_tree(self, entry_file_pattern: str) -> List[DataNode]:
    #     """从文件模式创建数据树

    #     Args:
    #         entry_file_pattern: 文件路径模式，如 "root.yaml" 或 "**/root/*.yaml", 指定入口文件

    #     Returns:
    #         List[DataNode]: 匹配模式的数据树列表

    #     Raises:
    #         YamlError: 如果树创建过程中出现错误
    #     """
    #     # 重置状态
    #     # self._path_mapping.clear()
    #     # self._clear_mapping()
    #     data_tree_list = []

    #     if len(self.file_tree.children) == 0:
    #         return []

    #     try:
    #         # 处理每个匹配的文件
    #         for child in self.file_tree.find_nodes_by_path(entry_file_pattern):
    #             if isinstance(child, FileNode):
    #                 try:
    #                     data_node = self._build_data_tree(child)
    #                     data_tree_list.append(data_node)
    #                 except YamlError as e:
    #                     raise  # 重新抛出所有YAML错误
    #     except YamlError as e:
    #         data_tree_list = []  # 出错时清空列表
    #         raise

    #     return data_tree_list

    # def serialize_data_tree(self, root: DataNode, indent: int = 0) -> str:
    #     """序列化目录树为字符串"""
    #     # 转换到FileNode
    #     file_node = self._file_node_mapping.get(root, None)
    #     if file_node is None:
    #         return ""

    #     result = [" " * indent + file_node.get_absolute_path() + "/"]

    #     for child in root.children:
    #         if isinstance(child, DirectoryNode):
    #             result.append(
    #                 self.serialize_data_tree(cast(DataNode, child), indent + 2)
    #             )
    #         else:
    #             result.append(" " * (indent + 2) + child.name)

    #     return "\n".join(result)
