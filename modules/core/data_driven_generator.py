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

    data_type: DataHandlerType
    data_config: Dict[str, Any]
    template_type: TemplateHandlerType
    template_config: Dict[str, Any]


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

        # 存储渲染结果的映射
        self._rendered_contents: Dict[DataNode, str] = {}

    def render(self, pattern: str) -> Dict[str, str]:
        """渲染模板并返回结果

        Args:
            pattern: 用于查找数据文件的模式，如 "root.yaml"

        Returns:
            Dict[str, str]: 文件名到渲染结果的映射

        Raises:
            GeneratorError: 如果数据验证或渲染失败
        """
        # 清空之前的渲染结果
        self._rendered_contents.clear()
        results = {}

        # 1. 创建数据树
        trees = self.data_handler.create_data_tree(pattern)
        if not trees:
            raise GeneratorError(
                GeneratorErrorType.DATA_INIT_ERROR,
                f"No data files found matching pattern: {pattern}",
            )
        # 1.1 打印数据树
        print("\n==============Serialized Data Tree==============")
        for root in trees:
            print(self.data_handler.serialize_data_tree(root))

        # 2. 对每个树进行后序遍历和渲染
        for root in trees:
            self._process_node(root)
            key = f"{root.name}"
            results[key] = self._rendered_contents[root]

        if not results:
            raise GeneratorError(
                GeneratorErrorType.RENDER_ERROR, "No templates were rendered"
            )

        return results

    def _process_node(self, node: DataNode) -> None:
        """处理单个节点及其子节点

        采用后序遍历（先处理子节点再处理父节点）

        Args:
            node: 要处理的数据节点
        """
        # 1. 先处理所有子节点
        for child in node.children:
            if isinstance(child, DataNode):
                self._process_node(child)

        # 2. 验证数据
        validate_data_context(node.data, self.data_handler.preserved_template_key)
        print(
            f"Processing node: {node.name} with children{node.children_group_number}: {[child.name for child in node.children]}"
        )

        def children_content_init(
            cur_node: DataNode,
            preserved_key: str,
            render_content_map: Dict[DataNode, str],
        ) -> None:
            """初始化子节点内容"""
            current_children_index = 0

            if preserved_key not in cur_node.data:
                # 如果没有preserved_children_key，初始化为空列表
                cur_node.data[preserved_key] = []

            if len(cur_node.children_group_number) == 0:
                # 如果没有分组信息, 保留数据不动
                pass
            else:
                # 根据分组信息初始化对应组的内容
                for group_index, group_number in enumerate(
                    cur_node.children_group_number
                ):
                    children_content: Union[List[str], str] = []
                    print(f"    Processing group {group_index}: {group_number}")
                    # 从children中取number个子节点
                    for child_index in range(
                        current_children_index, current_children_index + group_number
                    ):
                        if child_index < len(cur_node.children):
                            child = cur_node.children[child_index]
                            if (
                                isinstance(child, DataNode)
                                and child in render_content_map
                            ):
                                children_content.append(render_content_map[child])

                    # 5. 添加子节点内容到上下文
                    if len(children_content) > 0:
                        cur_node.data[preserved_key].append("\n".join(children_content))

                    # 更新当前子节点索引
                    current_children_index += group_number

        # Children content initialization
        children_content_init(
            node, self.template_handler.preserved_children_key, self._rendered_contents
        )

        # 预处理放在子节点渲染后
        self.data_handler.preprocess_expr(node)

        try:
            template_path = node.data[self.data_handler.preserved_template_key]

            # 6. 渲染模板
            result = self.template_handler.render_template(
                template_path, node, self.data_handler
            )

            # 7. 验证结果并保存
            validate_render_result(result, template_path)
            self._rendered_contents[node] = result

        except Exception as e:
            raise GeneratorError(
                GeneratorErrorType.RENDER_ERROR,
                f"Failed to render {template_path}: {str(e)}",
            )