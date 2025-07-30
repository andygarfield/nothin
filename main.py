from dataclasses import dataclass
from enum import Enum

number_chars = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "E", "e", "-", "+"}


@dataclass
class StringRef:
    start_index: int
    len: int


class ParseState(int, Enum):
    EXPECTING_VALUE = 0
    BEFORE_OBJECT_KEY = 1
    AFTER_OBJECT_KEY = 2
    AFTER_OBJECT_VALUE = 3
    AFTER_ARRAY_VALUE = 4
    AFTER_NUM_SIGN = 5
    AFTER_NUM_DECIMAL_POINT = 6
    AFTER_NUM_E = 7
    EOF = 8


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
    COLON = 10
    COMMA = 11
    WHITESPACE = 12
    DIGITS = 13
    PLUS = 14
    MINUS = 15
    DECIMAL_POINT = 16
    END = 17


class Container(int, Enum):
    ARRAY = 0
    OBJECT = 1


valid_tokens = {
    ParseState.EXPECTING_VALUE: {
        TokenType.STRING,
        TokenType.NUMBER,
        TokenType.TRUE,
        TokenType.FALSE,
        TokenType.NULL,
        TokenType.OBJECT_START,
        TokenType.ARRAY_START,
        TokenType.WHITESPACE,
        TokenType.PLUS,
        TokenType.MINUS,
    },
    ParseState.BEFORE_OBJECT_KEY: {
        TokenType.STRING,
        TokenType.WHITESPACE,
        TokenType.OBJECT_END,
    },
    ParseState.AFTER_OBJECT_KEY: {
        TokenType.COLON,
        TokenType.WHITESPACE,
    },
    ParseState.AFTER_OBJECT_VALUE: {
        TokenType.COMMA,
        TokenType.WHITESPACE,
        TokenType.OBJECT_END,
    },
    ParseState.AFTER_ARRAY_VALUE: {
        TokenType.COMMA,
        TokenType.WHITESPACE,
        TokenType.ARRAY_END,
    },
    ParseState.AFTER_NUM_SIGN: {
        TokenType.DIGITS,
    },
    ParseState.AFTER_NUM_DECIMAL_POINT: {
        TokenType.DIGITS,
    },
    ParseState.AFTER_NUM_E: {
        TokenType.DIGITS,
        TokenType.MINUS,
        TokenType.PLUS,
    },
}


@dataclass
class Token:
    token_type: TokenType
    data: StringRef | None


def main():
    # with open(sys.argv[1]) as f:
    #    for token in tokenize(f.read()):
    #        print(token)

    for token in tokenize('{"foo": null, "f": false, "dasd": 123.332}'):
        print(token)


def tokenize(buf: str):
    skip_to = -1
    string_start = -1
    number_start = -1
    prev_char = ""
    container_stack: list[Container] = []
    parse_state: ParseState = ParseState.EXPECTING_VALUE

    def find_container_parse_state():
        global parse_state
        match container_stack[-1]:
            case Container.ARRAY:
                parse_state = ParseState.AFTER_ARRAY_VALUE
            case Container.OBJECT:
                parse_state = ParseState.AFTER_OBJECT_VALUE

    # TODO: error if this is True and we've hit EOF
    for i, char in enumerate(buf):
        if skip_to > i:
            continue

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

        match char:
            case "{":
                assert TokenType.OBJECT_START in valid_tokens[parse_state]
                yield Token(token_type=TokenType.OBJECT_START, data=None)
                parse_state = ParseState.BEFORE_OBJECT_KEY
                container_stack.append(Container.OBJECT)
            case "}":
                assert TokenType.OBJECT_END in valid_tokens[parse_state]
                yield Token(token_type=TokenType.OBJECT_END, data=None)
                _ = container_stack.pop()
                if len(container_stack) == 0:
                    # TODO: may not need this token
                    yield Token(TokenType.END, data=None)
                    parse_state = ParseState.EOF
                find_container_parse_state()
            case '"':
                assert TokenType.STRING in valid_tokens[parse_state]
                if string_start >= 0 and prev_char != "\\":
                    yield Token(
                        token_type=TokenType.STRING,
                        data=StringRef(start_index=string_start, len=i - string_start),
                    )
                    parse_state = ParseState.BEFORE_OBJECT_KEY
                    string_start = -1
                else:
                    skip_to = i + 2
                    string_start = i + 1
            case "t" | "n":
                assert TokenType.STRING in valid_tokens[parse_state]
                if len(buf) < i + 4:
                    yield Token(token_type=TokenType.ERROR, data=None)
                val = buf[i : i + 4]
                match val:
                    case "true":
                        skip_to = i + 4
                        yield Token(token_type=TokenType.TRUE, data=None)
                    case "null":
                        skip_to = i + 4
                        yield Token(token_type=TokenType.NULL, data=None)
                    case _:
                        yield Token(token_type=TokenType.ERROR, data=StringRef(start_index=i, len=0))

            case "f":
                if len(buf) < i + 5:
                    yield Token(token_type=TokenType.ERROR, data=None)
                val = buf[i : i + 5]
                if val == "false":
                    skip_to = i + 5
                    yield Token(token_type=TokenType.FALSE, data=None)
                else:
                    yield Token(token_type=TokenType.ERROR, data=None)
            case ":":
                yield Token(token_type=TokenType.COLON, data=None)
                parse_state = ParseState.EXPECTING_VALUE
            case ",":
                yield Token(token_type=TokenType.COMMA, data=None)
            case "[":
                yield Token(token_type=TokenType.ARRAY_START, data=None)
                parse_state = ParseState.EXPECTING_VALUE
                container_stack.append(Container.ARRAY)
            case "]":
                yield Token(token_type=TokenType.ARRAY_END, data=None)
                if len(container_stack) == 0:
                    # TODO: may not need this token
                    yield Token(TokenType.END, data=None)
                    parse_state = ParseState.EOF
                find_container_parse_state()
                _ = container_stack.pop()
            case _:
                pass
        prev_char = char


if __name__ == "__main__":
    main()
