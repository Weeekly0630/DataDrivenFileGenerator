# Jinja2过滤器

此文档介绍如何使用jinja2过滤器函数调用用户自定义函数。

## 1.内容简介

jinja2提供了一个过滤器以便在模板中通过管道`|`调用注册的过滤器函数。用户可以通过在`jinja/user_func/plugins`中通过对template_plugins.py的拓展，实现自己的函数。

### 2.Jinja2过滤器

在Jinja2模板中使用自定义过滤器，可以通过`{{ value | filter_name }}`的方式调用。
例如：

```jinja2
{{ "hello world" | upper }}
```

生成结果为：

```text
HELLO WORLD
```

### 3.预留过滤器以及表达式树

在JinjaHandler中预留了过滤器`expr_filter`， 可以在模板中使用`{{ value | expr_filter }}`来调用。
expr_filter通过将一个字典数据根据其`type`及`args`解析为一个ExprNode树。一个expr节点分为如下类型：

```python
class ExprNodeType(Enum):
    XPATH = auto()  # XPath表达式
    FUNCTION = auto()  # 函数调用
    EXPRESSION = auto()  # 复合表达式
    LITERAL = auto()  # 字面量常数
```

#### 3.1 XPath Node

expr数据：

```yaml
expr:
    type: "xpath"
    args: [ExprNode(), ...]
```

渲染结果：
将args中的每一项进行递归渲染，最后使用`"/"`将结果拼接起来

#### 3.2 Function Node

expr数据:

```yaml
expr:
    type: "function"
    args: [str, ExprNode(), ...]
```

args中第一个参数表示函数名，后续参数表示函数的参数。如果函数存在，则将参数进行递归解析，并将解析结果作为参数进行函数调用。

渲染结果：
str(函数输出对象)

#### 3.3 Expression Node

expr数据:

```yaml
expr: 
    type: "expression"
    args: [str, ExprNode(), ...]
```

args第一个参数作为表达式的符号，后续项作为表达式的各个项。
渲染结果：
((arg1) op (arg2) op ...)

### 4. 函数调用

#### 4.1 FunctionResolverFactory

在JinjaHandler初始化时，会初始化一个`UserFunctionResolverFactory`用户函数处理工厂。其负责:

- plugin函数信息收集管理
- UserFunctionResolver对象的创建及渲染节点上下文传递

在遍历FunctionNode时，会查找当前函数是否注册在当前`UserFunctionResolver`中。
若已注册，则检查参数个数，执行validator函数，最后执行handler.
