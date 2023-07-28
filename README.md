# ReKernel

The experimental try to write OS kernel on Rust

## Description

It is a try to write Unix-like kernel like a linux :-\

## Building

Run:

```bash
build.py [TARGET]
```

where target is legacy, bios (unstable), efi (unstable) and clean (cleans directories). <br\>
See "build.py --help" for more info.

## Construction

- configs/ - Config directory
- kernel/ - Main kernel
- image/ - Source for building efi and bios images
- scripts/ - Scripts for building
- build.py - Main build script

## TODO

1. Kernel (Unix-like)
2. Other support
