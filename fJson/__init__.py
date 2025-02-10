"""
FlexibleJSON (fJson)
===================

一个灵活的 JSON 解析和序列化库,支持以下特性:
- 支持注释 
- 支持不带引号的键
- 支持数组、元组和集合
- 支持跨行字符串
- 支持全角引号
- 支持参数化格式
- 内置数据类装饰器

基本用法:
    from fJson import decode, encode, DataClass
    
    # 解析 JSON 字符串
    obj = decode('{"name": "张三", "age": 18}')
    
    # 序列化 Python 对象
    json_str = encode(obj, indent=2)
    
    # 数据类装饰器
    @DataClass
    class Person:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

"""
from .fjson import decode, encode, DataClass