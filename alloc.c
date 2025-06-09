#pragma once
#include "root.unity.h"

internal uintptr page_size;

internal void *alloc_pages(uintptr pages) {
	return mmap(0, page_size * pages, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
}
