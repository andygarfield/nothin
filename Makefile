.POSIX:
CLANG_FLAGS = -std=c99 -O0 -Wall -Werror -nostdlib -lSystem -fdelete-null-pointer-checks
GCC_FLAGS = -s -Os -fdata-sections -Wl,-gc-sections -nostdlib -Wl,--gc-sections \
	-fno-unwind-tables -fno-asynchronous-unwind-tables -fno-builtin -std=c99 \
	-Wall -Werror -Wa,--noexecstack -fno-stack-protector \
	-fdelete-null-pointer-checks -static -Wl,-nmagic
GCC_DB_FLAGS = -O0 -nostdlib -ggdb -z noexecstack
SRC=$(wildcard *.c)

schema_infer_mac: start_mac.S $(SRC)
	clang $(CLANG_FLAGS) -o $@ start_mac.S root.c

schema_infer_linux: start_linux.S $(SRC)
	gcc $(GCC_FLAGS) -o $@ start_linux.S root.c
schema_infer_linux_db: start_linux.S $(SRC)
	gcc $(GCC_DB_FLAGS) -o $@ start_linux.S root.c
