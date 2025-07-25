# 代码库说明

## 介绍

让你更加专注于核心数据的修改，而不是样式或者格式

## 软件架构

### DataDrivenGenerator

模板渲染，

## 安装教程

## 使用说明

```python
python modules/cli/cli.py your_config.yaml
```

## TODO-List

- 将expr_filter的逻辑全部删除
- 优化tree的构建，并支持内嵌DataNode
- 移除所有静态动态函数插件概念，因为上下文由函数运行时传递，所有函数都是静态的函数
