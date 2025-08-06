# Code Repository Information

## Software Architecture

Software architecture description

## Installation

1. xxxx
2. xxxx
3. xxxx

## Instructions

1. xxxx
2. xxxx
3. xxxx

## Contribution

## Features

1. Template rendering: Use a yaml file with one key-value pair specifying the template name. DataDrivenFileGenerator uses jinja2 to read the template and renders it with yaml data.
2. Template tree construction: A yaml specifies a jinja template, and multiple yaml use CHILDREN_PATH key-value pairs to associate on the file path, for example CHILDREN_PATH: [./a/*.yaml] means that all yaml files in folder A are child nodes. The parent node can use a special CHILDREN_CONTEXT key-value pair to reference the template, for example, CHILDREN_CONTEXT[0] refers to element 0.
3. Plugin class: The function information defined in the .py file in the plugins folder is loaded into the FunctionResolver, and the function can be called in the yaml data through the python fstring form f "{} {}", and the data of the node can be searched upwards.
4. inline data node: In CHILDREN_PATH, using a dictionary to directly add a full YAML template data dictionary, it will be resolved as an inline data node to a child node of that node. Some short yaml node creations can be reduced.