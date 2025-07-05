#pragma once
#include "alloc.c"
#include "root.unity.h"
#include <stdio.h>

int main(int argc, char **argv) {
	u64 pages = 1;
	u64 *mem = alloc_pages(pages);
	u64 fd = open_(argv[1], O_RDONLY, 0);

	u64 readBytes;
	do {
		readBytes = read_(fd, mem, PAGE_SIZE);
		String str = {.buffer = (char *)mem, .len = readBytes};
		print(str);
	} while (readBytes);

	return 0;
}
