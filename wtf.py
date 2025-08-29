from dataclasses import dataclass, fields
from typing import List, TypeVar, Type, Union, Any, Callable, Dict, get_type_hints, ClassVar, Protocol, runtime_checkable
from functools import wraps


# 定义协议类型
@runtime_checkable
class HasMetaData(Protocol):
    """定义具有MetaData内部类的协议"""
    MetaData: Type[Any]
    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Any: ...

M = TypeVar('M', bound=HasMetaData)  # 限制类型变量必须符合HasMetaData协议


T = TypeVar('T')

class Converter:
    """转换器基类，定义转换方法"""
    @staticmethod
    def convert(value: Any) -> Any:
        raise NotImplementedError

class StringListConverter(Converter):
    """字符串列表转换器"""
    @staticmethod
    def convert(value: Any) -> List[str]:
        if isinstance(value, str):
            return value.split('\n')
        return value

class IntConverter(Converter):
    """整数转换器"""
    @staticmethod
    def convert(value: Any) -> int:
        if isinstance(value, str):
            return int(value)
        return int(value)

class AutoConvertMixin:
    """自动转换Mixin类，提供create方法和转换功能"""
    
    # 类变量，存储每个类的转换器配置
    _converters: ClassVar[Dict[str, Type[Converter]]] = {}
    
    @classmethod
    def configure_converters(cls, **field_converters: Type[Converter]) -> None:
        """配置字段转换器
        
        Args:
            **field_converters: 字段名和对应的转换器类
            
        Example:
            MyClass.configure_converters(
                meta=StringListConverter,
                test_int=IntConverter
            )
        """
        cls._converters = field_converters
    
    @classmethod
    def create(cls: Type[T], *args, **kwargs) -> T:
        """创建类实例，自动进行类型转换"""
        # 处理位置参数
        try:
            field_names = [f.name for f in fields(cls)]
        except TypeError:
            # 如果不是dataclass，尝试从注解中获取字段名
            field_names = list(get_type_hints(cls).keys())
        
        new_args = list(args)
        
        # 转换位置参数
        for i, (value, field_name) in enumerate(zip(args, field_names)):
            if field_name in cls._converters:
                new_args[i] = cls._converters[field_name].convert(value)
        
        # 转换关键字参数
        new_kwargs = kwargs.copy()
        for field_name, value in kwargs.items():
            if field_name in cls._converters:
                new_kwargs[field_name] = cls._converters[field_name].convert(value)
        
        # 创建实例
        return cls(*new_args, **new_kwargs)


# 使用Mixin的方式
@dataclass
class Object1(AutoConvertMixin):
    meta: List[str]
    test_string: List[str]

# 配置转换器
Object1.configure_converters(
    meta=StringListConverter,
    test_string=StringListConverter
)

@dataclass
class Object2(AutoConvertMixin):
    meta: List[str]
    test_int: int

Object2.configure_converters(
    meta=StringListConverter,
    test_int=IntConverter
)

@dataclass
class Object3(AutoConvertMixin):
    meta: List[str]
    test_string: List[str]
    test_int: int

Object3.configure_converters(
    meta=StringListConverter,
    test_string=StringListConverter,
    test_int=IntConverter
)


# ---- 测试代码 ----
# if __name__ == "__main__":
#     # 测试1：多个字段的自动转换
#     print("\n测试1：多字段转换")
#     obj1 = Object1.create(
#         meta="第一行\n第二行",
#         test_string="测试1\n测试2"
#     )
#     print(f"obj1.meta = {obj1.meta}")
#     print(f"obj1.test_string = {obj1.test_string}")

#     # 测试2：整数转换
#     print("\n测试2：整数转换")
#     obj2 = Object2.create(
#         meta=["列表元素1", "列表元素2"],
#         test_int="42"  # 字符串会被自动转换为整数
#     )
#     print(f"obj2.meta = {obj2.meta}")
#     print(f"obj2.test_int = {obj2.test_int} (类型: {type(obj2.test_int)})")

#     # 测试3：混合类型转换
#     print("\n测试3：混合类型转换")
#     obj3 = Object3.create(
#         meta="首行\n次行",
#         test_string="A\nB\nC",
#         test_int=123
#     )
#     print(f"obj3.meta = {obj3.meta}")
#     print(f"obj3.test_string = {obj3.test_string}")
#     print(f"obj3.test_int = {obj3.test_int}")

#     # 测试4：错误处理
#     print("\n测试4：错误处理")
#     try:
#         obj_error = Object2.create(
#             meta="test",
#             test_int="not a number"  # 这应该引发错误
#         )
#         print("这行不应该执行")
#     except ValueError as e:
#         print(f"预期的错误: {e}")

#     # 测试5：类型检查
#     print("\n测试5：类型检查")
#     print(f"obj1是否为Object1实例: {isinstance(obj1, Object1)}")
#     print(f"obj1的实际类型: {type(obj1)}")

#     # 测试6：位置参数
#     print("\n测试6：位置参数")
#     obj1_pos = Object1.create(
#         "A\nB",  # meta
#         "C\nD"   # test_string
#     )
#     print(f"使用位置参数创建: {obj1_pos.meta}, {obj1_pos.test_string}")

#     # 测试7：混合参数
#     print("\n测试7：混合参数")
#     obj3_mixed = Object3.create(
#         "X\nY",           # meta (位置参数)
#         test_string="P\nQ",  # 关键字参数
#         test_int="789"    # 关键字参数，会被转换为整数
#     )
#     print(f"混合参数创建: {obj3_mixed.meta}, {obj3_mixed.test_string}, {obj3_mixed.test_int}")

def auto_metadata(*field_types: tuple[str, Type[Converter]]):
    """装饰器：为内部MetaData类添加自动转换功能
    
    Args:
        field_types: 元组列表，每个元组包含 (字段名, 转换器类)
        
    Example:
        @auto_metadata(
            ("x", IntConverter),
            ("y", IntConverter)
        )
        class Point:
            @dataclass
            class MetaData:
                x: int
                y: int
    """
    def decorator(cls: Type[M]) -> Type[M]:
        if not hasattr(cls, 'MetaData'):
            raise TypeError(f"{cls.__name__} must have a MetaData inner class")
            
        # 获取原始的MetaData类
        metadata_cls = cls.MetaData
        converters = dict(field_types)
        
        def create_impl(*args: Any, **kwargs: Any) -> cls.MetaData:
            # 处理位置参数
            field_names = [f.name for f in fields(metadata_cls)]
            new_args = list(args)
            
            # 转换位置参数
            for i, (value, field_name) in enumerate(zip(args, field_names)):
                if field_name in converters:
                    new_args[i] = converters[field_name].convert(value)
            
            # 转换关键字参数
            new_kwargs = kwargs.copy()
            for field_name, value in kwargs.items():
                if field_name in converters:
                    new_kwargs[field_name] = converters[field_name].convert(value)
                    
            return metadata_cls(*new_args, **new_kwargs)
            
        # 使用update_wrapper保持函数元数据
        setattr(cls, 'create', classmethod(create_impl))
        return cls

    return decorator


# 使用装饰器
@auto_metadata(
    ("x", IntConverter),
    ("y", IntConverter)
)
class Point(HasMetaData):
    @dataclass
    class MetaData:
        x: int
        y: int
        
    # 为了满足Protocol，提供一个空的create方法，它会被装饰器替换
    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> MetaData:
        ...

# 额外的测试代码
if __name__ == "__main__":
    print("\n测试Point类：")
    # 使用字符串创建点
    p1 = Point.create("42", "24")
    print(f"从字符串创建: x={p1.x}, y={p1.y}")
    
    # 使用关键字参数
    p2 = Point.create(x="10", y="20")
    print(f"使用关键字参数: x={p2.x}, y={p2.y}")
    
    # 混合使用
    p3 = Point.create("100", y="200")
    print(f"混合参数: x={p3.x}, y={p3.y}")
    
    # 错误处理
    try:
        p_error = Point.create("not a number", "20")
        print("这行不应该执行")
    except ValueError as e:
        print(f"预期的错误: {e}")