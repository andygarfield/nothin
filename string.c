#pragma once
#include "root.unity.h"

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

void appendRefString(RefStringArray *a, RefString item) {
    a->p[a->len] = item;
    a->len++;
}

internal void print(String s) { write_(1, (void *)s.buffer, s.len); }

internal u64 strlen(char const *str) {
	char const *p;
	for (p = str; *p; ++p)
		;
	return p - str;
}

internal String newString(char *s) {
	String str = {.buffer = s, .len = strlen(s)};
	return str;
}
