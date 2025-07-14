# Key Python Concepts Used in Data Driven Generator

This document explains the main Python concepts used in the implementation for future reference.

## 1. Protocols (@runtime_checkable)
```python
@runtime_checkable
class DataHandler(Protocol):
    def get_data(self) -> Iterator[Dict[str, Any]]:
        ...
```
- Like interfaces in other languages
- Defines what methods a class must implement
- @runtime_checkable allows using isinstance() checks

## 2. Property Decorators
```python
@property
def preserved_template_key(self) -> str:
    return self.config.preserved_template_key
```
- Makes method behave like an attribute
- Provides read-only access to internal data

## 3. Type Hints
```python
def render_template(self, template_path: str, context: Dict[str, Any]) -> Optional[str]:
```
- Shows what types methods expect/return
- Helps catch errors early
- Makes code more readable

## 4. Enums
```python
class DataType(Enum):
    YAML = "yaml"
```
- Defines a set of named constants
- Safer than using strings directly

## 5. Dataclasses
```python
@dataclass
class DataDrivenGeneratorConfig:
    data_type: DataType
    data_config: Dict[str, Any]
```
- Automatically adds __init__, __repr__
- Good for classes that mainly hold data

## 6. Exception Handling
```python
class GeneratorError(Exception):
    def __init__(self, error_type: GeneratorErrorType, message: str):
        self.error_type = error_type
        self.message = message
```
- Custom exceptions for specific error cases
- Makes error handling more organized

## Using the Generator

See `modules/test/test_data_driven_generator.py` for a complete example with:
1. Setting up test data and templates
2. Creating configuration
3. Using the generator
4. Error handling examples

Basic usage:
```python
config = DataDrivenGeneratorConfig(
    data_type=DataType.YAML,
    data_config={"root_path": "path/to/data.yaml"},
    template_type=TemplateType.JINJA,
    template_config={"template_dir": "path/to/templates"}
)
generator = DataDrivenGenerator(config)
result = generator.render()
