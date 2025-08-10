# 插件函数使用文档

本文档包含所有可用的插件函数及其使用方法。

## 目录

### 按类别浏览
{% for class_name in plugin_data.successful_classes %}
- [{{ class_name }} 类函数](#{{ class_name | lower }}-类函数)
{% endfor %}

### 所有函数列表
{% for class_name, functions_dict in plugin_data.registries.items() %}
{% for func_name, func_info in functions_dict.items() %}
- [{{ func_name }}](#{{ func_name | replace('_', '-') }})
{% endfor %}
{% endfor %}

---

## 函数收集摘要

- **总函数数**: {{ plugin_data.total_functions }}
- **成功收集的类**: {{ plugin_data.successful_classes | join(', ') }}
- **发现的类**: {{ plugin_data.discovered_classes | join(', ') }}
{% if plugin_data.failed_classes %}
- **收集失败的类**: {{ plugin_data.failed_classes | join(', ') }}
{% endif %}

---

{% for class_name, functions_dict in plugin_data.registries.items() %}
## {{ class_name }} 类函数

来源类：`{{ class_name }}`  
函数数量：{{ functions_dict | length }}

### 函数列表
{% for func_name, func_info in functions_dict.items() %}
- [{{ func_name }}](#{{ func_name | replace('_', '-') }})
{% endfor %}

{% for func_name, func_info in functions_dict.items() %}
<a id="{{ func_name | replace('_', '-') }}"></a>
### {{ func_name }}

**描述**：{{ func_info.description }}

{% if func_info.parameters %}
**参数列表**：
{% for param in func_info.parameters %}
- `{{ param.name }}`: {{ param.type_name }}
  {% if param.is_plugin_type %}
  - [{{ param.related_function }}](#{{ param.related_function | replace('_', '-') }})
  {% elif param.type_description %}
  - {{ param.type_description }}
  {% endif %}
{% endfor %}
{% else %}
无参数
{% endif %}



**函数签名**：
```python
{{ func_name }}({% for param in func_info.parameters %}{{ param.name }}{% if param.is_plugin_type %}: {{ param.related_function }}{% else %}: {{ param.type_name }}{% endif %}{% if not loop.last %}, {% endif %}{% endfor %})
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{% raw %}{{% endraw %}{{ func_name }}(
{% for param in func_info.parameters %}
    <{{ param.name }}_value>{% if not loop.last %},
    {% endif %}
{% endfor %}){% raw %}}{% endraw %}"
```

*带参数名的调用：*
```yaml
data: "{% raw %}{{% endraw %}
{{ func_name }}(
    {% for param in func_info.parameters %}
    {{ param.name }}=<{{ param.name }}_value>{% if not loop.last %},
    {% endif %}
    {% endfor %})
{% raw %}}{% endraw %}"
```

{% if func_info.parameters | selectattr('is_plugin_type') | list %}
*嵌套调用示例：*
```yaml
data: "{% raw %}{{% endraw %}
{{ func_name }}(
{% for param in func_info.parameters %}
    {% if param.is_plugin_type %}
    {{ param.name }}={{ param.related_function }}(<nested_params>)
    {%- else %}
    {{ param.name }}=<{{ param.name }}_value>
    {%- endif %}
    {%- if not loop.last -%}
    , 
    {% endif %}
{% endfor %}
)
{% raw %}}{% endraw %}"
```
{% endif %}

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{% raw %}{{% endraw %}{{ func_name }}({% for param in func_info.parameters %}{% if param.type_name == 'str' %}'example_{{ param.name }}'{% elif param.type_name == 'int' %}0{% elif param.type_name == 'bool' %}false{% elif param.type_name == 'List' %}[]{% elif param.is_plugin_type %}{{ param.related_function }}(){% else %}'{{ param.name }}_value'{% endif %}{% if not loop.last %}, {% endif %}{% endfor %}){% raw %}}{% endraw %}"

# 示例 2：在 f-string 中使用
example2: f"结果: {% raw %}{{% endraw %}{{ func_name }}({% for param in func_info.parameters %}{% if param.type_name == 'str' %}'demo'{% elif param.type_name == 'int' %}1{% elif param.type_name == 'bool' %}true{% elif param.type_name == 'List' %}['item1', 'item2']{% elif param.is_plugin_type %}{{ param.related_function }}(){% else %}'demo'{% endif %}{% if not loop.last %}, {% endif %}{% endfor %}){% raw %}}{% endraw %}"
```

{% if func_info.parameters | selectattr('is_plugin_type') | list %}
**相关函数**：
{% for param in func_info.parameters %}
{% if param.is_plugin_type %}
- [{{ param.related_function }}](#{{ param.related_function | replace('_', '-') }}) - 用于 `{{ param.name }}` 参数
{% endif %}
{% endfor %}
{% endif %}

---
{% endfor %}
{% endfor %}

## 使用指南

### 基本语法

1. **在表达式中使用**：
   ```yaml
   data: "{% raw %}{function_name(param1, param2)}{% endraw %}"
   ```

2. **在 f-string 中使用**：
   ```yaml
   data: f"结果是 {% raw %}{function_name(param1, param2)}{% endraw %}"
   ```

3. **嵌套函数调用**：
   ```yaml
   data: "{% raw %}{outer_function(inner_function(param1), param2)}{% endraw %}"
   ```

### 参数类型说明

- **str**: 字符串，需要用引号包围，如 `'example'`
- **int**: 整数，直接写数字，如 `42`
- **bool**: 布尔值，使用 `true` 或 `false`
- **List**: 列表，使用 `[]` 语法，如 `['item1', 'item2']`
- **Plugin类型**: 其他插件函数的返回值，可以嵌套调用

### 转义字符

在 YAML 中使用函数时，需要对大括号进行转义：
- 使用 `\\{% raw %}{{% endraw %}` 替代 `{% raw %}{{% endraw %}`
- 使用 `{% raw %}}{% endraw %}\\` 替代 `{% raw %}}{% endraw %}`

### 常见模式

1. **创建对象**：
   ```yaml
   object: "{% raw %}{create_function('name', 'type')}{% endraw %}"
   ```

2. **嵌套对象**：
   ```yaml
   complex_object: "{% raw %}{parent_create(
     child=child_create('child_name'),
     other_param='value'
   )}{% endraw %}"
   ```

3. **列表操作**：
   ```yaml
   list_data: "{% raw %}{list_function(['item1', 'item2', 'item3'])}{% endraw %}"
   ```

## 附录

### 生成信息

- 总函数数：{{ plugin_data.total_functions }}
- 成功收集的类：{{ plugin_data.successful_classes | join(', ') }}
{% if plugin_data.failed_classes %}
- 收集失败的类：{{ plugin_data.failed_classes | join(', ') }}
{% endif %}
