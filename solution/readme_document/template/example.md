# {{ name }}
---
{{ description }}

## 特性介绍

{% for feature in features %}
{{ feature.name }}: {{ feature.description }}
{% endfor %}

## 输入说明

{{ input_description }}

## 输出说明

{{ output_description }}

