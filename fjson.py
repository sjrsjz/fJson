"""
# FlexibleJSONParser

## 宽松格式的JSON解析器，支持注释、不带引号的键、数组、元组等，不支持特殊字符转义但支持跨行字符串、支持多行注释，支持全角引号

# 用法

除了decode函数外，其他类都是用于解析JSON的，decode函数是对外的接口，传入一个字符串，返回一个解析后的对象

# JSON格式

## 字典

e.g.
```
{
    key1: value1,
    key2: value2,
    key3: {
        key4: value4,
        key5: value5
    }
}
```

## 列表
e.g.
```
[
    value1,
    value2,
    value3
]
```

## 元组
e.g.
```
(value1, value2, value3)
```
或
```
(value1,)
```

## 参数组
e.g.
``` 
--key1 value1 --key2 value2 ..
```
其中key1, key2为键，value1, value2为值，值允许被省略，省略时值为None

# 例子
``` python
text = '''
--key1 value1 --key2 {
    A: "Hello World",
    B: (
        --key3 --key4 value,
        1,
        (
            ["A", 222] ,
        )
    )
}
'''
print(decode(text))
```

## 字符串

支持多行字符串，支持全角引号，支持base64编码字符串

对于多行字符串，使用`R"delimiter(内容)delimiter"`的形式，delimiter可以是任意字符，但不能包含括号

对于base64编码字符串，使用`$"base64字符串"`的形式，其最终会被解码为二进制字符串
"""
import re
import base64

DEBUG = True

class fJsonTokenType:
    TokenType_COMMENT = 'COMMENT'
    TokenType_NUMBER = 'NUMBER'
    TokenType_STRING = 'STRING'
    TokenType_SYMBOL = 'SYMBOL'
    TokenType_IDENTIFIER = 'IDENTIFIER'
    TokenType_BASE64 = 'BASE64'


class fJsonLexer:
    def tokenize(self, str):
        tokens = []
        currpos = 0

        def skip_space():
            nonlocal currpos
            while currpos < len(str) and str[currpos] in (' ', '\t', '\n', '\r'):
                currpos += 1

        def next_line():
            nonlocal currpos
            while currpos < len(str) and str[currpos] not in ('\n', '\r'):
                currpos += 1

        def test_string(test_str):
            nonlocal currpos
            if currpos + len(test_str) > len(str):
                return False
            return str[currpos:currpos + len(test_str)] == test_str

        def test_number(pos):
            number_pattern = re.compile(r'^\d*\.?\d+([eE][-+]?\d+)?')
            match = number_pattern.match(str[pos:])
            return match.end() if match else 0

        def read_number():
            nonlocal currpos
            length = test_number(currpos)
            if length:
                current_token = str[currpos:currpos + length]
                currpos += length
                return current_token
            return None

        def read_base64():
            nonlocal currpos
            current_token = ''
            if test_string('$"'):
                currpos += 2
                while currpos < len(str):
                    if str[currpos] == '\\':
                        currpos += 1
                        if currpos < len(str):
                            escape_char = str[currpos]
                            if escape_char == 'n':
                                current_token += '\n'
                            elif escape_char == 't':
                                current_token += '\t'
                            elif escape_char in ('"', '\\'):
                                current_token += escape_char
                            elif escape_char == 'u':
                                try:
                                    currpos += 1
                                    if currpos < len(str):
                                        hex_str = str[currpos:currpos + 4]
                                        current_token += chr(int(hex_str, 16))
                                        currpos += 3
                                    else:
                                        return None  # Error: unexpected end of string
                                except ValueError:
                                    return None
                            else:
                                current_token += '\\' + escape_char
                            currpos += 1
                        else:
                            return None  # Error: unexpected end of string
                    elif str[currpos] == '"':
                        currpos += 1
                        return current_token
                    else:
                        current_token += str[currpos]
                        currpos += 1
        def read_string():
            nonlocal currpos
            current_token = ''
            if test_string('R"'):
                currpos += 2
                divider = ''
                while currpos < len(str) and str[currpos] != '(':
                    divider += str[currpos]
                    currpos += 1
                if currpos < len(str):
                    currpos += 1  # skip '('
                    end_divider = ')' + divider + '"'
                    while currpos < len(str) and not test_string(end_divider):
                        if str[currpos] == '\\':  # Handle escape sequences
                            currpos += 1
                            if currpos < len(str):
                                escape_char = str[currpos]
                                if escape_char == 'n':
                                    current_token += '\n'
                                elif escape_char == 't':
                                    current_token += '\t'
                                elif escape_char in ('"', '\\'):
                                    current_token += escape_char
                                elif escape_char == 'u':
                                    try:
                                        currpos += 1
                                        if currpos < len(str):
                                            hex_str = str[currpos:currpos + 4]
                                            current_token += chr(int(hex_str, 16))
                                            currpos += 3
                                        else:
                                            return None  # Error: unexpected end of string
                                    except ValueError:
                                        return None
                                else:
                                    current_token += '\\' + escape_char  # Keep unrecognized escape sequences
                                currpos += 1
                            else:
                                return None  # Error: unexpected end of string
                        else:
                            current_token += str[currpos]
                            currpos += 1
                    if currpos < len(str):
                        currpos += len(end_divider)  # Skip the closing delimiter
                        return current_token
            match_pair = {
                '"': '"',
                "'": "'",
                '“': '”'
                # Add more pairs as needed
            }
            start_char = str[currpos]
            if start_char in match_pair:
                currpos += 1
                while currpos < len(str):
                    if str[currpos] == '\\':
                        currpos += 1
                        if currpos < len(str):
                            escape_char = str[currpos]
                            if escape_char == 'n':
                                current_token += '\n'
                            elif escape_char == 't':
                                current_token += '\t'
                            elif escape_char in (start_char, '\\'):
                                current_token += escape_char
                            elif escape_char == 'u':
                                try:
                                    currpos += 1
                                    if currpos < len(str):
                                        hex_str = str[currpos:currpos + 4]
                                        current_token += chr(int(hex_str, 16))
                                        currpos += 3
                                    else:
                                        return None  # Error: unexpected end of string
                                except ValueError:
                                    return None
                            else:
                                current_token += '\\' + escape_char
                            currpos += 1
                        else:
                            return None  # Error: unexpected end of string
                    elif str[currpos] == match_pair[start_char]:
                        currpos += 1
                        return current_token
                    else:
                        current_token += str[currpos]
                        currpos += 1

            return None


        def read_token():
            nonlocal currpos
            current_token = ''
            while currpos < len(str):
                if str[currpos] in (' ', '\t', '\n', '\r', '\'', '"'):
                    break
                if currpos < len(str) - 1:
                    two_char = str[currpos:currpos + 2]
                    if self.is_operator(two_char, 0):
                        break
                one_char = str[currpos]
                if self.is_operator(one_char, 0):
                    break
                current_token += one_char
                currpos += 1
            return current_token

        def read_operator():
            nonlocal currpos
            if currpos < len(str) - 1:
                two_char = str[currpos:currpos + 2]
                if self.is_operator(two_char, 0):
                    currpos += 2
                    return two_char
            if currpos < len(str):
                one_char = str[currpos]
                if self.is_operator(one_char, 0):
                    currpos += 1
                    return one_char
            return None

        def read_comment():
            nonlocal currpos
            current_token = ''
            if test_string('//'):
                currpos += 2
                while currpos < len(str) and str[currpos] not in ('\n', '\r'):
                    current_token += str[currpos]
                    currpos += 1
                return current_token
            if test_string('/*'):
                currpos += 2
                while currpos < len(str) and not test_string('*/'):
                    current_token += str[currpos]
                    currpos += 1
                if currpos < len(str):
                    currpos += 2  # Skip closing */
                return current_token
            return None

        while True:
            skip_space()
            if currpos >= len(str):
                break
            
            token = None
            position = currpos

            if (comment := read_comment()) is not None:
                tokens.append({'token': comment, 'type': fJsonTokenType.TokenType_COMMENT, 'position': position})
            elif (number := read_number()) is not None:
                tokens.append({'token': number, 'type': fJsonTokenType.TokenType_NUMBER, 'position': position})
            elif (string := read_string()) is not None:
                tokens.append({'token': string, 'type': fJsonTokenType.TokenType_STRING, 'position': position})
            elif (string := read_base64()) is not None:
                tokens.append({'token': string, 'type': fJsonTokenType.TokenType_BASE64, 'position': position})
            elif (operator := read_operator()) is not None:
                tokens.append({'token': operator, 'type': fJsonTokenType.TokenType_SYMBOL, 'position': position})
            else:
                token = read_token()
                if token:
                    tokens.append({'token': token, 'type': fJsonTokenType.TokenType_IDENTIFIER, 'position': position})

        return tokens

    def is_operator(self, t, type):
        l = (t in {"+", "-", "*", "/", "\\", "%", "&", "!", "^", "~", "=", "==", ">", "<", "<=", ">=", "!=", "?=", "|", "?", ":>",
                    "&&", ",", ".", "\n", ":", "->", "<<", ">>", "/*", "*/", ";", " ", ":=", "|>", "<|", "::", "--", "=>", "++", "||", ">>", "<<"})
        if type == 0:
            l = l or (t in {"(", ")", "[", "]", "{", "}"})
        return l

    def reject_comments(self, tokens):
        return [token for token in tokens if token['type'] != fJsonTokenType.TokenType_COMMENT]
    
    def concat_multi_line_string(self, tokens):
        new_tokens = []
        multi_line_string = None
        start_positon = None
        for token in tokens:
            if token['type'] == fJsonTokenType.TokenType_STRING:
                if multi_line_string is None:
                    multi_line_string = token['token']
                    start_positon = token['position']
                else:
                    multi_line_string += token['token']
            else:
                if multi_line_string is not None:
                    new_tokens.append({'token': multi_line_string, 'type': fJsonTokenType.TokenType_STRING, 'position': start_positon})
                    multi_line_string = None
                    start_positon = None
                new_tokens.append(token)
        if multi_line_string is not None:
            new_tokens.append({'token': multi_line_string, 'type': fJsonTokenType.TokenType_STRING, 'position': start_positon})
        return new_tokens
    
    # 合并负数
    def concat_negative_number(self, tokens):
        new_tokens = []
        offset = 0
        while offset < len(tokens):
            if tokens[offset]['token'] == '-' and tokens[offset]['type'] == fJsonTokenType.TokenType_SYMBOL:
                if offset + 1 < len(tokens) and tokens[offset + 1]['type'] == fJsonTokenType.TokenType_NUMBER and (offset == 0 or tokens[offset - 1]['type'] == fJsonTokenType.TokenType_SYMBOL):
                    new_tokens.append({'token': '-' + tokens[offset + 1]['token'], 'type': fJsonTokenType.TokenType_NUMBER, 'position': tokens[offset]['position']})
                    offset += 2
                    continue
            new_tokens.append(tokens[offset])
            offset += 1
        return new_tokens

class fJsonParser:
    def __init__(self):
        self.lexer = fJsonLexer()

    def parse(self, text):
        tokens = self.lexer.tokenize(text)
        tokens = self.lexer.reject_comments(tokens)

class fJsonBuilder:
    def __init__(self,tokens):
        self.tokens = tokens
    def build(self):
        return fJsonValue(self.tokens).match()
        

class NextToken:
    # 用于获取下一个token list的类，自动匹配括号
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
    def next(self, start_idx:int):
        stack = []
        next_tokens = []
        if start_idx >= len(self.tokens):
            return next_tokens
        while True:
            if self.tokens[start_idx]['token'] in ('{', '[', '(') and self.tokens[start_idx]['type'] == fJsonTokenType.TokenType_SYMBOL:
                stack.append(self.tokens[start_idx]['token'])
                next_tokens.append(self.tokens[start_idx])
            elif self.tokens[start_idx]['token'] in ('}', ']', ')') and self.tokens[start_idx]['type'] == fJsonTokenType.TokenType_SYMBOL:
                if len(stack) == 0:
                    return next_tokens
                    #raise Exception('Unmatched bracket')
                poped = stack.pop()
                if (poped == '{' and self.tokens[start_idx]['token'] != '}') or \
                    (poped == '[' and self.tokens[start_idx]['token'] != ']') or \
                    (poped == '(' and self.tokens[start_idx]['token'] != ')'):
                    raise Exception('Unmatched bracket')
                
                next_tokens.append(self.tokens[start_idx])
            else:
                next_tokens.append(self.tokens[start_idx])
            start_idx += 1            
            if len(stack) == 0 or start_idx >= len(self.tokens):
                break
        return next_tokens


class fJsonDict:
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个JSON字典

        if len(self.tokens) < 2:
            return None
        
        if self.tokens[0]['token'] != '{' or self.tokens[-1]['token'] != '}':
            return None
        
        match_dict = {}

        offset = 1
        key_token = []
        value_token = []
        is_value = False

        key_list = []
        value_list = []
        while offset < len(self.tokens) - 1:
            next_token = NextToken(self.tokens).next(offset)
            if len(next_token) == 0:
                break
            if len(next_token) == 1 and next_token[0]['type'] == fJsonTokenType.TokenType_SYMBOL and next_token[0]['token'] == ':':
                is_value = True
                offset += 1
                continue
            if len(next_token) == 1 and next_token[0]['type'] == fJsonTokenType.TokenType_SYMBOL and next_token[0]['token'] == ',':
                key_list.append(key_token)
                value_list.append(value_token)
                key_token = []
                value_token = []
                is_value = False
                offset += 1
                continue
            if is_value:
                value_token += next_token
            else:
                key_token += next_token
            offset += len(next_token)
            
        key_list.append(key_token)
        value_list.append(value_token)

        for value in value_list:
            if len(value) == 0:
                return None

        for i in range(len(key_list)):
            key = fJsonBuilder(key_list[i]).build()
            value = fJsonBuilder(value_list[i]).build()
            if key is None:
                continue
            try:
                key = str(key)
            except:
                raise Exception('Invalid JSON key')
            match_dict[key] = value
        if DEBUG:
            print("Dict", match_dict)
        return match_dict

class fJsonList:
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个JSON列表
        if len(self.tokens) < 2:
            return None
        if self.tokens[0]['token'] != '[' or self.tokens[-1]['token'] != ']':
            return None
        
        match_list = []
        tmp_list = []

        offset = 1
        while offset < len(self.tokens):
            next_token = NextToken(self.tokens).next(offset)
            if len(next_token) == 0:
                break
            if len(next_token) == 1 and next_token[0]['type'] == fJsonTokenType.TokenType_SYMBOL and next_token[0]['token'] == ',':
                match_list.append(tmp_list)
                tmp_list = []
                offset += 1
                continue
            tmp_list += next_token
            offset += len(next_token)
        match_list.append(tmp_list)
        
        return_list = []
        for x in match_list:
            if x == []:
                continue
            return_list.append(fJsonBuilder(x).build())
        if DEBUG:
            print("List", return_list)
        return return_list

class fJsonTuple:
    # 用于匹配JSON元组
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个JSON元组
        #if len(self.tokens) < 2:
        #    return None
        #if self.tokens[0]['token'] != '(' or self.tokens[-1]['token'] != ')':
        #    return None
        
        match_list = []

        arg = []

        offset = 0
        while offset < len(self.tokens):
            if self.tokens[offset]['type'] == fJsonTokenType.TokenType_SYMBOL and self.tokens[offset]['token'] == ',':
                match_list.append(arg)
                arg = []
                offset += 1
                continue
            next_token = NextToken(self.tokens).next(offset)
            arg += next_token
            offset += len(next_token)

        match_list.append(arg)


        new_list = []
        for x in match_list:
            if x != []:
                new_list.append(x)

        if len(match_list) == 1:
            return None

        return_list = []
        for x in new_list:
            return_list.append(fJsonBuilder(x).build())
        if DEBUG:
            print("Tuple", return_list)
        return tuple(return_list)

class fJsonSet:
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个JSON集合
        if len(self.tokens) < 2:
            return None
        if self.tokens[0]['token'] != '{' or self.tokens[-1]['token'] != '}':
            return None
        
        match_list = []
        tmp_list = []
        offset = 1
        while offset < len(self.tokens):
            next_token = NextToken(self.tokens).next(offset)
            if len(next_token) == 0:
                break
            if len(next_token) == 1 and next_token[0]['type'] == fJsonTokenType.TokenType_SYMBOL and next_token[0]['token'] == ',':
                match_list.append(tmp_list)
                tmp_list = []
                offset += 1
                continue
            tmp_list += next_token
            offset += len(next_token)
        match_list.append(tmp_list)
        set_list = [fJsonBuilder(x).build() for x in match_list]
        if DEBUG:
            print("Set", set_list)
        return set(set_list)


class fJsonValue:
    # 用于匹配JSON值
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个JSON值
        def match_json_value(self):
            matchers = [
                fJsonLines,
                fJsonTuple,
                fJsonDeclaration,
                fJsonPipe,
                fJsonIfExpression,
                fJsonConcat,
                fJsonMulAndDiv,
                fJsonContains,
                fJsonArgument,
                fJsonFunctionType,
                fJsonDict,
                fJsonSet,
                fJsonList,
                fJsonOrderChange
            ]

            for matcher in matchers:
                result = matcher(self.tokens).match()
                if result is not None:
                    return result
            return None
        
        result = match_json_value(self)
        if result is not None:
            return result
        
        if len(self.tokens) == 0:
            return None
        if len(self.tokens) == 1:
            if self.tokens[0]['type'] == fJsonTokenType.TokenType_NUMBER:
                if self.tokens[0]['token'].isdigit() or self.tokens[0]['token'].lstrip('-').isdigit():
                    return int(self.tokens[0]['token'])
                return float(self.tokens[0]['token'])
            if self.tokens[0]['type'] == fJsonTokenType.TokenType_STRING:
                return self.tokens[0]['token']
            if self.tokens[0]['type'] == fJsonTokenType.TokenType_BASE64:
                try:
                    return base64.b64decode(self.tokens[0]['token'])
                except:
                    raise Exception('Invalid base64 string')
            if self.tokens[0]['type'] == fJsonTokenType.TokenType_IDENTIFIER:
                if self.tokens[0]['token'].lower() == 'true':
                    return True
                if self.tokens[0]['token'].lower() == 'false':
                    return False
                if self.tokens[0]['token'].lower() in ('null', 'none'):
                    return None                
                return self.tokens[0]['token']
            raise Exception('Invalid JSON value: ' + self.tokens[0]['token'])        
        

        raise Exception('Invalid JSON value')

class fJsonOrderChange:
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        if len(self.tokens) < 2:
            return None
        if self.tokens[0]['token'] != '(' or self.tokens[-1]['token'] != ')':
            return None
        if DEBUG:
            print("OrderChange", get_str_from_tokens(self.tokens[1:-1]))
        return fJsonValue(self.tokens[1:-1]).match()


class fJsonArgument:
    # 用于匹配 --key value 形式的参数
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        # 检查是否是一个参数组
        size_tokens = len(self.tokens)
        if size_tokens < 2:
            return None
        if self.tokens[0]['type'] != fJsonTokenType.TokenType_SYMBOL or self.tokens[0]['token'] != '--':
            return None
        # --key开头，则认定为参数组

        match_dict = {}
        match_list = []
        offset = 0
        pair = [None, []]
        while offset < size_tokens:
            if self.tokens[offset]['type'] == fJsonTokenType.TokenType_SYMBOL and self.tokens[offset]['token'] == '--':
                offset += 1
                if pair[0] is not None:
                    match_list.append(pair)
                pair = [None, []]
                continue
            next_token = NextToken(self.tokens).next(offset)
            if pair[0] is None:
                pair[0] = next_token
                offset += len(next_token)
                continue
            pair[1].append(next_token)
            offset += len(next_token)
        if pair[0] is None:
            return None # 非法格式
        match_list.append(pair)

        for x in match_list:
            key = fJsonBuilder(x[0]).build()
            value = []
            for y in x[1]:
                value.append(fJsonBuilder(y).build())
            match_dict[key] = value
        if DEBUG:
            print("Argument", match_dict)
        return match_dict
            
class fJsonPipe:
    """
    A |> B |> C，结合方式从左到右
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        left = NextToken(self.tokens).next(offset)
        offset += len(left)

        if len(left) == 0:
            return None
        
        middle = NextToken(self.tokens).next(offset)
        offset += len(middle)
        if len(middle) == 0:
            return None
        
        if middle[0]['type'] != fJsonTokenType.TokenType_SYMBOL or middle[0]['token'] != '|>':
            return None
        
        right = self.tokens[offset:]
        left_value = fJsonBuilder(left).build()
        right_value = fJsonBuilder(right).build()
        if DEBUG:
            print("Pipe", left_value, right_value)
        return (left_value, right_value)

class fJsonConcat:
    """
    A + B + C，结合方式从左到右
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        left = NextToken(self.tokens).next(offset)
        offset += len(left)

        if len(left) == 0:
            return None
        
        middle = NextToken(self.tokens).next(offset)
        offset += len(middle)
        if len(middle) == 0:
            return None
        if middle[0]['type'] != fJsonTokenType.TokenType_SYMBOL or middle[0]['token'] != '+':
            return None
        
        right = self.tokens[offset:]
        
        left_value = fJsonBuilder(left).build()
        right_value = fJsonBuilder(right).build()

        if DEBUG:
            print("Concat", left_value, right_value)

        if isinstance(left_value, str) and isinstance(right_value, str):
            return left_value + right_value
        if isinstance(left_value, list) and isinstance(right_value, list):
            return left_value + right_value
        if isinstance(left_value, tuple) and isinstance(right_value, tuple):
            return left_value + right_value
        if isinstance(left_value, dict) and isinstance(right_value, dict):
            left_value.update(right_value)
            return left_value
        if isinstance(left_value, set) and isinstance(right_value, set):
            return left_value.union(right_value)
        if isinstance(left_value, int) and isinstance(right_value, int):
            return left_value + right_value
        if type(left_value) in [int, float] and type(right_value) in [int, float]:
            return float(left_value + right_value)
        if isinstance(left_value, bytes) and isinstance(right_value, bytes):
            return left_value + right_value
        
        raise Exception('Invalid concat operation: ' + str(left_value) + ' + ' + str(right_value) + '\n\tFound types: ' + str(type(left_value)) + ', ' + str(type(right_value)))

class fJsonIfExpression:
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        condition = NextToken(self.tokens).next(offset)
        offset += len(condition)
        if len(condition) == 0:
            return None
        if offset >= len(self.tokens):
            return None
        if self.tokens[offset]['type'] != fJsonTokenType.TokenType_SYMBOL or self.tokens[offset]['token'] != '?':
            return None
        offset += 1
        true_value = NextToken(self.tokens).next(offset)
        offset += len(true_value)
        if len(true_value) == 0:
            return None
        if offset >= len(self.tokens):
            return None
        if self.tokens[offset]['type'] != fJsonTokenType.TokenType_SYMBOL or self.tokens[offset]['token'] != ':':
            return None
        offset += 1
        false_value = self.tokens[offset:]

        condition_value = fJsonBuilder(condition).build()
        true_value = fJsonBuilder(true_value).build()
        false_value = fJsonBuilder(false_value).build()

        if type(condition_value) != bool:
            raise Exception('Invalid if condition: ' + str(condition_value))
        
        if DEBUG:
            print("IfExpression", condition_value, true_value, false_value)

        return true_value if condition_value else false_value

class fJsonMulAndDiv:
    """
    A * B / C，结合方式从左到右
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        left = NextToken(self.tokens).next(offset)
        offset += len(left)
        if len(left) == 0:
            return None
        middle = NextToken(self.tokens).next(offset)
        offset += len(middle)
        if len(middle) == 0:
            return None
        if middle[0]['type'] != fJsonTokenType.TokenType_SYMBOL or middle[0]['token'] not in ('*', '/'):
            return None
        right = self.tokens[offset:]
        left_value = fJsonBuilder(left).build()
        right_value = fJsonBuilder(right).build()

        if DEBUG:
            print("MulAndDiv", left_value, middle[0]['token'], right_value)

        if isinstance(left_value, list) and isinstance(right_value, list):
            if len(left_value) != len(right_value):
                raise Exception('Invalid mul/div operation: ' + str(left_value) + ' ' + middle[0]['token'] + ' ' + str(right_value)+ '\n\tExpected same length, but found ' + str(len(left_value)) + ', ' + str(len(right_value)))
            if middle[0]['token'] == '*':
                return [left_value[i] * right_value[i] for i in range(len(left_value))]
            else:
                return [left_value[i] / right_value[i] for i in range(len(left_value))]
        if type(left_value) in [int, float] and type(right_value) in [int, float]:
            if middle[0]['token'] == '*':
                return left_value * right_value
            if middle[0]['token'] == '/':
                return left_value / right_value
        if middle[0]['token'] == '/':
            raise Exception('Invalid div operation: ' + str(left_value) + ' / ' + str(right_value))
        if isinstance(left_value, str) and isinstance(right_value, int):
            return left_value * right_value
        if isinstance(left_value, int) and isinstance(right_value, str):
            return right_value * left_value
        if isinstance(left_value, list) and isinstance(right_value, int):
            return left_value * right_value
        if isinstance(left_value, int) and isinstance(right_value, list):
            return right_value * left_value
        if isinstance(left_value, bytes) and isinstance(right_value, int):
            return left_value * right_value
        if isinstance(left_value, int) and isinstance(right_value, bytes):
            return right_value * left_value
        if isinstance(left_value, set) and isinstance(right_value, set):
            # 笛卡尔积
            return {(x, y) for x in left_value for y in right_value}

            
        raise Exception('Invalid mul/div operation: ' + str(left_value) + ' ' + middle[0]['token'] + ' ' + str(right_value) + '\n\tFound types: ' + str(type(left_value)) + ', ' + str(type(right_value)))

class fJsonContains:
    """
    A in B，判断A是否在B中, 为了引入符号，使用A :> B
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        left = NextToken(self.tokens).next(offset)
        offset += len(left)
        if len(left) == 0:
            return None
        middle = NextToken(self.tokens).next(offset)
        offset += len(middle)
        if len(middle) == 0:
            return None
        if middle[0]['type'] != fJsonTokenType.TokenType_SYMBOL or middle[0]['token'] != ':>':
            return None
        right = self.tokens[offset:]
        left_value = fJsonBuilder(left).build()
        right_value = fJsonBuilder(right).build()

        if DEBUG:
            print("Contains", left_value, right_value)

        if isinstance(right_value, list):
            return left_value in right_value
        if isinstance(right_value, tuple):
            return left_value in right_value
        if isinstance(right_value, set):
            return left_value in right_value
        if isinstance(right_value, dict):
            return left_value in right_value
        if isinstance(right_value, str) and isinstance(left_value, str):
            return left_value in right_value
        if isinstance(right_value, bytes) and isinstance(left_value, bytes):
            return left_value in right_value

        raise Exception('Invalid contains operation: ' + str(left_value) + ' in ' + str(right_value) + '\n\tFound types: ' + str(type(left_value)) + ', ' + str(type(right_value)))


class fJsonFunctionType:
    """
    函数类型
    (A, B) -> (C, D)
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        left = NextToken(self.tokens).next(offset)
        offset += len(left)
        if len(left) == 0:
            return None
        middle = NextToken(self.tokens).next(offset)
        offset += len(middle)
        if len(middle) != 1:
            return None
        if middle[0]['type'] != fJsonTokenType.TokenType_SYMBOL or middle[0]['token'] != '->':
            return None
        right = self.tokens[offset:]
        
        left_value = fJsonBuilder(left).build()
        right_value = fJsonBuilder(right).build()

        if not isinstance(left_value, tuple):
            left_value = (left_value,)
        if not isinstance(right_value, tuple):
            right_value = (right_value,)

        print("FunctionType", left_value, right_value)
        return (left_value, right_value)



class fJsonLines:
    """
    匹配用分号分隔的多行表达式
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        lines = []
        tmp_tokens = []
        while offset < len(self.tokens):
            line = NextToken(self.tokens).next(offset)
            offset += len(line)
            if len(line) == 0:
                return None
            if len(line) == 1 and line[0]['type'] == fJsonTokenType.TokenType_SYMBOL and line[0]['token'] == ';':
                    lines.append(tmp_tokens)
                    tmp_tokens = []
                    continue
            tmp_tokens += line
        lines.append(tmp_tokens)
        if len(lines) < 2:
            return None
        
        return [fJsonBuilder(x).build() for x in lines]

class fJsonDeclaration:
    """
    匹配变量声明
    name:type:=value
    """
    def __init__(self, tokens):
        self.tokens = tokens
    def match(self):
        offset = 0
        name = NextToken(self.tokens).next(offset)
        offset += len(name)
        if len(name) == 0:
            return None
        if offset >= len(self.tokens):
            return None
        if self.tokens[offset]['type'] != fJsonTokenType.TokenType_SYMBOL or self.tokens[offset]['token'] != ':':
            return None
        offset += 1
        type_ = NextToken(self.tokens).next(offset)
        offset += len(type_)
        if len(type_) == 0:
            return None
        if offset >= len(self.tokens):
            return None
        if self.tokens[offset]['type'] != fJsonTokenType.TokenType_SYMBOL or self.tokens[offset]['token'] != ':=':
            return None
        offset += 1
        value = self.tokens[offset:]
        name = fJsonBuilder(name).build()
        type_ = fJsonBuilder(type_).build()
        #value = fJsonBuilder(value).build()
        if DEBUG:
            print("Declaration", name, type_, get_str_from_tokens(value))
        return (name, type_, value)

def get_str_from_tokens(tokens):
    return ''.join([x['token'] for x in tokens])

def decode(json_str):
    """
    解析JSON字符串
    """
    tokens = fJsonLexer().tokenize(json_str)
    tokens = fJsonLexer().reject_comments(tokens)
    tokens = fJsonLexer().concat_negative_number(tokens)
    #tokens = Lexer().concat_multi_line_string(tokens)
    return fJsonBuilder(tokens).build()


if __name__ == "__main__":
    text = """
    (A :> [A,B]) ? ({A: 1, B: 2, C: 3} + {D: 4, E: 5, F: 6}) : ({1, 2, 3} * {4, 5, 6}); test:(A->B):=(A+B)
    """
    try:
        print(decode(text))
    except Exception as e:
        print(e)