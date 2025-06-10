#pragma once
#include "root.unity.h"

typedef struct {
	char *buffer;
	unsigned int len;
} String;

internal void print(String s) { write_(1, (void *)s.buffer, s.len); }

internal String newString(char *s);
internal void print(String s);

internal uintptr strlen(char const *str) {
	char const *p;
	for (p = str; *p; ++p)
		;
	return p - str;
}

internal String newString(char *s) {
	String str = {.buffer = s, .len = strlen(s)};
	return str;
}
