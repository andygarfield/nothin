from dataclasses import dataclass
from enum import Enum


@dataclass
class StringRef:
    start_index: int
    len: int


class ParseState(int, Enum):
    EXPECTING_VALUE = 0
    AFTER_OBJECT_VALUE = 1
    AFTER_ARRAY_VALUE = 2
    AFTER_OBJECT_START = 3
    AFTER_OBJECT_KEY = 4
    AFTER_KEY_STRING_CHAR = 5
    AFTER_VAL_STRING_CHAR = 6
    AFTER_NUM_SIGN = 7
    AFTER_NUM_PRE_DECIMAL_DIGIT = 8
    AFTER_NUM_DECIMAL_POINT = 9
    AFTER_NUM_POST_DECIMAL_DIGIT = 10
    AFTER_NUM_E = 11
    AFTER_NUM_E_SIGN = 12
    AFTER_NUM_E_DIGIT = 13


class TokenType(int, Enum):
    ERROR = 0
    STRING = 1
    NUMBER = 2
    TRUE = 3
    FALSE = 4
    NULL = 5
    OBJECT_START = 6
    OBJECT_END = 7
    ARRAY_START = 8
    ARRAY_END = 9


class Container(int, Enum):
    ARRAY = 0
    OBJECT = 1


WHITESPACE = {" ", "\t", "\r", "\n"}
COMMA = {","}
COLON = {":"}
DOUBLE_QUOTE = {'"'}
ONE_THROUGH_NINE = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
DIGIT = {"0"} | ONE_THROUGH_NINE
DECIMAL_POINT = {"."}
NUM_EXPONENT = {"E"}
NUM_SIGN = {"-", "+"}
VALUE_START_CHARS = DIGIT | DOUBLE_QUOTE | {"{", "[", "t", "f", "n", "+", "-"}

valid_chars = {
    ParseState.EXPECTING_VALUE: VALUE_START_CHARS | WHITESPACE,
    # TODO: maybe these should just be a single thing after all
    ParseState.AFTER_OBJECT_VALUE: COMMA | WHITESPACE,
    ParseState.AFTER_ARRAY_VALUE: COMMA | WHITESPACE,
    ParseState.AFTER_OBJECT_START: DOUBLE_QUOTE | WHITESPACE,
    ParseState.AFTER_OBJECT_KEY: COLON | WHITESPACE,
    ParseState.AFTER_KEY_STRING_CHAR: DOUBLE_QUOTE,  # special
    ParseState.AFTER_VAL_STRING_CHAR: DOUBLE_QUOTE,  # special
    ParseState.AFTER_NUM_SIGN: DIGIT,
    ParseState.AFTER_NUM_PRE_DECIMAL_DIGIT: DIGIT | DECIMAL_POINT | NUM_EXPONENT,
    ParseState.AFTER_NUM_DECIMAL_POINT: DIGIT,
    ParseState.AFTER_NUM_POST_DECIMAL_DIGIT: DIGIT | NUM_EXPONENT,
    ParseState.AFTER_NUM_E: NUM_SIGN | DIGIT,
    ParseState.AFTER_NUM_E_SIGN: DIGIT,
    ParseState.AFTER_NUM_E_DIGIT: DIGIT | WHITESPACE,  # special
}
# ParseState.BEFORE_OBJECT_KEY: {
#    TokenType.STRING,
#    TokenType.WHITESPACE,
#    TokenType.OBJECT_END,
# },
# ParseState.AFTER_OBJECT_KEY: {
#    TokenType.COLON,
#    TokenType.WHITESPACE,
# },
# ParseState.AFTER_OBJECT_VALUE: {
#    TokenType.COMMA,
#    TokenType.WHITESPACE,
#    TokenType.OBJECT_END,
# },
# ParseState.AFTER_ARRAY_VALUE: {
#    TokenType.COMMA,
#    TokenType.WHITESPACE,
#    TokenType.ARRAY_END,
# },
# ParseState.AFTER_NUM_SIGN: {
#    TokenType.DIGITS,
# },
# ParseState.AFTER_NUM_DECIMAL_POINT: {
#    TokenType.DIGITS,
# },
# ParseState.AFTER_NUM_E: {
#    TokenType.DIGITS,
#    TokenType.MINUS,
#    TokenType.PLUS,
# },


@dataclass
class Token:
    token_type: TokenType
    data: StringRef | None


def main():
    tokenize("{}")

    pass


def tokenize(buf: str):
    container_stack: list[Container] = []
    parse_state: ParseState = ParseState.EXPECTING_VALUE
    value_start: int = -1
    i: int = 0

    def find_container_parse_state():
        global parse_state
        match container_stack[-1]:
            case Container.ARRAY:
                parse_state = ParseState.AFTER_ARRAY_VALUE
            case Container.OBJECT:
                parse_state = ParseState.AFTER_OBJECT_VALUE

    while i < len(buf):
        char = buf[i]

        # depending on the state which the parser is in, there are a finite
        # amount of valid characters
        if char not in valid_chars[parse_state]:
            yield Token(token_type=TokenType.ERROR, data=None)

        i += 1

    if len(container_stack) != 0:
        # TODO: may not error here as we can just keep parsing new values after
        # others end. JQ does this for instance.
        yield Token(token_type=TokenType.ERROR, data=None)

    #    if skip_to > i:
    #        continue

    # if number_start >= 0 and char in number_chars:
    #    continue

    # ord_num = ord(char)
    # if 48 <= ord_num <= 57:
    #    if number_start == -1:
    #        number_start = i
    #        continue
    # elif number_start >= 0:
    #    yield Token(token_type=TokenType.NUMBER, data=StringRef(start_index=number_start, len=i - number_start))
    #    number_start = -1


#        match char:
#            case "{":
#                assert TokenType.OBJECT_START in valid_tokens[parse_state]
#                yield Token(token_type=TokenType.OBJECT_START, data=None)
#                parse_state = ParseState.BEFORE_OBJECT_KEY
#                container_stack.append(Container.OBJECT)
#            case "}":
#                assert TokenType.OBJECT_END in valid_tokens[parse_state]
#                yield Token(token_type=TokenType.OBJECT_END, data=None)
#                _ = container_stack.pop()
#                if len(container_stack) == 0:
#                    # TODO: may not need this token
#                    yield Token(TokenType.END, data=None)
#                    parse_state = ParseState.EOF
#                find_container_parse_state()
#            case '"':
#                assert TokenType.STRING in valid_tokens[parse_state]
#                if string_start >= 0 and prev_char != "\\":
#                    yield Token(
#                        token_type=TokenType.STRING,
#                        data=StringRef(start_index=string_start, len=i - string_start),
#                    )
#                    parse_state = ParseState.BEFORE_OBJECT_KEY
#                    string_start = -1
#                else:
#                    skip_to = i + 2
#                    string_start = i + 1
#            case "t" | "n":
#                assert TokenType.STRING in valid_tokens[parse_state]
#                if len(buf) < i + 4:
#                    yield Token(token_type=TokenType.ERROR, data=None)
#                val = buf[i : i + 4]
#                match val:
#                    case "true":
#                        skip_to = i + 4
#                        yield Token(token_type=TokenType.TRUE, data=None)
#                    case "null":
#                        skip_to = i + 4
#                        yield Token(token_type=TokenType.NULL, data=None)
#                    case _:
#                        yield Token(token_type=TokenType.ERROR, data=StringRef(start_index=i, len=0))
#
#            case "f":
#                if len(buf) < i + 5:
#                    yield Token(token_type=TokenType.ERROR, data=None)
#                val = buf[i : i + 5]
#                if val == "false":
#                    skip_to = i + 5
#                    yield Token(token_type=TokenType.FALSE, data=None)
#                else:
#                    yield Token(token_type=TokenType.ERROR, data=None)
#            case ":":
#                yield Token(token_type=TokenType.COLON, data=None)
#                parse_state = ParseState.EXPECTING_VALUE
#            case ",":
#                yield Token(token_type=TokenType.COMMA, data=None)
#            case "[":
#                yield Token(token_type=TokenType.ARRAY_START, data=None)
#                parse_state = ParseState.EXPECTING_VALUE
#                container_stack.append(Container.ARRAY)
#            case "]":
#                yield Token(token_type=TokenType.ARRAY_END, data=None)
#                if len(container_stack) == 0:
#                    # TODO: may not need this token
#                    yield Token(TokenType.END, data=None)
#                    parse_state = ParseState.EOF
#                find_container_parse_state()
#                _ = container_stack.pop()
#            case _:
#                pass
#        prev_char = char


if __name__ == "__main__":
    main()
