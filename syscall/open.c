#pragma once
#include "../root.unity.h"

#ifdef __APPLE__
#define SYSCALL_OPEN 0x2000005
#endif
#ifdef __linux__
#define SYSCALL_OPEN 0x2
#endif

#define O_RDONLY 0x0000 /* open for reading only */
#define O_WRONLY 0x0001 /* open for writing only */
#define O_RDWR 0x0002	/* open for reading and writing */

internal u64 open_(const char *filename, i64 flags, i64 mode) {
	return (u64)syscall5((void *)filename, INT2VOIDP(flags), INT2VOIDP(mode), 0, 0, (void *)SYSCALL_OPEN);
}
