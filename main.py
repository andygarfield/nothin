from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class StringRef:
    start_index: int
    len: int


# class ParseState(int, Enum):
#    EXPECTING_VALUE = 0
#    AFTER_VALUE = 1
#    AFTER_ARRAY_START = 2
#    AFTER_ARRAY_END = 3
#    AFTER_OBJECT_START = 4
#    AFTER_OBJECT_END = 5
#    AFTER_COMMA = 6
#    AFTER_COLON = 7
#    END = 8
# AFTER_NUM_SIGN = 7
# AFTER_NUM_PRE_DECIMAL_DIGIT = 8
# AFTER_NUM_DECIMAL_POINT = 9
# AFTER_NUM_POST_DECIMAL_DIGIT = 10
# AFTER_NUM_E = 11
# AFTER_NUM_E_SIGN = 12
# AFTER_NUM_E_DIGIT = 13
# IN_VALUE = 14
# EXPECTING_OBJECT_VALUE = 15


class ParseState(int, Enum):
    START = 0
    SCALAR = 1
    COMMA = 2
    COLON = 3
    ARRAY_START = 4
    ARRAY_END = 5
    OBJECT_START = 6
    OBJECT_KEY = 7
    OBJECT_END = 8
    END = 9


class Container(int, Enum):
    ARRAY = 0
    OBJECT = 1


class ArrayOperation(int, Enum):
    POP = 0
    APPEND = 1


# (Current state, Current container): (New state, container type to pop or append, Whether to pop or append)
valid_new_states: dict[
    tuple[ParseState, Container | None],
    set[ParseState],
] = {
    (ParseState.START, None): {ParseState.SCALAR, ParseState.ARRAY_START, ParseState.OBJECT_START},
    (ParseState.SCALAR, None): {ParseState.END},
    (ParseState.ARRAY_START, Container.ARRAY): {
        ParseState.SCALAR,
        ParseState.ARRAY_START,
        ParseState.OBJECT_START,
        ParseState.ARRAY_END,
    },
    (ParseState.SCALAR, Container.ARRAY): {ParseState.ARRAY_END, ParseState.COMMA},
    (ParseState.COMMA, Container.ARRAY): {ParseState.SCALAR, ParseState.ARRAY_START, ParseState.OBJECT_START},
    (ParseState.ARRAY_END, Container.OBJECT): {ParseState.COMMA, ParseState.OBJECT_END},
    (ParseState.OBJECT_START, Container.OBJECT): {ParseState.OBJECT_KEY, ParseState.OBJECT_END},
    (ParseState.OBJECT_END, Container.OBJECT): {ParseState.COMMA, ParseState.OBJECT_END},
    (ParseState.OBJECT_KEY, Container.OBJECT): {ParseState.COLON},
    (ParseState.COLON, Container.OBJECT): {ParseState.SCALAR, ParseState.ARRAY_START, ParseState.OBJECT_START},
    (ParseState.SCALAR, Container.OBJECT): {ParseState.COMMA, ParseState.OBJECT_END},
    (ParseState.COMMA, Container.OBJECT): {ParseState.OBJECT_KEY},
}

# valid_new_states: dict[tuple[ParseState, Container | None], set[ParseState]] = {}
# for k, v in state_transitions.items():
#    valid_new_states[k] = {state[0] for state in v}


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


COMMA = {","}
COLON = {":"}
DOUBLE_QUOTE = {'"'}
WHITESPACE = {" ", "\t", "\r", "\n"}

DECIMAL_POINT = {"."}
NUM_EXPONENT = {"E", "e"}
NUM_SIGN = {"-", "+"}
ONE_THROUGH_NINE = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
DIGIT = {"0"} | ONE_THROUGH_NINE
NUM_CHARS = DIGIT | NUM_SIGN | NUM_EXPONENT | DECIMAL_POINT

VALUE_START_CHARS = DOUBLE_QUOTE | NUM_SIGN | ONE_THROUGH_NINE | NUM_SIGN | {"{", "[", "t", "f", "n"}
OBJECT_END = {"}"}
ARRAY_END = {"]"}


# STATE_TRANSITIONS = {
#    (None, ParseState.EXPECTING_VALUE, ParseState.IN_VALUE): VALUE_START_CHARS,
#    (Container.OBJECT, ParseState.EXPECTING_VALUE, ParseState.IN_VALUE): VALUE_START_CHARS,
#    (ParseState.IN_OBJECT_VALUE, ParseState.AFTER_OBJECT_VALUE),
#    (ParseState.AFTER_OBJECT_VALUE, ParseState.AFTER_OBJECT_VALUE),
# }
#
# valid_chars = {
#    ParseState.EXPECTING_VALUE: VALUE_START_CHARS | WHITESPACE,
#    ParseState.AFTER_OBJECT_VALUE: COMMA | WHITESPACE | OBJECT_END,
#    ParseState.AFTER_ARRAY_VALUE: COMMA | WHITESPACE | ARRAY_END,
#    ParseState.AFTER_OBJECT_START: DOUBLE_QUOTE | WHITESPACE,
#    ParseState.AFTER_OBJECT_KEY: COLON | WHITESPACE,
#    # ParseState.AFTER_KEY_STRING_CHAR: DOUBLE_QUOTE,  # special
#    # ParseState.AFTER_VAL_STRING_CHAR: DOUBLE_QUOTE,  # special
#    # ParseState.AFTER_NUM_SIGN: DIGIT,
#    # ParseState.AFTER_NUM_PRE_DECIMAL_DIGIT: DIGIT | DECIMAL_POINT | NUM_EXPONENT,
#    # ParseState.AFTER_NUM_DECIMAL_POINT: DIGIT,
#    # ParseState.AFTER_NUM_POST_DECIMAL_DIGIT: DIGIT | NUM_EXPONENT,
#    # ParseState.AFTER_NUM_E: NUM_SIGN | DIGIT,
#    # ParseState.AFTER_NUM_E_SIGN: DIGIT,
#    # ParseState.AFTER_NUM_E_DIGIT: DIGIT,  # special
# }
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


class ParseError(Exception): ...


@dataclass
class Token:
    token_type: TokenType
    data: StringRef | None = None


def main():
    buf = '{"23": 233, "asd": "sadasdfsdgdsgadfasdg", "fda": {"sd": [3, 12,3], "asd": 2}}'

    for t in tokenize(buf):
        if isinstance(t.data, StringRef):
            print(f"{t.token_type} - `{buf[t.data.start_index:t.data.start_index+t.data.len]}`")
        else:
            print(t)


def tokenize(buf: str) -> Generator[Token, None, None]:
    container_stack: list[Container] = []
    parse_state: ParseState = ParseState.START
    i: int = 0

    current_state = (parse_state, None)

    def token_or_error(new_state: ParseState, token: Token):
        if new_state in possible_states:
            yield token
        else:
            yield Token(token_type=TokenType.ERROR, data=None)
            raise ParseError(i)

    while i < len(buf):
        char = buf[i]
        possible_states = valid_new_states[current_state]

        match char:
            case "{":
                new_state = ParseState.OBJECT_START
                yield from token_or_error(new_state, Token(TokenType.OBJECT_START))
                container_stack.append(Container.OBJECT)
            case "}":
                new_state = ParseState.OBJECT_END
                yield from token_or_error(new_state, Token(TokenType.OBJECT_END))
                _ = container_stack.pop()
            case "[":
                new_state = ParseState.ARRAY_START
                yield from token_or_error(new_state, Token(TokenType.ARRAY_START))
                container_stack.append(Container.ARRAY)
            case "]":
                new_state = ParseState.ARRAY_END
                yield from token_or_error(new_state, Token(TokenType.ARRAY_END))
                _ = container_stack.pop()
            case ":":
                new_state = ParseState.COLON
                if new_state not in possible_states:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)
            case ",":
                new_state = ParseState.COMMA
                if new_state not in possible_states:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)
            case '"':
                if ParseState.SCALAR in possible_states:
                    new_state = ParseState.SCALAR
                elif ParseState.OBJECT_KEY in possible_states:
                    new_state = ParseState.OBJECT_KEY
                else:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                end_quote_index = parse_string(buf, i)
                if end_quote_index == -1:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                yield Token(TokenType.STRING, data=StringRef(start_index=i + 1, len=end_quote_index - i - 1))
                i = end_quote_index

            case "t" | "n":
                if ParseState.SCALAR not in possible_states:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                if len(buf) < i + 4:
                    yield Token(token_type=TokenType.ERROR)
                    raise ParseError(i)

                val = buf[i : i + 4]
                if val == "true":
                    yield Token(token_type=TokenType.TRUE)
                elif val == "null":
                    yield Token(token_type=TokenType.NULL)
                else:
                    yield Token(token_type=TokenType.ERROR)
                    raise ParseError(i)

                new_state = ParseState.SCALAR
                i += 4
            case "f":
                if ParseState.SCALAR not in possible_states:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                if len(buf) < i + 5:
                    yield Token(token_type=TokenType.ERROR)
                    raise ParseError(i)

                val = buf[i : i + 5]
                if val == "false":
                    yield Token(token_type=TokenType.FALSE, data=None)
                else:
                    yield Token(token_type=TokenType.ERROR, data=None)
                    raise ParseError(i)

                new_state = ParseState.SCALAR
                i += 5
            case "-" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                if ParseState.SCALAR not in possible_states:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                end_num_index = parse_number(buf, i)
                yield Token(token_type=TokenType.NUMBER, data=StringRef(start_index=i, len=end_num_index - i))

                new_state = ParseState.SCALAR
                i = end_num_index - 1
            case " " | "\n" | "\t" | "\r":
                new_state = current_state[0]
            case _:
                yield Token(token_type=TokenType.ERROR, data=None)
                raise ParseError(i)

        current_state = (new_state, container_stack[-1] if len(container_stack) > 0 else None)

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


def parse_string(buf: str, start: int) -> int:
    i = start
    while i < len(buf):
        char = buf[i]

        if i == start:
            assert buf[i] == '"'
            i += 1
            continue

        if char == '"':
            if buf[i - 1] == "\\":
                i += 1
                continue
            else:
                return i
        i += 1

    return -1


def parse_number(buf: str, start: int) -> int:
    # TODO: actually make a good inplementation of this
    i = start
    while i < len(buf):
        char = buf[i]

        if char not in NUM_CHARS:
            return i

        i += 1

    return i


if __name__ == "__main__":
    main()
