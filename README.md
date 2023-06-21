# Unified OS
The experimental try to write OS kernel on Rust

## Description

It is a try to write Unix-like kernel from zero.

## Building

Run 
```bash
build.py [TARGET]
```
where target is legacy, bios (unstable), efi (unstable) and clean (cleans directories)

## Construction

- configs/ - Config directory
- kernel_patch/ - Patch for efi and bios targets
- boot_target/ - Source for building efi and bios images
- scripts/ - Scripts for building
- build.py - Main build script

## TODO

1. Build system
2. Kernel (Unix-like)
3. Other support
