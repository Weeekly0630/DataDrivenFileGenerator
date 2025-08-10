# 插件函数使用文档

本文档包含所有可用的插件函数及其使用方法。

## 目录

### 按类别浏览
- [Decl 类函数](#decl-类函数)
- [Node 类函数](#node-类函数)

### 所有函数列表
- [插件函数使用文档](#插件函数使用文档)
  - [目录](#目录)
    - [按类别浏览](#按类别浏览)
    - [所有函数列表](#所有函数列表)
  - [函数收集摘要](#函数收集摘要)
  - [Decl 类函数](#decl-类函数)
    - [函数列表](#函数列表)
    - [decl\_field\_create](#decl_field_create)
    - [decl\_record\_create](#decl_record_create)
    - [decl\_struct\_create](#decl_struct_create)
    - [decl\_typemodifier\_create](#decl_typemodifier_create)
    - [decl\_typeref\_create](#decl_typeref_create)
    - [decl\_typedef\_create](#decl_typedef_create)
    - [decl\_union\_create](#decl_union_create)
    - [decl\_variable\_create](#decl_variable_create)
  - [Node 类函数](#node-类函数)
    - [函数列表](#函数列表-1)
    - [node\_find\_create](#node_find_create)
    - [node\_value\_create](#node_value_create)
  - [使用指南](#使用指南)
    - [基本语法](#基本语法)
    - [参数类型说明](#参数类型说明)
    - [转义字符](#转义字符)
    - [常见模式](#常见模式)
  - [附录](#附录)
    - [生成信息](#生成信息)

---

## 函数收集摘要

- **总函数数**: 10
- **成功收集的类**: Decl, Node
- **发现的类**: Decl, Node

---

## Decl 类函数

来源类：`Decl`  
函数数量：8

### 函数列表
- [插件函数使用文档](#插件函数使用文档)
  - [目录](#目录)
    - [按类别浏览](#按类别浏览)
    - [所有函数列表](#所有函数列表)
  - [函数收集摘要](#函数收集摘要)
  - [Decl 类函数](#decl-类函数)
    - [函数列表](#函数列表)
    - [decl\_field\_create](#decl_field_create)
    - [decl\_record\_create](#decl_record_create)
    - [decl\_struct\_create](#decl_struct_create)
    - [decl\_typemodifier\_create](#decl_typemodifier_create)
    - [decl\_typeref\_create](#decl_typeref_create)
    - [decl\_typedef\_create](#decl_typedef_create)
    - [decl\_union\_create](#decl_union_create)
    - [decl\_variable\_create](#decl_variable_create)
  - [Node 类函数](#node-类函数)
    - [函数列表](#函数列表-1)
    - [node\_find\_create](#node_find_create)
    - [node\_value\_create](#node_value_create)
  - [使用指南](#使用指南)
    - [基本语法](#基本语法)
    - [参数类型说明](#参数类型说明)
    - [转义字符](#转义字符)
    - [常见模式](#常见模式)
  - [附录](#附录)
    - [生成信息](#生成信息)

<a id="decl-field-create"></a>
### decl_field_create

**描述**：C语言结构/联合字段信息

**参数列表**：
- `name`: str
  - 名称字符串
- `modifier`: decl_typemodifier_create
  - [decl_typemodifier_create](#decl-typemodifier-create)
- `bitfield_width`: int
  - 整数值



**函数签名**：
```python
decl_field_create(name: str, modifier: decl_typemodifier_create, bitfield_width: int)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_field_create(
    <name_value>,
    <modifier_value>,
    <bitfield_width_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_field_create(
    name=<name_value>,
    modifier=<modifier_value>,
    bitfield_width=<bitfield_width_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_field_create(
    name=<name_value>, 
    modifier=decl_typemodifier_create(<nested_params>), 
    bitfield_width=<bitfield_width_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_field_create('example_name', decl_typemodifier_create(), 0)}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_field_create('demo', decl_typemodifier_create(), 1)}"
```

**相关函数**：
- [decl_typemodifier_create](#decl-typemodifier-create) - 用于 `modifier` 参数

---
<a id="decl-record-create"></a>
### decl_record_create

**描述**：C语言结构体/联合体信息

**参数列表**：
- `name`: str
  - 名称字符串
- `fields`: decl_field_create
  - [decl_field_create](#decl-field-create)
- `attributes`: List
  - 列表类型
- `qualifiers`: str
  - 限定符字符串



**函数签名**：
```python
decl_record_create(name: str, fields: decl_field_create, attributes: List, qualifiers: str)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_record_create(
    <name_value>,
    <fields_value>,
    <attributes_value>,
    <qualifiers_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_record_create(
    name=<name_value>,
    fields=<fields_value>,
    attributes=<attributes_value>,
    qualifiers=<qualifiers_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_record_create(
    name=<name_value>, 
    fields=decl_field_create(<nested_params>), 
    attributes=<attributes_value>, 
    qualifiers=<qualifiers_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_record_create('example_name', decl_field_create(), [], 'example_qualifiers')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_record_create('demo', decl_field_create(), ['item1', 'item2'], 'demo')}"
```

**相关函数**：
- [decl_field_create](#decl-field-create) - 用于 `fields` 参数

---
<a id="decl-struct-create"></a>
### decl_struct_create

**描述**：C语言结构体信息

**参数列表**：
- `record`: Any
  - 任意类型



**函数签名**：
```python
decl_struct_create(record: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_struct_create(
    <record_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_struct_create(
    record=<record_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_struct_create('record_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_struct_create('demo')}"
```


---
<a id="decl-typemodifier-create"></a>
### decl_typemodifier_create

**描述**：C语言类型修饰符信息

**参数列表**：
- `type`: decl_typeref_create
  - [decl_typeref_create](#decl-typeref-create)
- `qualifiers`: str
  - 限定符字符串
- `attributes`: List
  - 列表类型
- `is_pointer`: bool
  - 布尔值
- `pointer_level`: int
  - 整数值
- `is_array`: bool
  - 布尔值
- `array_dims`: List
  - 列表类型



**函数签名**：
```python
decl_typemodifier_create(type: decl_typeref_create, qualifiers: str, attributes: List, is_pointer: bool, pointer_level: int, is_array: bool, array_dims: List)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_typemodifier_create(
    <type_value>,
    <qualifiers_value>,
    <attributes_value>,
    <is_pointer_value>,
    <pointer_level_value>,
    <is_array_value>,
    <array_dims_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_typemodifier_create(
    type=<type_value>,
    qualifiers=<qualifiers_value>,
    attributes=<attributes_value>,
    is_pointer=<is_pointer_value>,
    pointer_level=<pointer_level_value>,
    is_array=<is_array_value>,
    array_dims=<array_dims_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_typemodifier_create(
    type=decl_typeref_create(<nested_params>), 
    qualifiers=<qualifiers_value>, 
    attributes=<attributes_value>, 
    is_pointer=<is_pointer_value>, 
    pointer_level=<pointer_level_value>, 
    is_array=<is_array_value>, 
    array_dims=<array_dims_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_typemodifier_create(decl_typeref_create(), 'example_qualifiers', [], false, 0, false, [])}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_typemodifier_create(decl_typeref_create(), 'demo', ['item1', 'item2'], true, 1, true, ['item1', 'item2'])}"
```

**相关函数**：
- [decl_typeref_create](#decl-typeref-create) - 用于 `type` 参数

---
<a id="decl-typeref-create"></a>
### decl_typeref_create

**描述**：C语言类型引用信息

**参数列表**：
- `ref`: decl_typeref_create
  - [decl_typeref_create](#decl-typeref-create)



**函数签名**：
```python
decl_typeref_create(ref: decl_typeref_create)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_typeref_create(
    <ref_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_typeref_create(
    ref=<ref_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_typeref_create(
    ref=decl_typeref_create(<nested_params>))
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_typeref_create(decl_typeref_create())}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_typeref_create(decl_typeref_create())}"
```

**相关函数**：
- [decl_typeref_create](#decl-typeref-create) - 用于 `ref` 参数

---
<a id="decl-typedef-create"></a>
### decl_typedef_create

**描述**：C语言类型定义信息

**参数列表**：
- `name`: str
  - 名称字符串
- `typeref`: decl_typeref_create
  - [decl_typeref_create](#decl-typeref-create)



**函数签名**：
```python
decl_typedef_create(name: str, typeref: decl_typeref_create)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_typedef_create(
    <name_value>,
    <typeref_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_typedef_create(
    name=<name_value>,
    typeref=<typeref_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_typedef_create(
    name=<name_value>, 
    typeref=decl_typeref_create(<nested_params>))
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_typedef_create('example_name', decl_typeref_create())}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_typedef_create('demo', decl_typeref_create())}"
```

**相关函数**：
- [decl_typeref_create](#decl-typeref-create) - 用于 `typeref` 参数

---
<a id="decl-union-create"></a>
### decl_union_create

**描述**：C语言联合体信息

**参数列表**：
- `record`: Any
  - 任意类型



**函数签名**：
```python
decl_union_create(record: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_union_create(
    <record_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_union_create(
    record=<record_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_union_create('record_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_union_create('demo')}"
```


---
<a id="decl-variable-create"></a>
### decl_variable_create

**描述**：C语言变量信息

**参数列表**：
- `name`: str
  - 名称字符串
- `modifier`: decl_typemodifier_create
  - [decl_typemodifier_create](#decl-typemodifier-create)
- `init_expr`: Any
  - 初始化表达式



**函数签名**：
```python
decl_variable_create(name: str, modifier: decl_typemodifier_create, init_expr: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_variable_create(
    <name_value>,
    <modifier_value>,
    <init_expr_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_variable_create(
    name=<name_value>,
    modifier=<modifier_value>,
    init_expr=<init_expr_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_variable_create(
    name=<name_value>, 
    modifier=decl_typemodifier_create(<nested_params>), 
    init_expr=<init_expr_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_variable_create('example_name', decl_typemodifier_create(), 'init_expr_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_variable_create('demo', decl_typemodifier_create(), 'demo')}"
```

**相关函数**：
- [decl_typemodifier_create](#decl-typemodifier-create) - 用于 `modifier` 参数

---
## Node 类函数

来源类：`Node`  
函数数量：2

### 函数列表
- [node_find_create](#node-find-create)
- [node_value_create](#node-value-create)

<a id="node-find-create"></a>
### node_find_create

**描述**：查找数据节点的结果

**参数列表**：
- `results`: Any
  - 任意类型



**函数签名**：
```python
node_find_create(results: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{node_find_create(
    <results_value>)}"
```

*带参数名的调用：*
```yaml
data: "{node_find_create(
    results=<results_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{node_find_create('results_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {node_find_create('demo')}"
```


---
<a id="node-value-create"></a>
### node_value_create

**描述**：引用节点值的元数据

**参数列表**：
- `value`: Any
  - 任意类型



**函数签名**：
```python
node_value_create(value: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{node_value_create(
    <value_value>)}"
```

*带参数名的调用：*
```yaml
data: "{node_value_create(
    value=<value_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{node_value_create('value_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {node_value_create('demo')}"
```


---

## 使用指南

### 基本语法

1. **在表达式中使用**：
   ```yaml
   data: "{function_name(param1, param2)}"
   ```

2. **在 f-string 中使用**：
   ```yaml
   data: f"结果是 {function_name(param1, param2)}"
   ```

3. **嵌套函数调用**：
   ```yaml
   data: "{outer_function(inner_function(param1), param2)}"
   ```

### 参数类型说明

- **str**: 字符串，需要用引号包围，如 `'example'`
- **int**: 整数，直接写数字，如 `42`
- **bool**: 布尔值，使用 `true` 或 `false`
- **List**: 列表，使用 `[]` 语法，如 `['item1', 'item2']`
- **Plugin类型**: 其他插件函数的返回值，可以嵌套调用

### 转义字符

在 YAML 中使用函数时，需要对大括号进行转义：
- 使用 `\\{` 替代 `{`
- 使用 `}\\` 替代 `}`

### 常见模式

1. **创建对象**：
   ```yaml
   object: "{create_function('name', 'type')}"
   ```

2. **嵌套对象**：
   ```yaml
   complex_object: "{parent_create(
     child=child_create('child_name'),
     other_param='value'
   )}"
   ```

3. **列表操作**：
   ```yaml
   list_data: "{list_function(['item1', 'item2', 'item3'])}"
   ```

## 附录

### 生成信息

- 总函数数：10
- 成功收集的类：Decl, Node
