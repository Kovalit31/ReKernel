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
        return true
    fi
    command -v $1 >/dev/null 2>&1m || return false
    return true
}

install_rust() {
    check_cmd wget || fatal "No wget found. Abort."
    info "I will install rust in 5 seconds"
    sleep 5
    (wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal) || fatal "Error occured. Abort."
    rustup set profile default || warning "Can't set default toolchain profile!"
}

# Adding components
install_components() {
    rustup component add rust-std llvm-tools-preview cargo || fatal "Components installation failed! Abort."
}

main_kernel () {
    cd $DIR
    cp configs/$ARCH.toml config.toml || fatal "Arch not detected. Abort"
    check_cmd rustup || install_rust

    if [ $ARCH = "x86_64" ]; then
        rustup toolchain install nightly$VERSION-x86_64-unknown-linux-gnu || fatal "Toolchain not installable. Abort."
        rustup default nightly$VERSION-x86_64-unknown-linux-gnu || warning "Can't set default toolchain!"
    fi

    install_components
    cargo build || fatal "Can't build system! Abort."
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

## STACKOVERFLOW
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
## END

if [ -n $1 ]; then
    sleep 1
    exit 1
fi

main_kernel