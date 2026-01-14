all: set-diff
.PHONY: all clean

CFLAGS=-Wall

ifeq ($(DEBUG),1)
  # We want debug mode.
  CFLAGS += -g -DDEBUG -Og -ggdb -Wno-attributes
else
  # We want release mode.
  CFLAGS += -O3 -DNDEBUG
endif

ifeq ($(PERF),1)
  # We want debug mode.
  CFLAGS += -g -ggdb
endif



set-diff: set-diff.c
	gcc ${CFLAGS} set-diff.c -o set-diff

clean:
	rm -f set-diff
