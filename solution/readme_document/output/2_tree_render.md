# 数据驱动模版生成器树渲染
---
该文档讲解了数据驱动模版生成器的数据树构建功能，展示如何通过保留关键字指示数据数的构建，模板嵌套，以及简述树渲染流程

## 特性介绍

模板嵌套: 支持模板嵌套，数据节点通过指定`children_key`来指示子模板路径，在模板中通过`children_context_key`来引用子模版内容

## 详细说明

### 数据树

数据树是一个N叉树，其节点为`DataNode`，在yaml中的保留键所指定的是子节点的路径列表(Windows file path)， 通过递归的方式从入口数据文件开始，逐步读取子节点文件，最终构建出一个完整的数据树。数据树的每一个节点都包含一个字典数据， 以及一个子节点列表。数据树的构建仅在DataHandler为`YamlHandler`时被构建。

### 递归渲染

以深度优先的方式对数据树进行递归渲染。首先渲染叶子节点，然后将渲染结果(str)通过`preserved_children_content_key`传递给父节点，即在父节点的数据 字典中添加一个键值对，键为`preserved_children_content_key`，值为子节点渲染结果(str)。然后父节点进行渲染，依次类推，直到根节点渲染完成。

### 子节点分组

在指定子节点路径时，支持使用通配符以及路径列表的方式来指定子节点路径，从而实现子节点的分组功能。
例如:
```yaml
CHILDREN_PATH:
  - "child1.yaml"
  - "child2.yaml"
  - "group/*.yaml"
```
最终的`preserved_children_content_key`为`[[child1.yaml], [child2.yaml], [group/*.yaml]]`，父节点通过`preserved_children_content_key[index]`来引用子节点渲染结果。同时若引用对象为一个列表，将自动以换行符进行拼接。


### 子节点引用

在模板中引用`preserved_children_content_key=CHILDREN_CONTEXT`, 推荐加上 `| string`.否则需要注意该对象是否为字符串类型。
```jinja2
<web-service>
    <info>
        <name>{{ name }}</name>
        <type>{{ type }}</type>
        <port>{{ port }}</port>
        <enabled>{{ enabled }}</enabled>
    </info>
    <endpoints>
        {{ CHILDREN_CONTEXT[0] | string | indent(8) }}
    </endpoints>
    <children1>
        {{ CHILDREN_CONTEXT[1] | string | indent(8) }}
    </children1>
</web-service>
```



## 输入说明

- **文件树"**: 
```text
==============Serialized File Tree==============
u:/users/enlink/documents/code/python/datadrivenfilegenerator/modules/examples/2_tree_render/source/data/
  services/
    endpoints/
      api1.yaml
      api2.yaml
    database.yaml
    web.yaml
  root.yaml
```

- **数据树**: 
```text
==============Serialized Data Tree==============
root.yaml
  database.yaml
  web.yaml
    api1.yaml
    api2.yaml
```


## 输出说明

输出root.yaml的渲染结果。

## 关键内容展示

- **文件构建**: 
```python
def visitor(node: DataNode, *args) -> None:
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
  expression_preprocess(node)
  # 进行渲染
  try:
      template_path = node.data[self.config.preserved_template_key]
      # 渲染模板
      result = self.template_handler.render(template_path, node.data)
      # 验证渲染结果并保存
      validate_render_result(result, template_path)
      self._rendered_contents[node] = result
  except Exception as e:
      raise GeneratorError(
          GeneratorErrorType.RENDER_ERROR,
          f"Failed to render {template_path}: {str(e)}",
      )
```

- `children_content_init`将初始化数据字典中保留的属性
- `children_content_update`将子节点的内容分组

