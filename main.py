from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum


@dataclass
class StringRef:
    start_index: int
    len: int


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
    (ParseState.ARRAY_END, Container.ARRAY): {ParseState.COMMA, ParseState.ARRAY_END},
    (ParseState.ARRAY_END, None): {ParseState.END},
    (ParseState.OBJECT_START, Container.OBJECT): {ParseState.OBJECT_KEY, ParseState.OBJECT_END},
    (ParseState.OBJECT_END, Container.OBJECT): {ParseState.COMMA, ParseState.OBJECT_END},
    (ParseState.OBJECT_END, Container.ARRAY): {ParseState.COMMA, ParseState.ARRAY_END},
    (ParseState.OBJECT_END, None): {ParseState.END},
    (ParseState.OBJECT_KEY, Container.OBJECT): {ParseState.COLON},
    (ParseState.COLON, Container.OBJECT): {ParseState.SCALAR, ParseState.ARRAY_START, ParseState.OBJECT_START},
    (ParseState.SCALAR, Container.OBJECT): {ParseState.COMMA, ParseState.OBJECT_END},
    (ParseState.COMMA, Container.OBJECT): {ParseState.OBJECT_KEY},
}


class TokenType(int, Enum):
    ERROR = 0
    STRING = 1
    NUMBER = 2
    TRUE = 3
    FALSE = 4
    NULL = 5
    OBJECT_START = 6
    OBJECT_END = 7
    OBJECT_KEY = 8
    ARRAY_START = 9
    ARRAY_END = 10


DECIMAL_POINT = {"."}
NUM_EXPONENT = {"E", "e"}
NUM_SIGN = {"-", "+"}
ONE_THROUGH_NINE = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
DIGIT = {"0"} | ONE_THROUGH_NINE
NUM_CHARS = DIGIT | NUM_SIGN | NUM_EXPONENT | DECIMAL_POINT
NON_DIGIT_NUM_CHAR = NUM_CHARS - DIGIT


class ParseError(Exception): ...


@dataclass
class Token:
    token_type: TokenType
    data: StringRef | None = None


def main():
    with open("/Users/andy/Downloads/twitter.json") as f:
        buf = f.read()
    # for buf in ["]:
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
                    breakpoint()
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                end_quote_index = parse_string(buf, i)
                if end_quote_index == -1:
                    yield Token(TokenType.ERROR)
                    raise ParseError(i)

                yield Token(
                    TokenType.STRING if new_state == ParseState.SCALAR else TokenType.OBJECT_KEY,
                    data=StringRef(start_index=i + 1, len=end_quote_index - i - 1),
                )
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
                i += 3
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
                i += 4
            case "-" | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
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
        raise ParseError(i)


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
    # TODO: Maybe actually validate the number. Progress in the commented out code below.
    i = start
    while i < len(buf):
        char = buf[i]

        if char not in NUM_CHARS:
            return i

        i += 1

    return i


# class NumberState(int, Enum):
#    NEGATIVE_SIGN = 0
#    WHOLE_NUMBER = 1
#    AFTER_DECIMAL_NUMBER = 2
#    EXPONENT = 3
#    EXPONENT_SIGN = 4
#    POWER = 5
#
#
# def parse_number(buf: str, start: int) -> int:
#    state = 0
#    i = start
#
#    negative = False
#    breakpoint()
#    while i < len(buf):
#        char = buf[i]
#        if i == 0:
#            state += 1
#            if char == "-":
#                negative = True
#                i += 1
#                continue
#            else:
#                if char not in DIGIT:
#                    return -1
#        elif (i == 1 and not negative) or (i == 2 and negative):
#            if buf[i - 1] == "0":
#                return -1
#
#        if char == ".":
#            if NumberState(state) == NumberState.WHOLE_NUMBER:
#                state += 1
#            else:
#                return -1
#
#        if char in NON_DIGIT_NUM_CHAR and buf[i - 1] == ".":
#            return -1
#
#        if char not in NUM_CHARS:
#            if buf[i - 1] in NON_DIGIT_NUM_CHAR:
#                return -1
#            return i
#
#        i += 1
#
#    if buf[i - 1] in NON_DIGIT_NUM_CHAR:
#        return -1
#    return i


if __name__ == "__main__":
    main()
