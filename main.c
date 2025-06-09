#pragma once
#include "root.unity.h"

typedef struct {
	char *buffer;
	unsigned int len;
} String;

internal uintptr get_page_size(void) {
	char *p;
	uintptr u;
	for (uintptr n = 1; n; n *= 2) {
		p = mmap(0, n * 2, PROT_NONE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
		if (p == MAP_FAILED) {
			return -1;
		}
		u = munmap((uintptr)p + n, n);
		if (!u) {
			return n;
		}
	}
	return -1;
}

internal intptr write_(int fd, void const *data, uintptr nbytes) {
	return (intptr)syscall5((void *)(intptr)fd, (void *)data, (void *)nbytes, 0, 0, (void *)0x2000004);
}

internal String newString(char *s);
internal void print(String s);

internal uintptr strlen(char const *str) {
	char const *p;
	for (p = str; *p; ++p)
		;
	return p - str;
}

internal void print(String s) { write_(1, (void *)s.buffer, s.len); }

internal String newString(char *s) {
	String str = {.buffer = s, .len = strlen(s)};
	return str;
}

int main(void) {
	// find and set the global page size at the beginning
	page_size = get_page_size();

	uintptr pages = 100000;
	print(newString("doing stuff\n"));
	uintptr *mem = alloc_pages(pages);
	for (uintptr i = 0; i < ((page_size * pages) / 8); i++) {
		mem[i] = 0xffffffffffffffff;
	}
	return 0;
}
