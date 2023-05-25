#!/bin/bash

ARCH=$(uname -m | sed -e s/i.86/x86/ -e s/x86_64/x86_64/ \
				  -e s/sun4u/sparc64/ \
				  -e s/arm.*/arm/ -e s/sa110/arm/ \
				  -e s/s390x/s390/ -e s/parisc64/parisc/ \
				  -e s/ppc.*/powerpc/ -e s/mips.*/mips/ \
				  -e s/sh[234].*/sh/ -e s/aarch64.*/arm64/)

VERSION=""
CURPWD=$(pwd)
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

# Check availability of commands
WGET=true
command -v wget > /dev/null 2>&1 || {
    WGET=false
}

INSTALL=false
command -v rustup >/dev/null 2>&1 || {
    if $WGET; then
        echo "I will install rustup after 5 seconds..."
        INSTALL=true
    else
        echo "No rustup and wget found. Abort!"; exit 1
    fi
}

if $INSTALL; then
    wget -O- http://sh.rustup.rs | sh - -y --profile minimal || (echo "Error occured. Abort."; exit 1)
fi

# Set toolchains default profile
rustup set profile default

# Adding components
install_components() {
    rustup component add rust-std llvm-tools-preview cargo
    cargo install cargo-xbuild bootimage
}

if [ $ARCH = "x86_64" ]; then
    rustup toolchain install nightly$VERSION-x86_64-unknown-linux-gnu
    rustup default nightly$VERSION-x86_64-unknown-linux-gnu
    install_components
    cd $DIR
    cargo build --target configs/x86_64-kernel.json
    cargo bootimage    
fi
