# fJson

fJson 是一个宽松格式的 JSON 解析器，支持注释、不带引号的键、数组、元组等，不支持特殊字符转义但支持跨行字符串、支持多行注释，支持全角引号。

本意是为了解决LLMs的抽风问题，后来发现实际还可以添加其他用途，比如解析命令行参数。于是催生了这个项目。

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

除了 

decode

 函数外，其他类都是用于解析 JSON 的，

decode

 函数是对外的接口，传入一个字符串，返回一个解析后的对象。

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
    key7: --key10 value10 --key11 value11,
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

## 类和函数

### 

fJsonLexer



负责将输入字符串分解为 token。

### 

fJsonBuilder



根据 token 构建 JSON 对象。

### 

NextToken



用于获取下一个 token 列表，自动匹配括号。

### 

fJsonDict



用于匹配 JSON 字典。

### 

fJsonList



用于匹配 JSON 列表。

### 

fJsonTuple



用于匹配 JSON 元组。

### 

fJsonSet



用于匹配 JSON 集合。

### 

fJsonValue



用于匹配 JSON 值。

### 

fJsonOrderChange



用于匹配顺序改变的表达式。

### 

fJsonArgument



用于匹配 `--key value` 形式的参数。

### 

fJsonPipe



用于匹配 `A |> B |> C` 形式的管道表达式。

### 

fJsonConcat



用于匹配 `A + B + C` 形式的连接表达式。

### 

fJsonIfExpression



用于匹配 `A ? B : C` 形式的条件表达式。

### 

fJsonMulAndDiv



用于匹配 `A * B / C` 形式的乘除表达式。

### 

fJsonContains



用于匹配 `A in B` 形式的包含表达式。

### 

fJsonFunctionType



用于匹配函数类型 `(A, B) -> (C, D)`。

### 

fJsonLines



用于匹配用分号分隔的多行表达式。

### 

fJsonDeclaration



用于匹配变量声明 

name:type:=value

。

### 

decode



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
if __name__ == "__main__":
    text = """
    (A :> [A,B]) ? ({A: 1, B: 2, C: 3} + {D: 4, E: 5, F: 6}) : ({1, 2, 3} * {4, 5, 6}); test:(A->B):=(A+B)
    """
    try:
        print(decode(text))
    except Exception as e:
        print(e)
```