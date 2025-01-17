# fJson

[English](readme-en.md) | [中文](readme.md)

fJson 是一个宽松格式的 JSON 解析器，支持注释、不带引号的键、数组、元组等，不支持特殊字符转义但支持跨行字符串、支持多行注释，支持全角引号。

本意是为了解决 LLMs 的抽风问题，后来发现实际还可以添加其他用途，比如解析命令行参数。于是催生了这个项目。

这个项目基本上是 Python 专供的，因为 Python 支持动态类型，所以可以直接解析出来，而 C++ 之类的需要自己实现数据结构管理。

## 功能特性

- **字典**: 支持不带引号的键
- **列表**: 支持标准 JSON 列表格式
- **元组**: 支持元组格式
- **参数组**: 支持 `--key value` 形式的参数组
- **多行字符串**: 支持 `R"delimiter(内容)delimiter"` 形式的多行字符串
- **Base64 编码字符串**: 支持 `$"base64字符串"` 形式的 Base64 编码字符串
- **表达式计算**: 支持一些表达式计算，如笛卡尔积、字符串连接、条件表达式等
- _预计支持更多特性_

## 使用方法

除了 `decode` 函数外，其他类都是用于解析 JSON 的，`decode` 函数是对外的接口，传入一个字符串，返回一个解析后的对象。

### 示例

```python
from fjson import decode

text = '''
{
    key1: value1,
    key2: {
        key3: value3,
        key4: value4
    },
    key5: [value5, value6, value7],
    key6: (value8, value9),
    key7: (--key10 value10 --key11 value11),
    key8: R"delimiter(
        multi-line
        string
    )delimiter",
    key9: $"YmFzZTY0IGVuY29kZWQgc3RyaW5n"
}
'''

result = decode(text)
print(result)
```

## 函数

### decode(json_str: str) -> Any

解析 JSON 字符串，返回解析后的对象。

```python
def decode(json_str):
    """
    解析 JSON 字符串
    """
    tokens = fJsonLexer().tokenize(json_str)
    tokens = fJsonLexer().reject_comments(tokens)
    tokens = fJsonLexer().concat_negative_number(tokens)
    return fJsonBuilder(tokens).build()
```

## 例子

```python
import fJson as json

fjson_str = """
/* This is a comment */
[
    {
        name: 'John',
        age: 30,
        city: "New York",
        male: true
    }, // 字典
    {
        “name”: "Ja" + “ne”,
        'age': 5 * 5,
        "city": "London",
        male: fAlsE
    }
],  // 列表

{A,B,C} * {1,2,3}, // 笛卡尔积

(1, 2), // 元组

{1, 2, 3}, // 集合

--draw circle --rotate 90 --fill red --position (0,0) (1,1) (2,2), // 参数组

R"delimiter(
    multi-line
    string
)delimiter", // 多行字符串

$"YmFzZTY0IGVuY29kZWQgYmFzZTY0IGVuY29kZWQ=", // Base64 编码字符串

[1, 2, 3] + [4, 5, 6], // 连接表达式

[1, 2] * [3, 4], // 分量乘法

[1 ,2] * 3 // 列表乘法
"""

print(json.decode(fjson_str))
```
