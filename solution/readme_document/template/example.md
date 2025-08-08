# {{ name }}
---
{{ description }}

## 特性介绍

{% for feature in features %}
{{ feature.name }}: {{ feature.description }}
{% endfor %}

## 详细说明

{% for section in sections %}
### {{ section.title }}

{{ section.content }}

{% endfor %}

## 输入说明

{% for input_desc in input_descs %}
- **{{ input_desc.name }}**: {{ input_desc.description }}
{% endfor %}

## 输出说明

{{ output_description }}

## 关键内容展示

{% for key_content in key_contents %}
- **{{ key_content.title }}**: {{ key_content.content }}
{% endfor %}