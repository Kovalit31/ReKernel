#!/bin/bash

fatal() {
    echo "[&]" $1
    cd $CURPWD
    exit 1
}

info() {
    echo "[*]" $1
}

warning() {
    echo "[!]" $1
}

check_cmd() {
    if [ -z ${1+x} ]; then 
        warning "\$1 is unsetted! Can't check command"
        return 0
    fi
    (command -v $1 &> /dev/null) || return 1
    return 0
}

install_rust() {
    check_cmd wget || fatal "No wget found. Abort."
    info "I will install rust in 5 seconds"
    sleep 5
    (wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal) || fatal "Error occured. Abort"
    rustup set profile default || warning "Can't set default toolchain profile!"
}

# Adding components
install_components() {
    rustup component add rust-std llvm-tools-preview cargo || fatal "Components installation failed! Abort"
}

main_kernel () {
    mkdir .cargo || fatal "Can't create cargo data folder! Abort"
    cp configs/$ARCH.$TARGET.toml .cargo/config.toml || fatal "Arch or target (main config) not detected. Abort"
    cp configs/Cargo_$ARCH.$TARGET.toml Cargo.toml || fatal "Arch or target (cargo) not detected. Abort"
    check_cmd rustup || install_rust

    if [ $ARCH = "x86_64" ]; then
        rustup toolchain install nightly$VERSION-x86_64-unknown-linux-gnu || fatal "Toolchain not installable. Abort"
        rustup default nightly$VERSION-x86_64-unknown-linux-gnu || warning "Can't set default toolchain!"
    fi

    install_components
    cargo build || fatal "Can't build system! Abort."
    exit 0
}

main_boot() {
    mkdir kernel || fatal "Can't create kernel folder"
    mv src kernel || fatal "Can't move src to kernel!"
    mkdir kernel/.cargo || fatal "Can't create cargo data folder for kernel. Abort"
    cp configs/$ARCH.default.toml kernel/.cargo/config.toml || fatal "Arch not detected (main config@kernel). Abort"
    cp configs/Cargo_$ARCH.default.toml kernel/Cargo.toml || fatal "Arch not detected (cargo@kernel). Abort"
    mv build.rs kernel || fatal "Can't move build.rs of kernel! Abort"
    mv boot_target src || fatal "Can't create new src folder! Abort"
    mv src/build.rs . || fatal "Can't move build.rs of bootloader! Abort"
    main_kernel
}

if [ -z ${ARCH+x} ]; then 
    ARCH=$(uname -m | sed -e s/i.86/x86/ -e s/x86_64/x86_64/ \
				  -e s/sun4u/sparc64/ \
				  -e s/arm.*/arm/ -e s/sa110/arm/ \
				  -e s/s390x/s390/ -e s/parisc64/parisc/ \
				  -e s/ppc.*/powerpc/ -e s/mips.*/mips/ \
				  -e s/sh[234].*/sh/ -e s/aarch64.*/arm64/)
fi

if [ -z ${VERSION+x} ]; then 
    VERSION=""
fi

CURPWD=$(pwd)

## STACKOVERFLOWитт
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
## END

TARGET=default

cd $DIR

if [ ! -z ${1+x} ]; then
    if [ $1 = "boot" ]; then
        main_boot
    fi
fi

main_kernel