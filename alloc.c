#pragma once
#include "root.unity.h"
//#include <sys/mman.h>

#define PAGE_SIZE 4096

internal void *alloc_pages(uintptr pages) {
	return mmap(0, PAGE_SIZE * pages, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
}
