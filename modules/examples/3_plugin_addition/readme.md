# 插件拓展

通过在modules/jinja/user_function/plugins下添加拓展python文件。可以在Jinja2模板中使用自定义过滤器。

## 1.内容简介

### Jinja2过滤器

在Jinja2模板中使用自定义过滤器，可以通过`{{ value | filter_name }}`的方式调用。
例如：
```jinja2
{{ "hello world" | upper }}
```
生成结果为：
```text
HELLO WORLD
```

### 预留过滤器及Expression AST

在JinjaHandler中预留了过滤器`expr_filter`， 可以在模板中使用`{{ value | expr_filter }}`来调用。
expr_filter将数据解析为AST树，并执行AST树中的表达式。

AST节点分为多种类型：

```python
class ExprNodeType(Enum):
    XPATH = auto()  # XPath表达式
    FUNCTION = auto()  # 函数调用
    EXPRESSION = auto()  # 复合表达式
    LITERAL = auto()  # 字面量常数
```

通过value中的`type`键指定节点类型, 通过`args`传递相关数据.
例如一个function节点可以这样定义：

```yaml
function_node:
  type: function
  args: [function_name, arg1, arg2]
```

对于一个function节点，`args`中的第一个元素是函数名，后续元素是函数参数。expr_filter将根据函数名查找plugins中对应注册的函数，并执行。

### 添加插件

在plugins目录下实现一个`FunctionPlugin`类
```python
class FunctionPlugin:
    """插件基类，支持静态和动态函数"""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """返回插件提供的静态函数列表（与节点无关）"""
        return []

    @classmethod
    def dynamic_functions(cls, node: DataNode, data_handler: DataHandler) -> List[UserFunctionInfo]:
        """返回插件提供的动态函数列表（需要节点上下文以及节点树上下文）"""
        return []

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
```
在JinjaHandler中，会初始化一个`UserFunctionResolverFactory`实例用来加载所有插件。在渲染模板时，JinjaHandler会调用`UserFunctionResolverFactory`的`create_resolver`方法生成DataNode对应的`expr_filter`函数，并注册到Jinja Env中，以便提供含节点上下文的过滤器函数。

---
### 实现示例
例如有如下实现：
```python
@classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """静态数学函数"""
        return [
            UserFunctionInfo(
                name="math:square",
                arg_range=(1, 1),
                description="Calculate the square of a number",
                handler=lambda x: x * x,
            ),
            UserFunctionInfo(
                name="math:sum",
                arg_range=(2, None),
                description="Sum all arguments",
                handler=lambda *args: sum(args),
            ),
        ]

    @classmethod
    def dynamic_functions(cls, node: DataNode, data_handler: DataHandler) -> List[UserFunctionInfo]:
        """动态数学函数（使用节点上下文）"""
        return [
            UserFunctionInfo(
                name="math:node_value",
                arg_range=(0, 0),
                description="Get current node's numeric value",
                handler=lambda: float(node.data.get("value", 0)),
            ),
            UserFunctionInfo(
                name="math:children_sum",
                arg_range=(0, 0),
                description="Sum values of all child nodes",
                handler=lambda: sum(
                    (
                        float(child.data.get("value", 0))
                        if isinstance(child, DataNode)
                        else 0
                    )
                    for child in node.children
                ),
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        print(
            f"MathUtilsPlugin loaded with {len(cls.static_functions())} static functions"
        )

    @classmethod
    def on_plugin_unload(cls):
        print("MathUtilsPlugin unloaded")
```