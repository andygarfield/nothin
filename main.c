#pragma once
#include "root.unity.h"
#include <stdio.h>

int main(int argc, char **argv) {
	// 2^25 pages or 128GiB (the OS shouldn't allocate this entire chunk for real
	// unless we actually access it)
	// u64 pages = 33554432;
	// char *mem = alloc_pages(pages);
	// u64 pages = 1;

	// one less page than the signed 32-bit max
	// u64 pages = 524287;
	//  RefStringArray a = {.p = allocPages(pages), .len = 0};

	// Hard-limit of 500MiB per JSON object
	u64 fileBufferPages = 128000;
	char *fileBuffer = allocPages(fileBufferPages);
	// TODO: use this back later to check if we're out of range
	// char *maxFillBufferAddress = fileBuffer + (fileBufferPages * PAGE_SIZE) - 1;
	char *startPos = fileBuffer;

	u64 fd = open_(argv[1], O_RDONLY, 0);

	u64 numBytesRead;
	// s64 stringStart = -1;
	for (u64 i = 0; i < fileBufferPages; i++) {
		numBytesRead = read_(fd, fileBuffer, PAGE_SIZE);
		if (!numBytesRead) {
			break;
		}

		fileBuffer += numBytesRead;
	}
	String wholeBufferStr = {.buffer = startPos, .len = fileBuffer - startPos};
	// print(wholeBufferStr);
	JsonStringReader r = newJsonStringReader(wholeBufferStr);
	JsonToken t;
	while (1) {
		t = jsonNext(&r);
		switch (t.tokenType) {
		case TOKEN_TYPE_OBJECT_START:
			printChar("object start\n");
            break;
		case TOKEN_TYPE_OBJECT_END:
			printChar("object end\n");
            break;
		case TOKEN_TYPE_ARRAY_START:
			printChar("array start\n");
            break;
		case TOKEN_TYPE_ARRAY_END:
			printChar("array end\n");
            break;
		case TOKEN_TYPE_STRING:
			print(newString("string\n"));
            printRefString(wholeBufferStr, t.data);
	        print(newString("\n"));
            break;
		case TOKEN_TYPE_TRUE:
			printChar("true\n");
            break;
		case TOKEN_TYPE_FALSE:
			printChar("false\n");
            break;
		case TOKEN_TYPE_NULL:
			printChar("null\n");
            break;
		case TOKEN_TYPE_EOF:
			printChar("eof\n");
			goto afterLoop;
		case TOKEN_TYPE_ERROR:
			printChar("error\n");
			goto afterLoop;
		default:
			goto afterLoop;
		}
	}
afterLoop:
	printChar("end\n");
	print(newString(""));
	return 0;
}
