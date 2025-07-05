#pragma once
#include "root.unity.h"

#ifdef __APPLE__
#define SYSCALL_MMAP 0x20000c5
#define SYSCALL_MUNMAP 0x2000049
#define SYSCALL_READ 0x2000003
#define SYSCALL_WRITE 0x2000004

#define MAP_ANON 0x1000 /* allocated from memory, swap space */
#endif
#ifdef __linux__
#define SYSCALL_MMAP 0x9
#define SYSCALL_MUNMAP 0xb
#define SYSCALL_READ 0x0
#define SYSCALL_WRITE 0x1
#define SYSCALL_OPEN 0x2

#define MAP_ANON 0x20 /* Don't use a file.  */
#endif

volatile void *syscall5(void *arg1, void *arg2, void *arg3, void *arg4, void *arg5, void *number);
volatile void *syscall6(void *arg1, void *arg2, void *arg3, void *arg4, void *arg5, void *arg6, void *number);

//internal u64 munmap(u64 addr, u64 len) {
//	return (u64)syscall5((void *)addr, (void *)len, 0, 0, 0, (void *)SYSCALL_MUNMAP);
//}
