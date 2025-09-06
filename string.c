#pragma once
#include "root.unity.h"

// Max 1GB string
#define MAX_STRING_SIZE (1 << 30)

typedef struct {
	char *buffer;
	u64 len;
} String;

// RefString is a reference to a string in a buffer. The `start` field is the
// first index of the string, and `len` is the string's length.
typedef struct {
	u64 start;
	u64 len;
} RefString;

typedef struct {
	RefString *p;
	u64 len;
} RefStringArray;

// void appendRefString(RefStringArray *a, RefString item) {
//	a->p[a->len] = item;
//	a->len++;
// }

internal void print(String s) { write_(1, (void *)s.buffer, s.len); }

internal void printRefString(String s, RefString r) { write_(1, (void *)((char *)s.buffer + r.start), r.len); }

internal u64 strlen(char const *str) {
    u64 i;
	for (i = 0; i < MAX_STRING_SIZE; ++i) {
		if (str[i] == 0) {
			break;
		}
	}
	return i;
}

internal String newString(char *s) {
	String str = {.buffer = s, .len = strlen(s)};
	return str;
}

internal void printChar(char *s) { print(newString(s)); }
