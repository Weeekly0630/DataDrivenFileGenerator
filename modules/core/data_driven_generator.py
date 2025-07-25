"""Data-driven generator module for Jinja Template"""

from typing import Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from . import (
    GeneratorError,
    GeneratorErrorType,
    DataHandler,
    TemplateHandler,
    validate_data_context,
    validate_render_result,
)
from .handler_factory import HandlerFactory
from .types import DataHandlerType, TemplateHandlerType
from ..node.data_node import DataNode
from ..jinja.user_func.func_handler import UserFunctionInfo, UserFunctionResolver


@dataclass
class DataDrivenGeneratorConfig:
    """Configuration for the DataDrivenGenerator"""

    data_type: DataHandlerType  # 数据处理器类型
    data_config: Dict[str, Any]  # 数据处理器配置
    template_type: TemplateHandlerType  # 模板处理器类型
    template_config: Dict[str, Any]  # 模板处理器配置

    preserved_template_key: str  # 指定字典树中的字典的保留模板键
    preserved_children_key: str  # 指定字典树中的字典的保留子节点键
    preserved_children_content_key: str  # 指定模板中引用子节点数据对象名称


class DataDrivenGenerator:
    """Data-driven generator class
    This class is responsible for generating data-driven templates based on provided data.
    """

    def __init__(
        self,
        config: DataDrivenGeneratorConfig,
    ) -> None:
        """Initialize the generator with configuration

        Args:
            config: Configuration for data and template handlers
        """
        self.data_handler = HandlerFactory.create_data_handler(
            config.data_type, config.data_config
        )
        self.template_handler = HandlerFactory.create_template_handler(
            config.template_type, config.template_config
        )
        self.config = config

    def _rendered_contents_init(self) -> None:
        # 存储渲染结果的映射
        self._rendered_contents: Dict[DataNode, str] = {}

    def render_by_pattern(self, pattern: str) -> str:
        """Render templates based on the provided pattern

        Args:
            pattern: Pattern to match data files

        Returns:
            Dict[str, str]: Rendered template contents keyed by node name

        Raises:
            GeneratorError: If rendering fails or no templates are found
        """
        # 1. 创建数据树
        root = self.data_handler.create_data_tree(
            {
                "pattern": pattern,
                "preserved_template_key": self.config.preserved_template_key,
                "preserved_children_key": self.config.preserved_children_key,
            }
        )
        if not root:
            raise GeneratorError(
                GeneratorErrorType.DATA_INIT_ERROR,
                f"No data files found matching pattern: {pattern}",
            )
        # 1.1 打印数据树
        print("\n==============Serialized Data Tree==============")
        print(root._parent.serialze())

        # 2. 后续遍历
        self._process_node(root)

        # 3. 取结果
        result = self._rendered_contents.get(root, "")

        return result

    def render(self, *args, **kvargs) -> str:
        """渲染模板"""
        # 清空之前的渲染结果
        self._rendered_contents_init()
        if "pattern" in kvargs:
            pattern = kvargs["pattern"]
            return self.render_by_pattern(pattern)
        else:
            return ""

    def _process_node(self, root: DataNode) -> None:
        """处理单个节点及其子节点

        采用后序遍历（先处理子节点再处理父节点）

        Args:
            node: 要处理的数据节点
        """

        def children_content_init(node: DataNode, preserved_key: str) -> None:
            """Initialize children content key in the node data"""
            if preserved_key not in node.data:
                node.data[preserved_key] = []

        def children_content_update(
            node: DataNode,
            preserved_key: str,
            rendered_content_map: Dict[DataNode, str],
        ) -> None:
            """Update children content key in the node data with rendered contents"""
            if len(node._parent._parent.children) == 0:
                # No children to update
                return
            else:
                # Current children node index
                children_index = 0
                # Get group number from parent
                for number in node.group_number:
                    # Initialize group content list
                    group_content = []
                    # Get the corresponding child node
                    for child in node._parent._parent.children[
                        children_index : children_index + number
                    ]:
                        obj = child.mapping_obj
                        if isinstance(obj, DataNode):
                            # Get rendered content for the child node
                            content = rendered_content_map.get(obj, "")
                            if content != "":
                                group_content.append(content)
                    # Update the preserved key with group content
                    node.data[preserved_key].append("\n".join(group_content))

        def visitor(node: DataNode) -> None:
            """Visitor function to process each node"""
            if not isinstance(node, DataNode):
                raise TypeError("Node must be an instance of DataNode")
            # 校验DataNode数据
            validate_data_context(node.data, self.config.preserved_children_key)
            validate_data_context(node.data, self.config.preserved_template_key)
            # 打印当前节点信息
            print(f"Processing node: {node._parent.meta_data.name}")
            # 初始化children_content
            children_content_init(node, self.config.preserved_children_content_key)
            # 更新children_content
            children_content_update(
                node,
                self.config.preserved_children_content_key,
                self._rendered_contents,
            )
            # 预处理复合表达式

            # 进行渲染
            try:
                template_path = node.data[self.config.preserved_template_key]
                # 渲染模板
                result = self.template_handler.render(template_path)
                # 验证渲染结果并保存
                validate_render_result(result, template_path)
                self._rendered_contents[node] = result
            except Exception as e:
                raise GeneratorError(
                    GeneratorErrorType.RENDER_ERROR,
                    f"Failed to render {template_path}: {str(e)}",
                )

        # 进行后序遍历
        root.post_traverse(visitor)