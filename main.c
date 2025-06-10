#pragma once
#include "root.unity.h"
#include <stdio.h>

int main(void) {
	uintptr pages = 1;
	print(newString("doing stuff\n"));
	intptr *mem = alloc_pages(pages);
	for (uintptr i = 0; i < ((PAGE_SIZE * 1) / 8); i++) {
        printf("%lu\n", i);
		mem[i] = 0xffffffffffffffff;
	}
	//for (uintptr i = 0; i < (1100000000); i++) {
	//	sleepytime();
	//}
	return 0;
}
