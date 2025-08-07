# 函数调用模板文档

本文档列出了所有可用的函数及其调用模板。

## 目录

- [函数调用模板文档](#函数调用模板文档)
  - [目录](#目录)
  - [decl\_field\_create {#decl-field-create}](#decl_field_create-decl-field-create)
  - [decl\_struct\_create {#decl-struct-create}](#decl_struct_create-decl-struct-create)
  - [decl\_typemodifier\_create {#decl-typemodifier-create}](#decl_typemodifier_create-decl-typemodifier-create)
  - [decl\_typeref\_create {#decl-typeref-create}](#decl_typeref_create-decl-typeref-create)
  - [decl\_typedef\_create {#decl-typedef-create}](#decl_typedef_create-decl-typedef-create)
  - [decl\_union\_create {#decl-union-create}](#decl_union_create-decl-union-create)
  - [decl\_variable\_create {#decl-variable-create}](#decl_variable_create-decl-variable-create)
- [函数调用模板文档](#函数调用模板文档-1)
  - [目录](#目录-1)
  - [node\_find\_create {#node-find-create}](#node_find_create-node-find-create)
  - [node\_value\_create {#node-value-create}](#node_value_create-node-value-create)

---

## decl_field_create {#decl-field-create}

**参数列表**:
- `name`: `str` - 名称字符串
- `modifier`: [decl_typemodifier_create](#decl-typemodifier-create)
- `bitfield_width`: `int` - 整数值

**调用模板**:
```
decl_field_create(
    <name_value>,
    <modifier_value>,
    <bitfield_width_value>
)
```

---

## decl_struct_create {#decl-struct-create}

**参数列表**:
- `record`: `Any` - 任意类型
- `fields`: [decl_field_create](#decl-field-create)

**调用模板**:
```
decl_struct_create(<record_value>, <fields_value>)
```

---

## decl_typemodifier_create {#decl-typemodifier-create}

**参数列表**:
- `type`: [decl_typeref_create](#decl-typeref-create)
- `qualifiers`: `str` - 限定符字符串
- `attributes`: `List` - 列表类型
- `is_pointer`: `bool` - 布尔值
- `pointer_level`: `int` - 整数值
- `is_array`: `bool` - 布尔值
- `array_dims`: `List` - 列表类型

**调用模板**:
```
decl_typemodifier_create(
    <type_value>,
    <qualifiers_value>,
    <attributes_value>,
    <is_pointer_value>,
    <pointer_level_value>,
    <is_array_value>,
    <array_dims_value>
)
```

---

## decl_typeref_create {#decl-typeref-create}

**参数列表**:
- `ref`: [decl_typeref_create](#decl-typeref-create)

**调用模板**:
```
decl_typeref_create(<ref_value>)
```

---

## decl_typedef_create {#decl-typedef-create}

**参数列表**:
- `name`: `str` - 名称字符串
- `typeref`: [decl_typeref_create](#decl-typeref-create)

**调用模板**:
```
decl_typedef_create(<name_value>, <typeref_value>)
```

---

## decl_union_create {#decl-union-create}

**参数列表**:
- `record`: `Any` - 任意类型
- `fields`: [decl_field_create](#decl-field-create)

**调用模板**:
```
decl_union_create(<record_value>, <fields_value>)
```

---

## decl_variable_create {#decl-variable-create}

**参数列表**:
- `name`: `str` - 名称字符串
- `modifier`: [decl_typemodifier_create](#decl-typemodifier-create)
- `init_expr`: `Any` - 初始化表达式

**调用模板**:
```
decl_variable_create(
    <name_value>,
    <modifier_value>,
    <init_expr_value>
)
```

---

# 函数调用模板文档

本文档列出了所有可用的函数及其调用模板。

## 目录

- [node_find_create](#node-find-create)
- [node_value_create](#node-value-create)

---

## node_find_create {#node-find-create}

**参数列表**:
- `results`: `Any` - 任意类型

**调用模板**:
```
node_find_create(<results_value>)
```

---

## node_value_create {#node-value-create}

**参数列表**:
- `value`: `Any` - 任意类型

**调用模板**:
```
node_value_create(<value_value>)
```
