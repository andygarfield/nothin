#pragma once
#include "alloc.c"
#include "root.unity.h"
#include <stdio.h>

#define JSON_NULL 0
#define JSON_TRUE 1
#define JSON_FALSE 2
#define JSON_STRING 3
#define JSON_NUMBER 4
#define JSON_OBJECT 5
#define JSON_ARRAY 6

#define bool u64
#define false 0
#define true 1

typedef struct {
	String name;
	u64 jsonType;

} JsonField;

int main(int argc, char **argv) {
	// 2^25 pages or 128GiB (the OS shouldn't allocate this entire chunk for real
	// unless we actually access it)
	// u64 pages = 33554432;
	// char *mem = alloc_pages(pages);
	// u64 pages = 1;

	// one less page than the signed 32-bit max
	u64 pages = 524287;
	RefStringArray a = {.p = allocPages(pages), .len = 0};

	// Hard-limit of 500MiB per JSON object
	u64 fileBufferPages = 128000;
	char *fileBuffer = allocPages(fileBufferPages);
	// TODO: use this later to check if we're out of range
	// char *maxFillBufferAddress = fileBuffer + (fileBufferPages * PAGE_SIZE) - 1;
	char *startPos = fileBuffer;

	u64 fd = open_(argv[1], O_RDONLY, 0);

	print(newString(""));
	u64 readBytes;
	i64 stringStart = -1;
	for (u64 i = 0; i < fileBufferPages; i++) {
		printf("page num %lu\n", i);
		readBytes = read_(fd, fileBuffer, PAGE_SIZE);
		if (!readBytes) {
			break;
		}

		// String str = {.buffer = (char *)fileBuffer, .len = readBytes};
		u64 startIndex = fileBuffer - startPos;
		u64 j = startIndex;
		for (; j < (startIndex + readBytes); j++) {
			switch (startPos[j]) {
			case '\n':
			case '\t':
			case '\r':
			case ' ':
				continue;
			case '"':
				// TODO: add quote escaping
				if (stringStart == -1) {
					stringStart = j + 1;
				} else {
					RefString s = {.start = stringStart, .len = j - stringStart};

					appendRefString(&a, s);

					stringStart = -1;
				}
			default:
				break;
			}
		}

		fileBuffer += PAGE_SIZE;
	}

	for (u64 i = 0; i < a.len; i++) {
		RefString s = a.p[i];
		printf("start %lu; len %lu\n", s.start, s.len);
		String js = {.buffer = startPos + s.start, .len = s.len};
		print(js);
		printf("\n");
	}

	return 0;
}
