ARCH ?= $(shell uname -m | sed -e s/i.86/x86/ -e s/x86_64/x86/ \
				  -e s/sun4u/sparc64/ \
				  -e s/arm.*/arm/ -e s/sa110/arm/ \
				  -e s/s390x/s390/ -e s/parisc64/parisc/ \
				  -e s/ppc.*/powerpc/ -e s/mips.*/mips/ \
				  -e s/sh[234].*/sh/ -e s/aarch64.*/arm64/ )
DIR := $(strip $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))
REQUIRED_BINS := rustup, cargo

check:
	$(foreach bin,$(REQUIRED_BINS),\
		$(if $(shell command -v $(bin) 2> /dev/null),$(info configure: Found `$(bin)`),$(error Error: please install `$(bin)`)))

install_deps:
	rustup component add rust-std llvm-tools-preview
	cargo install cargo-xbuild
	cargo install bootloader

build:
	cd $(DIR)
	ifeq ($(ARCH), x86_64)
		cargo xbuild --target $(DIR)/configs/x86_64-kernel.json
	endif
	cargo bootloader

all: check, install_deps, build
