# fJson

[English](readme-en.md) | [中文](readme.md)

fJson is a lenient JSON parser that supports comments, unquoted keys, arrays, tuples, etc. It does not support special character escaping but supports multiline strings, multiline comments, and full-width quotes.

The original intention was to solve the problem of LLMs' quirks, but later it was found that it could actually be used for other purposes, such as parsing command line arguments. Thus, this project was born.

This project is mainly for Python because Python supports dynamic types, so it can be parsed directly, while C++ and other languages need to implement data structure management themselves.

## Features

- **Dictionary**: Supports unquoted keys
- **List**: Supports standard JSON list format
- **Tuple**: Supports tuple format
- **Argument Group**: Supports `--key value` form of argument groups
- **Multiline String**: Supports `R"delimiter(content)delimiter"` form of multiline strings
- **Base64 Encoded String**: Supports `$"base64 string"` form of Base64 encoded strings
- **Expression Evaluation**: Supports some expression evaluations, such as Cartesian product, string concatenation, conditional expressions, etc.
- _More features are expected to be supported_

## Usage

Except for the `decode` function, other classes are used to parse JSON. The `decode` function is the external interface, which takes a string and returns a parsed object.

### Example

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

## Functions

### decode(json_str: str) -> Any

Parses a JSON string and returns the parsed object.

```python
def decode(json_str):
    """
    Parses a JSON string
    """
    tokens = fJsonLexer().tokenize(json_str)
    tokens = fJsonLexer().reject_comments(tokens)
    tokens = fJsonLexer().concat_negative_number(tokens)
    return fJsonBuilder(tokens).build()
```

## Examples

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
    }, // Dictionary
    {
        “name”: "Ja" + “ne”,
        'age': 5 * 5,
        "city": "London",
        male: fAlsE
    }
],  // List

{A,B,C} * {1,2,3}, // Cartesian product

(1, 2), // Tuple

{1, 2, 3}, // Set

--draw circle --rotate 90 --fill red --position (0,0) (1,1) (2,2), // Argument group

R"delimiter(
    multi-line
    string
)delimiter", // Multiline string

$"YmFzZTY0IGVuY29kZWQgYmFzZTY0IGVuY29kZWQ=", // Base64 encoded string

[1, 2, 3] + [4, 5, 6], // Concatenation expression

[1, 2] * [3, 4], // Element-wise multiplication

[1 ,2] * 3 // List multiplication
"""

print(json.decode(fjson_str))
```
