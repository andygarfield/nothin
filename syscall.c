#pragma once
#include "root.unity.h"

#ifdef __APPLE__
#define SYSCALL_MMAP 0x20000c5
#define SYSCALL_MUNMAP 0x2000049
#define SYSCALL_WRITE 0x2000004
#define MAP_ANON 0x1000 /* allocated from memory, swap space */
#endif
#ifdef __linux__
#define SYSCALL_MMAP 0x9
#define SYSCALL_MUNMAP 0xb
#define SYSCALL_WRITE 0x1
#define MAP_ANON 0x20 /* Don't use a file.  */
#endif

void *syscall5(void *arg1, void *arg2, void *arg3, void *arg4, void *arg5, void *number);
void *syscall6(void *arg1, void *arg2, void *arg3, void *arg4, void *arg5, void *arg6, void *number);

/*
 * Protections are chosen from these bits, or-ed together
 */
#define PROT_NONE 0x00	/* [MC2] no permissions */
#define PROT_READ 0x01	/* [MC2] pages can be read */
#define PROT_WRITE 0x02 /* [MC2] pages can be written */
#define PROT_EXEC 0x04	/* [MC2] pages can be executed */

/*
 * Flags contain sharing type and options.
 * Sharing types; choose one.
 */
#define MAP_SHARED 0x0001  /* [MF|SHM] share changes */
#define MAP_PRIVATE 0x0002 /* [MF|SHM] changes are private */

/*
 * Other flags
 */
#define MAP_FIXED 0x0010 /* [MF|SHM] interpret addr exactly */

/*
 * Mapping type
 */
#define MAP_FILE 0x0000 /* map from file (default) */
#define MAP_ANONYMOUS MAP_ANON

/*
 * Error return from mmap()
 */
#define MAP_FAILED ((void *)-1) /* [MF|SHM] mmap failed */

internal void *mmap(void *addr, uintptr len, int prot, int flags, int fd, uintptr offset) {
	return (uintptr *)syscall6(addr, (void *)len, INT2VOIDP(prot), INT2VOIDP(flags), INT2VOIDP(fd), (void *)offset,
				   (void *)SYSCALL_MMAP);
}

// internal uintptr munmap(uintptr addr, uintptr len) {
//	return (uintptr)syscall5((void *)addr, (void *)len, 0, 0, 0, (void *)SYSCALL_MUNMAP);
// }

internal intptr write_(int fd, void const *data, uintptr nbytes) {
	return (intptr)syscall5((void *)(intptr)fd, (void *)data, (void *)nbytes, 0, 0, (void *)SYSCALL_WRITE);
}
