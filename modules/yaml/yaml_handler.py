import yaml
from typing import Optional, List, Dict, Any, Iterator, cast
from dataclasses import dataclass
from pathlib import Path

from .errors import (
    YamlError,
    YamlConfigError,
    YamlPathError,
    YamlLoadError,
    YamlStructureError,
)
from ..node.data_node import DataNode
from ..node.file_node import DirectoryNode, FileNode
from ..core import DataHandler


@dataclass
class YamlConfig:
    """YAML配置，包含模板和子节点路径的保留键"""

    root_path: Path
    file_pattern: List[str]
    encoding: str = "utf-8"
    preserved_template_key: str = "TEMPLATE_PATH"
    preserved_children_key: str = "CHILDREN_PATH"
    max_depth: int = 1000  # 递归的最大深度

    @classmethod
    def validate(cls, config: Dict[str, Any]) -> "YamlConfig":
        """验证配置并返回配置对象

        Args:
            config: 配置字典
                必需字段:
                    - root_path: YAML文件的根路径
                可选字段:
                    - encoding: 文件编码 (默认: utf-8)
                    - preserved_template_key: 模板路径键名 (默认: TEMPLATE_PATH)
                    - preserved_children_key: 子节点路径键名 (默认: CHILDREN_PATH)

        Raises:
            YamlConfigError: 如果缺少必需字段
            YamlPathError: 如果根路径不存在
        """
        if "root_path" not in config:
            raise YamlConfigError("Missing required field 'root_path'")

        root_path = Path(config["root_path"])
        if not root_path.exists():
            raise YamlPathError(f"root_path {root_path} does not exist", str(root_path))

        return cls(
            root_path=root_path,
            file_pattern=config.get("file_pattern", ["*.yaml"]),
            encoding=config.get("encoding", "utf-8"),
            preserved_template_key=config.get(
                "preserved_template_key", "TEMPLATE_PATH"
            ),
            preserved_children_key=config.get(
                "preserved_children_key", "CHILDREN_PATH"
            ),
        )


class _YamlFileHandler:
    """内部使用的YAML文件处理类"""

    @staticmethod
    def _load_yaml_file(yaml_path: str) -> dict:
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
                return data
        except (IOError, yaml.YAMLError) as e:
            raise YamlLoadError(str(e), yaml_path)


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
        # self._path_mapping: Dict[str, DataNode] = {}  # 文件路径到数据节点的映射

        # DataNode 映射到 FileNode
        self._file_node_mapping: Dict[DataNode, FileNode] = {}

        # FileNode 映射到 DataNode
        self._data_node_mapping: Dict[FileNode, DataNode] = {}

        # 初始化文件树
        self.file_tree: DirectoryNode = DirectoryNode(
            dir_name=str(self.config.root_path)
        )
        self._file_tree_init()

    @property
    def preserved_template_key(self) -> str:
        """获取模板路径的键名"""
        return self.config.preserved_template_key

    @property
    def preserved_children_key(self) -> str:
        """获取子节点路径的键名"""
        return self.config.preserved_children_key

    def _add_mapping(self, data_node: DataNode, file_node: FileNode) -> None:
        self._file_node_mapping[data_node] = file_node
        self._data_node_mapping[file_node] = data_node

    def _clear_mapping(self) -> None:
        self._file_node_mapping.clear()
        self._data_node_mapping.clear()

    def get_absolute_path(self, node: DataNode) -> str:
        """获取节点的文件绝对路径

        Args:
            node: 数据节点

        Returns:
            str: 节点的绝对路径
        """
        return str(self.config.root_path.resolve()) + node.get_absolute_path()

    def _file_tree_init(self) -> None:
        """初始化文件树结构

        根据配置的根路径和文件模式构建文件树。
        不直接访问此方法，它由__init__自动调用。
        """
        self.file_tree.build_tree(
            str(self.config.root_path), patterns=self.config.file_pattern
        )

    def find_by_file_path(self, node: DataNode, pattern: str) -> List[DataNode]:
        """根据文件路径模式查找数据节点

        Args:
            pattern: 文件路径模式，如 "*.yaml" 或 "**/config/*.yaml"

        Returns:
            List[DataNode]: 匹配的数据节点列表
        """
        # Get file node from mapping
        file_node: Optional[FileNode] = self._file_node_mapping.get(node, None)
        if file_node is None:
            pass

        found_node = cast(DirectoryNode, file_node.parent).find_nodes_by_path(pattern)
        result: List[DataNode] = []
        for node in found_node:
            if isinstance(node, FileNode):
                # Get data node from mapping
                data_node = self._data_node_mapping.get(node)
                if data_node:
                    result.append(data_node)
        return result

    def _data_node_create(self, file_node: FileNode, depth: int) -> DataNode:
        """从文件节点创建数据节点

        Args:
            file_node: 文件节点
            depth: 当前递归深度

        Returns:
            DataNode: 创建的数据节点

        Raises:
            YamlStructureError: 如果递归深度超限或缺少必要字段
            YamlLoadError: 如果文件加载失败
        """
        if depth > self.config.max_depth:
            raise YamlStructureError.max_depth_exceeded(
                self.config.max_depth, file_node.name
            )
            
        file_system_path: str = str(
            self.config.root_path
        ) + file_node.get_absolute_path(slice_range=(1, None))
        
        data = _YamlFileHandler._load_yaml_file(file_system_path)
        if data:
            # 创建数据节点并存入映射
            data_node = DataNode(data=data, name=file_node.name)

            # Add data node to file node mapping
            self._add_mapping(data_node, file_node)

            # 验证必要字段
            for key in [self.preserved_template_key, self.preserved_children_key]:
                if key not in data:
                    raise YamlStructureError.missing_key(key, file_system_path)

            # 处理子节点
            children_path = data_node.data[self.preserved_children_key]
            
            if children_path == "":  # 空字符串视为空列表
                children_path = []
            if children_path:
                if isinstance(children_path, str):
                    children_path = [children_path]  # 转换单个字符串为列表
                elif isinstance(children_path, list):
                    pass  # 已经是列表

                # 为每个模式创建子节点, 同时将他们分组
                for paths in children_path:
                    if not paths:  # 跳过空路径
                        continue
                    patterns = []
                    if isinstance(paths, str):
                        patterns = [paths]
                    elif isinstance(paths, list):
                        patterns = paths
                    else:
                        raise YamlStructureError.invalid_children(
                            f"Invalid children path specification: {paths}",
                            file_system_path,
                        )
                    # 处理每个模式
                    for pattern in patterns:
                        current_group_number = 0
                        if not pattern:  # 跳过空模式
                            continue
                        if file_node.parent:
                            matching_files = cast(
                                DirectoryNode, file_node.parent
                            ).find_nodes_by_path(pattern)
                            for matching_file in matching_files:
                                if isinstance(matching_file, FileNode):
                                    try:
                                        child_node = self._data_node_create(
                                            matching_file, depth + 1
                                        )
                                        data_node.add_child(child_node)
                                        current_group_number += 1
                                    except YamlError as e:
                                        # 重新抛出异常，添加子节点处理失败的上下文
                                        raise YamlStructureError(
                                            e.error_type,
                                            f"Error processing child {matching_file.name}: {str(e)}",
                                            str(matching_file.get_absolute_path()),
                                        ) from e
                        data_node.children_group_number.append(current_group_number)
                                        
        else:
            raise YamlLoadError(f"Failed to load data", file_system_path)
        return data_node

    def create_data_tree(self, pattern: str) -> List[DataNode]:
        """从文件模式创建数据树

        Args:
            pattern: 文件路径模式，如 "root.yaml" 或 "**/root/*.yaml"

        Returns:
            List[DataNode]: 匹配模式的数据树列表

        Raises:
            YamlError: 如果树创建过程中出现错误
        """
        # 重置状态
        # self._path_mapping.clear()
        self._clear_mapping()
        data_tree_list = []

        if len(self.file_tree.children) == 0:
            return []

        try:
            # 处理每个匹配的文件
            for child in self.file_tree.find_nodes_by_path(pattern):
                if isinstance(child, FileNode):
                    try:
                        data_node = self._data_node_create(child, 0)
                        data_tree_list.append(data_node)
                    except YamlError as e:
                        raise  # 重新抛出所有YAML错误
        except YamlError as e:
            data_tree_list = []  # 出错时清空列表
            raise

        return data_tree_list
