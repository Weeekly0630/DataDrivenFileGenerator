# 数据树渲染示例

**DataHandler**模块提供了数据树渲染的能力，可以将复杂的数据结构以树形方式展示。**DataHandler**将解析data_config中的root_path下所有符合file_pattern的文件，并构建一个树结构`DataNode`。**DataDrivenGenerator**将递归遍历这个树结构，并使用TemplateHander生成每个节点的渲染数据。

## 1.使用方法
```python
cli.py ./example_config.yaml
```

## 2.文件结构
### DataNodeTree(Yaml文件树)
Yaml文件树通过config中定义的template_key以及children_key来指定模版名称以及子节点内容。YamlHandler根据CHILDREN_PATH, 通过FileNode进行搜索，构建一个DataNode树

- root.yaml:
    ```yaml
    TEMPLATE_PATH: "root.j2" # 模版名称
    CHILDREN_PATH: ["services/*.yaml"] # 子节点路径
    ```
- web.yaml:
    ```yaml
    TEMPLATE_PATH: "web.j2"
    CHILDREN_PATH: ["endpoints/*.yaml", "../children/*.yaml"]
    ```
- DataNode树：
    ```mermaid
    graph TD;
        root[root.yaml]
        root -->|pattrens| root_pattern(services/*.yaml)
        root_pattern --> web[web.yaml]
        root_pattern --> database[database.yaml]
        web -->|pattrens| web_pattern1(endpoints/*.yaml)
        web -->|pattrens| web_pattern2(../children/*.yaml)
        web_pattern1 --> api[api.yaml]
        web_pattern2 --> child1[child1.yaml]
    ```
同时，会自动为CHILDREN_PATH不同路径进行分组，生成不同的children_context。例如在web.yaml中，CHILDREN_PATH有两个路径，分别为`endpoints/*.yaml`和`../children/*.yaml`，因此会生成两个children_context：**CHILDREN_CONTEXT0**和**CHILDREN_CONTEXT1**。