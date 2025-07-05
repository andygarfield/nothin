#pragma once
#include "root.unity.h"

#define internal static

typedef unsigned long int u64; /* size_t */
typedef long int i64;	       /* ssize_t */

#define UINT2VOIDP(i) (void *)(u64)(i)
#define INT2VOIDP(i) (void *)(i64)(i)

void sleepytime();
