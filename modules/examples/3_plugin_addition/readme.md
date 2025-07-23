# Plugin Extension Example

This example demonstrates how to extend the template rendering system by adding custom Jinja filters and Python function plugins.

## Overview

### What is a Jinja Filter?

A Jinja filter is a function that transforms the value of a variable in a template. Filters are applied using the pipe (`|`) syntax in Jinja templates.
For example:
```jinja2
{{ "hello world" | upper }}
```
Result:
```text
HELLO WORLD
```

### Preserved Filter: `expr_filter` and Expression AST

The [`jinja_handler`](modules/jinja/jinja_handler.py:1) provides a preserved filter called [`expr_filter`](modules/jinja/expr_filter.py:1), which can be used in templates as `{{ value | expr_filter }}`.
`expr_filter` parses the input data as an AST (Abstract Syntax Tree) and evaluates the expression.

AST nodes include several types:
```python
class ExprNodeType(Enum):
    XPATH = auto()      # XPath expression
    FUNCTION = auto()   # Function call
    EXPRESSION = auto() # Composite expression
    LITERAL = auto()    # Literal constant
```
Specify the node type with the `type` key in the value, and pass related data via `args`.
For example, a function node can be defined as:
```yaml
function_node:
  type: function
  args: [function_name, arg1, arg2]
```
For a function node, the first element in `args` is the function name, and the rest are arguments.
`expr_filter` will look up the corresponding registered function in plugins and execute it.

### Context Variable: `__context__`

When rendering, the handler injects a special variable `__context__` into the template, providing access to the current rendering context (such as the current node and data tree).

### Adding Plugins

To add a plugin, implement a `FunctionPlugin` class in the `plugins` directory:
```python
class FunctionPlugin:
    """Base class for plugins, supporting static and dynamic functions."""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """Return static functions provided by the plugin (not node-dependent)."""
        return []

    @classmethod
    def dynamic_functions(cls, node: DataNode, data_handler: DataHandler) -> List[UserFunctionInfo]:
        """Return dynamic functions (require node and context)."""
        return []

    @classmethod
    def on_plugin_load(cls):
        """Initialization when plugin loads (optional)."""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """Cleanup when plugin unloads (optional)."""
        pass
```
The [`jinja_handler`](modules/jinja/jinja_handler.py:1) initializes a `UserFunctionResolverFactory` to load all plugins.
When rendering, it calls `create_resolver` to generate the `expr_filter` function for each `DataNode`, registering it in the Jinja environment so filters have access to node context.

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