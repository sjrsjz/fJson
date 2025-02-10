# fJson

[English](readme-en.md) | [中文](readme.md)

fJson is a lenient JSON parser that supports comments, unquoted keys, arrays, tuples, and more. While it doesn't support special character escaping, it does support multi-line strings, multi-line comments, and fullwidth quotes.

Initially created to handle LLM output parsing issues, it later evolved to support additional use cases like command-line argument parsing.

This project is primarily Python-focused, leveraging Python's dynamic typing for direct parsing. Languages like C++ would require custom data structure implementations.

## Features

- **Dictionaries**: Support for unquoted keys
- **Lists**: Support for standard JSON list format
- **Tuples**: Support for tuple format
- **Parameter Groups**: Support for `--key value` style parameter groups
- **Multi-line Strings**: Support for `R"delimiter(content)delimiter"` style multi-line strings
- **Base64 Encoded Strings**: Support for `$"base64string"` style Base64 encoded strings
- **Expression Evaluation**: Support for various expressions like Cartesian products, string concatenation, conditional expressions, etc.
- _More features planned_

## Usage

All classes except the `decode` function are used internally for JSON parsing. The `decode` function serves as the public interface, taking a string input and returning a parsed object.

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

Parse a JSON string and return the parsed object.

```python
def decode(json_str):
    """
    Parse a JSON string
    """
    tokens = fJsonLexer().tokenize(json_str)
    tokens = fJsonLexer().reject_comments(tokens)
    tokens = fJsonLexer().concat_negative_number(tokens)
    return fJsonBuilder(tokens).build()
```

### encode(obj: Any, indent: int = None, multi_line: bool = False, ascii_only: bool = False) -> str

Encode an object into a JSON string.

## Decorators

### @DataClass

Declare a data class with direct fJson serialization support, automatically adding the following methods:
- `json(self, **kwargs) -> str`: Encode object to JSON string, supports `indent`, `multi_line`, `ascii_only` parameters
- `from_json(cls, json_str: str) -> Any`: Parse object from JSON string
- `dict(self) -> dict`: Convert object to dictionary
- `from_dict(cls, data: dict) -> Any`: Parse object from dictionary

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
    }, // dictionary
    {
        "name": "Ja" + "ne",
        'age': 5 * 5,
        "city": "London",
        male: fAlsE
    }
],  // list

{A,B,C} * {1,2,3}, // Cartesian product

(1, 2), // tuple

{1, 2, 3}, // set

--draw circle --rotate 90 --fill red --position (0,0) (1,1) (2,2), // parameter group

R"delimiter(
    multi-line
    string
)delimiter", // multi-line string

$"YmFzZTY0IGVuY29kZWQgYmFzZTY0IGVuY29kZWQ=", // Base64 encoded string

[1, 2, 3] + [4, 5, 6], // concatenation expression

[1, 2] * [3, 4], // element-wise multiplication

[1 ,2] * 3 // list multiplication
"""

print(json.decode(fjson_str))


@json.DataClass
class Person:
    def __init__(self, name: str, age: int, hobbies: list = None, pair: tuple = (), bytestr: bytes = b''):
        self.name = name
        self.age = age
        self.hobbies = hobbies or []
        self.pair = pair
        self.bytestr = bytestr

# Create object
person = Person(name="John", age=25, hobbies=["reading", "running"], pair=(1, ), bytestr=b'base64 encoded base64 encoded')

# Convert to JSON
json_str = person.json(indent = 4, multi_line = True, ascii_only = True)
print("Convert to JSON:")
print(json_str)

# Create new object from JSON
new_person = Person.load_json(json_str)
print("\nRestore from JSON:")
print(f"Name: {new_person.name}")
print(f"Age: {new_person.age}")
print(f"Hobbies: {new_person.hobbies}")
print(f"Tuple: {new_person.pair}")
print(f"Bytes: {new_person.bytestr}")

# Convert to dictionary
person_dict = person.dict()
print("\nConvert to dictionary:")
print(person_dict)

# Create new object from dictionary
dict_person = Person.load_dict(person_dict)
print("\nRestore from dictionary:")
print(f"Name: {dict_person.name}")
print(f"Age: {dict_person.age}")
print(f"Hobbies: {dict_person.hobbies}")
print(f"Tuple: {dict_person.pair}")
print(f"Bytes: {dict_person.bytestr}")
```