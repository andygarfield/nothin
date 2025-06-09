#pragma once
#include "root.unity.h"
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
#define MAP_ANON 0x1000 /* allocated from memory, swap space */
#define MAP_ANONYMOUS MAP_ANON

/*
 * Error return from mmap()
 */
#define MAP_FAILED ((void *)-1) /* [MF|SHM] mmap failed */

internal void *mmap(void *addr, uintptr len, int prot, int flags, int fd, uintptr offset) {
	return (uintptr *)syscall6(addr, (void *)len, INT2VOIDP(prot), INT2VOIDP(flags), INT2VOIDP(fd), (void *)offset,
				   (void *)0x20000c5);
}

internal uintptr munmap(uintptr addr, uintptr len) {
	return (uintptr)syscall5((void *)addr, (void *)len, 0, 0, 0, (void *)0x2000049);
}
