.POSIX:
CC     = clang
CFLAGS = -std=c99 -O0 -Wall -Werror -nostdlib -lSystem -fdelete-null-pointer-checks

SRC=$(wildcard *.c)

schema_infer: hello.S $(SRC)
	$(CC) $(CFLAGS) -o $@ hello.S root.c

#hello:  hello.S hello.c
#	gcc -s -Os -fdata-sections -Wl,-gc-sections -nostdlib -Wl,--gc-sections \
#	-fno-unwind-tables -fno-asynchronous-unwind-tables -fno-builtin -std=c89 \
#	-pedantic -Wall -Werror -Wa,--noexecstack -fno-stack-protector \
#	-fdelete-null-pointer-checks -static -Wl,-nmagic \
#	-o hello $^
#hello_debug: hello.S hello.c
#	gcc -O0 -nostdlib -ggdb -z noexecstack -o hello_debug $^
