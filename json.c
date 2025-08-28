#pragma once
#include "root.unity.h"
#include <stdio.h>

typedef enum {
	PARSE_STATE_START = 0,
	PARSE_STATE_SCALAR,
	PARSE_STATE_COMMA,
	PARSE_STATE_COLON,
	PARSE_STATE_ARRAY_START,
	PARSE_STATE_ARRAY_END,
	PARSE_STATE_OBJECT_START,
	PARSE_STATE_OBJECT_KEY,
	PARSE_STATE_OBJECT_END,
	PARSE_STATE_END,
} JsonParseState;

typedef enum {
	TOKEN_TYPE_ERROR = 0,
	TOKEN_TYPE_STRING,
	TOKEN_TYPE_NUMBER,
	TOKEN_TYPE_TRUE,
	TOKEN_TYPE_FALSE,
	TOKEN_TYPE_NULL,
	TOKEN_TYPE_OBJECT_START,
	TOKEN_TYPE_OBJECT_END,
	TOKEN_TYPE_OBJECT_KEY,
	TOKEN_TYPE_ARRAY_START,
	TOKEN_TYPE_ARRAY_END,
} JsonTokenType;

typedef struct {
	JsonTokenType tokenType;
	RefString data;
} JsonToken;

typedef struct {
	String string;
	u64 stringPos;
	// bunch of bits - 0 means array, 1 means object. Max depth is 127
	char containerStack[16];
	// -1 is initial position
	s8 containerStackPos;
	JsonParseState parseState;
} JsonStringReader;

JsonStringReader newJsonStringReader(String s) {
	JsonStringReader r = {
	    .string = s,
	    .stringPos = 0,
	    .containerStackPos = -1,
	    .parseState = PARSE_STATE_START,
	};
	return r;
}

JsonToken jsonNext(JsonStringReader *r) {
	// TODO: give error details
	if (r->containerStackPos > 127) {
		return (JsonToken){.tokenType = TOKEN_TYPE_ERROR};
	}
	// String str = {.buffer = (char *)fileBuffer, .len = readBytes};
	// u64 startIndex = fileBuffer - startPos;
	// u64 j = startIndex;
	for (; r->stringPos < r->string.len; r->stringPos++) {
		// printf("string pos %llu\n", r->stringPos);
		char c = r->string.buffer[r->stringPos];

		switch (c) {
		case '{':
			r->parseState = PARSE_STATE_OBJECT_START;
            r->stringPos++;
			return (JsonToken){.tokenType = TOKEN_TYPE_OBJECT_START};
		case '}':
			r->parseState = PARSE_STATE_OBJECT_END;
            r->stringPos++;
			return (JsonToken){.tokenType = TOKEN_TYPE_OBJECT_END};
		case '[':
			r->parseState = PARSE_STATE_ARRAY_START;
            r->stringPos++;
			return (JsonToken){.tokenType = TOKEN_TYPE_ARRAY_START};
		case ']':
			r->parseState = PARSE_STATE_ARRAY_END;
            r->stringPos++;
			return (JsonToken){.tokenType = TOKEN_TYPE_ARRAY_END};
		default:
            return (JsonToken){.tokenType = TOKEN_TYPE_ERROR};
		}
		//
		// printf("%c\n", r->string.buffer[r->currentPos]);
		//  switch (*j) {
		//  case '\n':
		//  case '\t':
		//  case '\r':
		//  case ' ':
		//	continue;
		//  case '"':
		//	// TODO: add quote escaping
		//	if (stringStart == -1) {
		//		stringStart = j + 1;
		//	} else {
		//		RefString s = {.start = stringStart, .len = j - stringStart};

		//		appendRefString(&a, s);

		//		stringStart = -1;
		//	}
		// case '{':

		// default:
		//	break;
		// }
	}

	// for (u64 i = 0; i < a.len; i++) {
	//	RefString s = a.p[i];
	//	// printf("start %lu; len %lu\n", s.start, s.len);
	//	String js = {.buffer = startPos + s.start, .len = s.len};
	//	print(js);
	//	print(newString("\n"));
	// }
	return (JsonToken){.tokenType = TOKEN_TYPE_ERROR};
}
