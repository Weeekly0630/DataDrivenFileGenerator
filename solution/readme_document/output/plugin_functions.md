# 插件函数使用文档

本文档包含所有可用的插件函数及其使用方法。

## 目录

### 按类别浏览
- [Node 类函数](#node-类函数)
- [Decl 类函数](#decl-类函数)
- [Preprocess 类函数](#preprocess-类函数)
- [XdmA 类函数](#xdma-类函数)
- [XdmAttribute 类函数](#xdmattribute-类函数)

### 所有函数列表
- [node_find_create](#node-find-create)
- [node_value_create](#node-value-create)
- [decl_field_create](#decl-field-create)
- [decl_function_create](#decl-function-create)
- [decl_param_create](#decl-param-create)
- [decl_record_create](#decl-record-create)
- [decl_struct_create](#decl-struct-create)
- [decl_typemodifier_create](#decl-typemodifier-create)
- [decl_typeref_create](#decl-typeref-create)
- [decl_typedef_create](#decl-typedef-create)
- [decl_union_create](#decl-union-create)
- [decl_variable_create](#decl-variable-create)
- [preprocess_inclusiondirective_create](#preprocess-inclusiondirective-create)
- [preprocess_macrodefinition_create](#preprocess-macrodefinition-create)
- [preprocess_macroinstantiation_create](#preprocess-macroinstantiation-create)
- [xdma_bswmoduledescblock_create](#xdma-bswmoduledescblock-create)
- [xdma_checkbox_create](#xdma-checkbox-create)
- [xdma_combobox_create](#xdma-combobox-create)
- [xdma_ecuparamdefblock_create](#xdma-ecuparamdefblock-create)
- [xdma_inputbox_create](#xdma-inputbox-create)
- [xdma_mainpage_create](#xdma-mainpage-create)
- [xdma_maptable_create](#xdma-maptable-create)
- [xdma_moduleblock_create](#xdma-moduleblock-create)
- [xdma_moduledefblock_create](#xdma-moduledefblock-create)
- [xdma_orderedtable_create](#xdma-orderedtable-create)
- [xdma_referencebox_create](#xdma-referencebox-create)
- [xdmattribute_node_create](#xdmattribute-node-create)

---

## 函数收集摘要

- **总函数数**: 27
- **成功收集的类**: Node, Decl, Preprocess, XdmA, XdmAttribute
- **发现的类**: Node, Decl, Preprocess, XdmA, XdmAttribute

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
## Decl 类函数

来源类：`Decl`  
函数数量：10

### 函数列表
- [decl_field_create](#decl-field-create)
- [decl_function_create](#decl-function-create)
- [decl_param_create](#decl-param-create)
- [decl_record_create](#decl-record-create)
- [decl_struct_create](#decl-struct-create)
- [decl_typemodifier_create](#decl-typemodifier-create)
- [decl_typeref_create](#decl-typeref-create)
- [decl_typedef_create](#decl-typedef-create)
- [decl_union_create](#decl-union-create)
- [decl_variable_create](#decl-variable-create)

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
- `raw_code`: Any
  - 任意类型
- `comment`: Any
  - 任意类型



**函数签名**：
```python
decl_field_create(name: str, modifier: decl_typemodifier_create, bitfield_width: int, raw_code: Any, comment: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_field_create(
    <name_value>,
    <modifier_value>,
    <bitfield_width_value>,
    <raw_code_value>,
    <comment_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_field_create(
    name=<name_value>,
    modifier=<modifier_value>,
    bitfield_width=<bitfield_width_value>,
    raw_code=<raw_code_value>,
    comment=<comment_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_field_create(
    name=<name_value>, 
    modifier=decl_typemodifier_create(<nested_params>), 
    bitfield_width=<bitfield_width_value>, 
    raw_code=<raw_code_value>, 
    comment=<comment_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_field_create('example_name', decl_typemodifier_create(), 0, 'raw_code_value', 'comment_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_field_create('demo', decl_typemodifier_create(), 1, 'demo', 'demo')}"
```

**相关函数**：
- [decl_typemodifier_create](#decl-typemodifier-create) - 用于 `modifier` 参数

---
<a id="decl-function-create"></a>
### decl_function_create

**描述**：C语言函数信息

**参数列表**：
- `name`: str
  - 名称字符串
- `return_type`: Any
  - 任意类型
- `params`: Any
  - 任意类型
- `comment`: Any
  - 任意类型
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_function_create(name: str, return_type: Any, params: Any, comment: Any, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_function_create(
    <name_value>,
    <return_type_value>,
    <params_value>,
    <comment_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_function_create(
    name=<name_value>,
    return_type=<return_type_value>,
    params=<params_value>,
    comment=<comment_value>,
    raw_code=<raw_code_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_function_create('example_name', 'return_type_value', 'params_value', 'comment_value', 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_function_create('demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="decl-param-create"></a>
### decl_param_create

**描述**：C语言函数参数信息

**参数列表**：
- `name`: str
  - 名称字符串
- `modifier`: decl_typemodifier_create
  - [decl_typemodifier_create](#decl-typemodifier-create)
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_param_create(name: str, modifier: decl_typemodifier_create, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_param_create(
    <name_value>,
    <modifier_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_param_create(
    name=<name_value>,
    modifier=<modifier_value>,
    raw_code=<raw_code_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_param_create(
    name=<name_value>, 
    modifier=decl_typemodifier_create(<nested_params>), 
    raw_code=<raw_code_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_param_create('example_name', decl_typemodifier_create(), 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_param_create('demo', decl_typemodifier_create(), 'demo')}"
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
- `attribute`: Any
  - 任意类型
- `qualifiers`: str
  - 限定符字符串
- `comment`: Any
  - 任意类型



**函数签名**：
```python
decl_record_create(name: str, fields: decl_field_create, attribute: Any, qualifiers: str, comment: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_record_create(
    <name_value>,
    <fields_value>,
    <attribute_value>,
    <qualifiers_value>,
    <comment_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_record_create(
    name=<name_value>,
    fields=<fields_value>,
    attribute=<attribute_value>,
    qualifiers=<qualifiers_value>,
    comment=<comment_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_record_create(
    name=<name_value>, 
    fields=decl_field_create(<nested_params>), 
    attribute=<attribute_value>, 
    qualifiers=<qualifiers_value>, 
    comment=<comment_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_record_create('example_name', decl_field_create(), 'attribute_value', 'example_qualifiers', 'comment_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_record_create('demo', decl_field_create(), 'demo', 'demo', 'demo')}"
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
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_struct_create(record: Any, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_struct_create(
    <record_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_struct_create(
    record=<record_value>,
    raw_code=<raw_code_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_struct_create('record_value', 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_struct_create('demo', 'demo')}"
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
- `attribute`: Any
  - 任意类型
- `pointer_level`: int
  - 整数值
- `array_dims`: List
  - 列表类型



**函数签名**：
```python
decl_typemodifier_create(type: decl_typeref_create, qualifiers: str, attribute: Any, pointer_level: int, array_dims: List)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_typemodifier_create(
    <type_value>,
    <qualifiers_value>,
    <attribute_value>,
    <pointer_level_value>,
    <array_dims_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_typemodifier_create(
    type=<type_value>,
    qualifiers=<qualifiers_value>,
    attribute=<attribute_value>,
    pointer_level=<pointer_level_value>,
    array_dims=<array_dims_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_typemodifier_create(
    type=decl_typeref_create(<nested_params>), 
    qualifiers=<qualifiers_value>, 
    attribute=<attribute_value>, 
    pointer_level=<pointer_level_value>, 
    array_dims=<array_dims_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_typemodifier_create(decl_typeref_create(), 'example_qualifiers', 'attribute_value', 0, [])}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_typemodifier_create(decl_typeref_create(), 'demo', 'demo', 1, ['item1', 'item2'])}"
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
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_typedef_create(name: str, typeref: decl_typeref_create, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_typedef_create(
    <name_value>,
    <typeref_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_typedef_create(
    name=<name_value>,
    typeref=<typeref_value>,
    raw_code=<raw_code_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_typedef_create(
    name=<name_value>, 
    typeref=decl_typeref_create(<nested_params>), 
    raw_code=<raw_code_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_typedef_create('example_name', decl_typeref_create(), 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_typedef_create('demo', decl_typeref_create(), 'demo')}"
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
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_union_create(record: Any, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_union_create(
    <record_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_union_create(
    record=<record_value>,
    raw_code=<raw_code_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_union_create('record_value', 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_union_create('demo', 'demo')}"
```


---
<a id="decl-variable-create"></a>
### decl_variable_create

**描述**：C语言变量信息

**参数列表**：
- `name`: str
  - 名称字符串
- `storage_class`: Any
  - 任意类型
- `modifier`: decl_typemodifier_create
  - [decl_typemodifier_create](#decl-typemodifier-create)
- `init_expr`: Any
  - 初始化表达式
- `comment`: Any
  - 任意类型
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
decl_variable_create(name: str, storage_class: Any, modifier: decl_typemodifier_create, init_expr: Any, comment: Any, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{decl_variable_create(
    <name_value>,
    <storage_class_value>,
    <modifier_value>,
    <init_expr_value>,
    <comment_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{decl_variable_create(
    name=<name_value>,
    storage_class=<storage_class_value>,
    modifier=<modifier_value>,
    init_expr=<init_expr_value>,
    comment=<comment_value>,
    raw_code=<raw_code_value>)
}"
```

*嵌套调用示例：*
```yaml
data: "{decl_variable_create(
    name=<name_value>, 
    storage_class=<storage_class_value>, 
    modifier=decl_typemodifier_create(<nested_params>), 
    init_expr=<init_expr_value>, 
    comment=<comment_value>, 
    raw_code=<raw_code_value>)
}"
```

**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{decl_variable_create('example_name', 'storage_class_value', decl_typemodifier_create(), 'init_expr_value', 'comment_value', 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {decl_variable_create('demo', 'demo', decl_typemodifier_create(), 'demo', 'demo', 'demo')}"
```

**相关函数**：
- [decl_typemodifier_create](#decl-typemodifier-create) - 用于 `modifier` 参数

---
## Preprocess 类函数

来源类：`Preprocess`  
函数数量：3

### 函数列表
- [preprocess_inclusiondirective_create](#preprocess-inclusiondirective-create)
- [preprocess_macrodefinition_create](#preprocess-macrodefinition-create)
- [preprocess_macroinstantiation_create](#preprocess-macroinstantiation-create)

<a id="preprocess-inclusiondirective-create"></a>
### preprocess_inclusiondirective_create

**描述**：C语言包含指令信息

**参数列表**：
- `filename`: Any
  - 任意类型
- `is_system`: Any
  - 任意类型



**函数签名**：
```python
preprocess_inclusiondirective_create(filename: Any, is_system: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{preprocess_inclusiondirective_create(
    <filename_value>,
    <is_system_value>)}"
```

*带参数名的调用：*
```yaml
data: "{preprocess_inclusiondirective_create(
    filename=<filename_value>,
    is_system=<is_system_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{preprocess_inclusiondirective_create('filename_value', 'is_system_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {preprocess_inclusiondirective_create('demo', 'demo')}"
```


---
<a id="preprocess-macrodefinition-create"></a>
### preprocess_macrodefinition_create

**描述**：C语言宏定义的元数据

**参数列表**：
- `name`: str
  - 名称字符串
- `value`: Any
  - 任意类型
- `params`: Any
  - 任意类型
- `comment`: Any
  - 任意类型
- `raw_code`: Any
  - 任意类型



**函数签名**：
```python
preprocess_macrodefinition_create(name: str, value: Any, params: Any, comment: Any, raw_code: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{preprocess_macrodefinition_create(
    <name_value>,
    <value_value>,
    <params_value>,
    <comment_value>,
    <raw_code_value>)}"
```

*带参数名的调用：*
```yaml
data: "{preprocess_macrodefinition_create(
    name=<name_value>,
    value=<value_value>,
    params=<params_value>,
    comment=<comment_value>,
    raw_code=<raw_code_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{preprocess_macrodefinition_create('example_name', 'value_value', 'params_value', 'comment_value', 'raw_code_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {preprocess_macrodefinition_create('demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="preprocess-macroinstantiation-create"></a>
### preprocess_macroinstantiation_create

**描述**：C语言宏实例化信息

**参数列表**：
- `name`: str
  - 名称字符串
- `args`: Any
  - 任意类型



**函数签名**：
```python
preprocess_macroinstantiation_create(name: str, args: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{preprocess_macroinstantiation_create(
    <name_value>,
    <args_value>)}"
```

*带参数名的调用：*
```yaml
data: "{preprocess_macroinstantiation_create(
    name=<name_value>,
    args=<args_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{preprocess_macroinstantiation_create('example_name', 'args_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {preprocess_macroinstantiation_create('demo', 'demo')}"
```


---
## XdmA 类函数

来源类：`XdmA`  
函数数量：11

### 函数列表
- [xdma_bswmoduledescblock_create](#xdma-bswmoduledescblock-create)
- [xdma_checkbox_create](#xdma-checkbox-create)
- [xdma_combobox_create](#xdma-combobox-create)
- [xdma_ecuparamdefblock_create](#xdma-ecuparamdefblock-create)
- [xdma_inputbox_create](#xdma-inputbox-create)
- [xdma_mainpage_create](#xdma-mainpage-create)
- [xdma_maptable_create](#xdma-maptable-create)
- [xdma_moduleblock_create](#xdma-moduleblock-create)
- [xdma_moduledefblock_create](#xdma-moduledefblock-create)
- [xdma_orderedtable_create](#xdma-orderedtable-create)
- [xdma_referencebox_create](#xdma-referencebox-create)

<a id="xdma-bswmoduledescblock-create"></a>
### xdma_bswmoduledescblock_create

**描述**：MetaData(name: str, module_ref_path: str)

**参数列表**：
- `name`: str
  - 名称字符串
- `module_ref_path`: Any
  - 任意类型



**函数签名**：
```python
xdma_bswmoduledescblock_create(name: str, module_ref_path: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_bswmoduledescblock_create(
    <name_value>,
    <module_ref_path_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_bswmoduledescblock_create(
    name=<name_value>,
    module_ref_path=<module_ref_path_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_bswmoduledescblock_create('example_name', 'module_ref_path_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_bswmoduledescblock_create('demo', 'demo')}"
```


---
<a id="xdma-checkbox-create"></a>
### xdma_checkbox_create

**描述**：MetaData(name: str, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, label_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, default_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>, is_label: bool = False)

**参数列表**：
- `name`: str
  - 名称字符串
- `desc_attr_xml`: Any
  - 任意类型
- `label_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `default_attr_xml`: Any
  - 任意类型
- `additional_attributes`: Any
  - 任意类型
- `is_label`: Any
  - 任意类型



**函数签名**：
```python
xdma_checkbox_create(name: str, desc_attr_xml: Any, label_attr_xml: Any, uuid_attr_xml: Any, default_attr_xml: Any, additional_attributes: Any, is_label: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_checkbox_create(
    <name_value>,
    <desc_attr_xml_value>,
    <label_attr_xml_value>,
    <uuid_attr_xml_value>,
    <default_attr_xml_value>,
    <additional_attributes_value>,
    <is_label_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_checkbox_create(
    name=<name_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    label_attr_xml=<label_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    default_attr_xml=<default_attr_xml_value>,
    additional_attributes=<additional_attributes_value>,
    is_label=<is_label_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_checkbox_create('example_name', 'desc_attr_xml_value', 'label_attr_xml_value', 'uuid_attr_xml_value', 'default_attr_xml_value', 'additional_attributes_value', 'is_label_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_checkbox_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-combobox-create"></a>
### xdma_combobox_create

**描述**：MetaData(name: str, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, label_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, range_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, default_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>, is_label: bool = False)

**参数列表**：
- `name`: str
  - 名称字符串
- `desc_attr_xml`: Any
  - 任意类型
- `label_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `range_attr_xml`: Any
  - 任意类型
- `default_attr_xml`: Any
  - 任意类型
- `additional_attributes`: Any
  - 任意类型
- `is_label`: Any
  - 任意类型



**函数签名**：
```python
xdma_combobox_create(name: str, desc_attr_xml: Any, label_attr_xml: Any, uuid_attr_xml: Any, range_attr_xml: Any, default_attr_xml: Any, additional_attributes: Any, is_label: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_combobox_create(
    <name_value>,
    <desc_attr_xml_value>,
    <label_attr_xml_value>,
    <uuid_attr_xml_value>,
    <range_attr_xml_value>,
    <default_attr_xml_value>,
    <additional_attributes_value>,
    <is_label_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_combobox_create(
    name=<name_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    label_attr_xml=<label_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    range_attr_xml=<range_attr_xml_value>,
    default_attr_xml=<default_attr_xml_value>,
    additional_attributes=<additional_attributes_value>,
    is_label=<is_label_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_combobox_create('example_name', 'desc_attr_xml_value', 'label_attr_xml_value', 'uuid_attr_xml_value', 'range_attr_xml_value', 'default_attr_xml_value', 'additional_attributes_value', 'is_label_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_combobox_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-ecuparamdefblock-create"></a>
### xdma_ecuparamdefblock_create

**描述**：MetaData(name: str, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, module_ref_path: str)

**参数列表**：
- `name`: str
  - 名称字符串
- `uuid_attr_xml`: Any
  - 任意类型
- `module_ref_path`: Any
  - 任意类型



**函数签名**：
```python
xdma_ecuparamdefblock_create(name: str, uuid_attr_xml: Any, module_ref_path: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_ecuparamdefblock_create(
    <name_value>,
    <uuid_attr_xml_value>,
    <module_ref_path_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_ecuparamdefblock_create(
    name=<name_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    module_ref_path=<module_ref_path_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_ecuparamdefblock_create('example_name', 'uuid_attr_xml_value', 'module_ref_path_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_ecuparamdefblock_create('demo', 'demo', 'demo')}"
```


---
<a id="xdma-inputbox-create"></a>
### xdma_inputbox_create

**描述**：MetaData(name: str, type: str, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, label_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, default_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>, is_label: bool = False)

**参数列表**：
- `name`: str
  - 名称字符串
- `type`: Any
  - 任意类型
- `desc_attr_xml`: Any
  - 任意类型
- `label_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `default_attr_xml`: Any
  - 任意类型
- `additional_attributes`: Any
  - 任意类型
- `is_label`: Any
  - 任意类型



**函数签名**：
```python
xdma_inputbox_create(name: str, type: Any, desc_attr_xml: Any, label_attr_xml: Any, uuid_attr_xml: Any, default_attr_xml: Any, additional_attributes: Any, is_label: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_inputbox_create(
    <name_value>,
    <type_value>,
    <desc_attr_xml_value>,
    <label_attr_xml_value>,
    <uuid_attr_xml_value>,
    <default_attr_xml_value>,
    <additional_attributes_value>,
    <is_label_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_inputbox_create(
    name=<name_value>,
    type=<type_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    label_attr_xml=<label_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    default_attr_xml=<default_attr_xml_value>,
    additional_attributes=<additional_attributes_value>,
    is_label=<is_label_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_inputbox_create('example_name', 'type_value', 'desc_attr_xml_value', 'label_attr_xml_value', 'uuid_attr_xml_value', 'default_attr_xml_value', 'additional_attributes_value', 'is_label_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_inputbox_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-mainpage-create"></a>
### xdma_mainpage_create

**描述**：MetaData(xml_version: str, namespaces: Dict[str, str], project: Optional[str], platform: Optional[str], peripheral: Optional[str], autosar_version: Optional[str], build_version: Optional[str], copyright: Optional[str], ctr_type: str, ctr_factory: str, ctr_namespaces: Dict[str, str], top_level_package_name: Optional[str], top_level_package_type: Optional[str], uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData)

**参数列表**：
- `xml_version`: Any
  - 任意类型
- `namespaces`: Any
  - 任意类型
- `project`: Any
  - 任意类型
- `platform`: Any
  - 任意类型
- `peripheral`: Any
  - 任意类型
- `autosar_version`: Any
  - 任意类型
- `build_version`: Any
  - 任意类型
- `copyright`: Any
  - 任意类型
- `ctr_type`: Any
  - 任意类型
- `ctr_factory`: Any
  - 任意类型
- `ctr_namespaces`: Any
  - 任意类型
- `top_level_package_name`: Any
  - 任意类型
- `top_level_package_type`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型



**函数签名**：
```python
xdma_mainpage_create(xml_version: Any, namespaces: Any, project: Any, platform: Any, peripheral: Any, autosar_version: Any, build_version: Any, copyright: Any, ctr_type: Any, ctr_factory: Any, ctr_namespaces: Any, top_level_package_name: Any, top_level_package_type: Any, uuid_attr_xml: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_mainpage_create(
    <xml_version_value>,
    <namespaces_value>,
    <project_value>,
    <platform_value>,
    <peripheral_value>,
    <autosar_version_value>,
    <build_version_value>,
    <copyright_value>,
    <ctr_type_value>,
    <ctr_factory_value>,
    <ctr_namespaces_value>,
    <top_level_package_name_value>,
    <top_level_package_type_value>,
    <uuid_attr_xml_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_mainpage_create(
    xml_version=<xml_version_value>,
    namespaces=<namespaces_value>,
    project=<project_value>,
    platform=<platform_value>,
    peripheral=<peripheral_value>,
    autosar_version=<autosar_version_value>,
    build_version=<build_version_value>,
    copyright=<copyright_value>,
    ctr_type=<ctr_type_value>,
    ctr_factory=<ctr_factory_value>,
    ctr_namespaces=<ctr_namespaces_value>,
    top_level_package_name=<top_level_package_name_value>,
    top_level_package_type=<top_level_package_type_value>,
    uuid_attr_xml=<uuid_attr_xml_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_mainpage_create('xml_version_value', 'namespaces_value', 'project_value', 'platform_value', 'peripheral_value', 'autosar_version_value', 'build_version_value', 'copyright_value', 'ctr_type_value', 'ctr_factory_value', 'ctr_namespaces_value', 'top_level_package_name_value', 'top_level_package_type_value', 'uuid_attr_xml_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_mainpage_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-maptable-create"></a>
### xdma_maptable_create

**描述**：MetaData(name: str, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>)

**参数列表**：
- `name`: str
  - 名称字符串
- `additional_attributes`: Any
  - 任意类型



**函数签名**：
```python
xdma_maptable_create(name: str, additional_attributes: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_maptable_create(
    <name_value>,
    <additional_attributes_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_maptable_create(
    name=<name_value>,
    additional_attributes=<additional_attributes_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_maptable_create('example_name', 'additional_attributes_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_maptable_create('demo', 'demo')}"
```


---
<a id="xdma-moduleblock-create"></a>
### xdma_moduleblock_create

**描述**：MetaData(name: str, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>)

**参数列表**：
- `name`: str
  - 名称字符串
- `desc_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `additional_attributes`: Any
  - 任意类型



**函数签名**：
```python
xdma_moduleblock_create(name: str, desc_attr_xml: Any, uuid_attr_xml: Any, additional_attributes: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_moduleblock_create(
    <name_value>,
    <desc_attr_xml_value>,
    <uuid_attr_xml_value>,
    <additional_attributes_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_moduleblock_create(
    name=<name_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    additional_attributes=<additional_attributes_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_moduleblock_create('example_name', 'desc_attr_xml_value', 'uuid_attr_xml_value', 'additional_attributes_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_moduleblock_create('demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-moduledefblock-create"></a>
### xdma_moduledefblock_create

**描述**：MetaData(name: str, release_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, admin_data_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, postbuildvariantsupport_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, lower_multiplicity_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, upper_multiplicity_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_implementationconfigclass_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_label_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_default_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, imp_range_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, module_refined_module_def_path: Optional[str] = None)

**参数列表**：
- `name`: str
  - 名称字符串
- `release_attr_xml`: Any
  - 任意类型
- `admin_data_attr_xml`: Any
  - 任意类型
- `postbuildvariantsupport_attr_xml`: Any
  - 任意类型
- `desc_attr_xml`: Any
  - 任意类型
- `lower_multiplicity_attr_xml`: Any
  - 任意类型
- `upper_multiplicity_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `imp_desc_attr_xml`: Any
  - 任意类型
- `imp_implementationconfigclass_attr_xml`: Any
  - 任意类型
- `imp_label_attr_xml`: Any
  - 任意类型
- `imp_uuid_attr_xml`: Any
  - 任意类型
- `imp_default_attr_xml`: Any
  - 任意类型
- `imp_range_attr_xml`: Any
  - 任意类型
- `module_refined_module_def_path`: Any
  - 任意类型



**函数签名**：
```python
xdma_moduledefblock_create(name: str, release_attr_xml: Any, admin_data_attr_xml: Any, postbuildvariantsupport_attr_xml: Any, desc_attr_xml: Any, lower_multiplicity_attr_xml: Any, upper_multiplicity_attr_xml: Any, uuid_attr_xml: Any, imp_desc_attr_xml: Any, imp_implementationconfigclass_attr_xml: Any, imp_label_attr_xml: Any, imp_uuid_attr_xml: Any, imp_default_attr_xml: Any, imp_range_attr_xml: Any, module_refined_module_def_path: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_moduledefblock_create(
    <name_value>,
    <release_attr_xml_value>,
    <admin_data_attr_xml_value>,
    <postbuildvariantsupport_attr_xml_value>,
    <desc_attr_xml_value>,
    <lower_multiplicity_attr_xml_value>,
    <upper_multiplicity_attr_xml_value>,
    <uuid_attr_xml_value>,
    <imp_desc_attr_xml_value>,
    <imp_implementationconfigclass_attr_xml_value>,
    <imp_label_attr_xml_value>,
    <imp_uuid_attr_xml_value>,
    <imp_default_attr_xml_value>,
    <imp_range_attr_xml_value>,
    <module_refined_module_def_path_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_moduledefblock_create(
    name=<name_value>,
    release_attr_xml=<release_attr_xml_value>,
    admin_data_attr_xml=<admin_data_attr_xml_value>,
    postbuildvariantsupport_attr_xml=<postbuildvariantsupport_attr_xml_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    lower_multiplicity_attr_xml=<lower_multiplicity_attr_xml_value>,
    upper_multiplicity_attr_xml=<upper_multiplicity_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    imp_desc_attr_xml=<imp_desc_attr_xml_value>,
    imp_implementationconfigclass_attr_xml=<imp_implementationconfigclass_attr_xml_value>,
    imp_label_attr_xml=<imp_label_attr_xml_value>,
    imp_uuid_attr_xml=<imp_uuid_attr_xml_value>,
    imp_default_attr_xml=<imp_default_attr_xml_value>,
    imp_range_attr_xml=<imp_range_attr_xml_value>,
    module_refined_module_def_path=<module_refined_module_def_path_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_moduledefblock_create('example_name', 'release_attr_xml_value', 'admin_data_attr_xml_value', 'postbuildvariantsupport_attr_xml_value', 'desc_attr_xml_value', 'lower_multiplicity_attr_xml_value', 'upper_multiplicity_attr_xml_value', 'uuid_attr_xml_value', 'imp_desc_attr_xml_value', 'imp_implementationconfigclass_attr_xml_value', 'imp_label_attr_xml_value', 'imp_uuid_attr_xml_value', 'imp_default_attr_xml_value', 'imp_range_attr_xml_value', 'module_refined_module_def_path_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_moduledefblock_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-orderedtable-create"></a>
### xdma_orderedtable_create

**描述**：MetaData(name: str, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>)

**参数列表**：
- `name`: str
  - 名称字符串
- `additional_attributes`: Any
  - 任意类型



**函数签名**：
```python
xdma_orderedtable_create(name: str, additional_attributes: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_orderedtable_create(
    <name_value>,
    <additional_attributes_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_orderedtable_create(
    name=<name_value>,
    additional_attributes=<additional_attributes_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_orderedtable_create('example_name', 'additional_attributes_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_orderedtable_create('demo', 'demo')}"
```


---
<a id="xdma-referencebox-create"></a>
### xdma_referencebox_create

**描述**：MetaData(name: str, type: str, desc_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, label_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, ref_attr_xml: modules.plugins.type_classes.xml.XmlNode.MetaData, additional_attributes: List[modules.plugins.type_classes.xml.XmlNode.MetaData] = <factory>)

**参数列表**：
- `name`: str
  - 名称字符串
- `type`: Any
  - 任意类型
- `desc_attr_xml`: Any
  - 任意类型
- `label_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `ref_attr_xml`: Any
  - 任意类型
- `additional_attributes`: Any
  - 任意类型



**函数签名**：
```python
xdma_referencebox_create(name: str, type: Any, desc_attr_xml: Any, label_attr_xml: Any, uuid_attr_xml: Any, ref_attr_xml: Any, additional_attributes: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_referencebox_create(
    <name_value>,
    <type_value>,
    <desc_attr_xml_value>,
    <label_attr_xml_value>,
    <uuid_attr_xml_value>,
    <ref_attr_xml_value>,
    <additional_attributes_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_referencebox_create(
    name=<name_value>,
    type=<type_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    label_attr_xml=<label_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    ref_attr_xml=<ref_attr_xml_value>,
    additional_attributes=<additional_attributes_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_referencebox_create('example_name', 'type_value', 'desc_attr_xml_value', 'label_attr_xml_value', 'uuid_attr_xml_value', 'ref_attr_xml_value', 'additional_attributes_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_referencebox_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
## XdmAttribute 类函数

来源类：`XdmAttribute`  
函数数量：1

### 函数列表
- [xdmattribute_node_create](#xdmattribute-node-create)

<a id="xdmattribute-node-create"></a>
### xdmattribute_node_create

**描述**：Xdm Attribute Metadata

**参数列表**：
- `name`: str
  - 名称字符串
- `metadata`: Any
  - 任意类型



**函数签名**：
```python
xdmattribute_node_create(name: str, metadata: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdmattribute_node_create(
    <name_value>,
    <metadata_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdmattribute_node_create(
    name=<name_value>,
    metadata=<metadata_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdmattribute_node_create('example_name', 'metadata_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdmattribute_node_create('demo', 'demo')}"
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

- 总函数数：27
- 成功收集的类：Node, Decl, Preprocess, XdmA, XdmAttribute
