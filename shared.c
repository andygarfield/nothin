typedef unsigned long int uintptr; /* size_t */
typedef long int intptr;       /* ssize_t */

#define internal static
#define INT2VOIDP(i) (void *)(uintptr)(i)
