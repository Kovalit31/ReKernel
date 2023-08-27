#![allow(dead_code)]
#![allow(non_camel_case_types)]
#![allow(non_upper_case_globals)]
#![allow(non_snake_case)]
#![allow(improper_ctypes)]
#![allow(non_shorthand_field_patterns)]
#![allow(unused_imports)]

pub struct ELF_IDENT_HEADER {
    ELF_FIRST_BYTE: u8,
    ELF_MAGIC_BYTES: [u8; 3], // "ELF"
    ELF_BITNESS: u8,
    ELF_ENDIAN: u8,
    ELF_VERSION: u8, // 0x01
    ELF_OS_ABI: u8, // For linux 0x03
    ELF_ABI_VERSION: u8,
    ELF_PAD: [u8; 7],
}

#[cfg(target_pointer_width="64")]
pub struct ELF_HEADER_64 {
    ELF_TYPE: u16,
    ELF_MACHINE: u16,
    ELF_VERSION: u32, // 0x01
    ELF_ENTRY: u64,
    ELF_PHOFF: u64, // Program Header Offset (usually 0x40)
    ELF_SHOFF: u64, // Section Header Offset
    ELF_FLAGS: u32,
    ELF_EHSIZE: u16, // ELF Header Size (64 bits)
    ELF_PHENTSIZE: u16, // Program Header Entry Size
    ELF_PHNUM: u16, // Number of Program Header Entries
    ELF_SHENTSIZE: u16, // Section Header Entry Size
    ELF_SHNUM: u16, // Number of Section Header Entries
    ELF_SHSTRNDX: u16, // Section Header String Table Index
}

pub struct ELF_HEADER_32 {
    ELF_TYPE: u16,
    ELF_MACHINE: u16,
    ELF_VERSION: u32, // 0x01
    ELF_ENTRY: u32,
    ELF_PHOFF: u32, // Program Header Offset (usually 0x34)
    ELF_SHOFF: u32, // Section Header Offset
    ELF_FLAGS: u32,
    ELF_EHSIZE: u16, // ELF Header Size (52 bits)
    ELF_PHENTSIZE: u16, // Program Header Entry Size
    ELF_PHNUM: u16, // Number of Program Header Entries
    ELF_SHENTSIZE: u16, // Section Header Entry Size
    ELF_SHNUM: u16, // Number of Section Header Entries
    ELF_SHSTRNDX: u16, // Section Header String Table Index
}

#[cfg(target_pointer_width="64")]
pub struct ELF_CODE_HEADER_64 {
    PH_TYPE: u32,
    PH_FLAGS: u32,
    PH_OFFSET: u64,
    PH_VIRT_ADDR: u64,
    PH_PHY_ADDR: u64,
    PH_FILE_SIZE: u64,
    PH_MEM_SIZE: u64,
    PH_ALIGN: u64,
}

pub struct ELF_CODE_HEADER_32 {
    PH_TYPE: u32,
    PH_OFFSET: u32,
    PH_VIRT_ADDR: u32,
    PH_PHY_ADDR: u32,
    PH_FILE_SIZE: u32,
    PH_MEM_SIZE: u32,
    PH_FLAGS: u32,
    PH_ALIGN: u32,
}

#[cfg(target_pointer_width="64")]
pub struct ELF_DATA_HEADER_64 {
    SH_NAME: u32,
    SH_TYPE: u32,
    SH_FLAGS: u64,
    SH_ADDR: u64,
    SH_OFFSET: u64,
    SH_SIZE: u64,
    SH_LINK: u32,
    SH_INFO: u32,
    SH_ADDR_ALIGN: u64,
    SH_ENTSIZE: u64,
}

pub struct ELF_DATA_HEADER_32 {
    SH_NAME: u32,
    SH_TYPE: u32,
    SH_FLAGS: u32,
    SH_ADDR: u32,
    SH_OFFSET: u32,
    SH_SIZE: u32,
    SH_LINK: u32,
    SH_INFO: u32,
    SH_ADDR_ALIGN: u32,
    SH_ENTSIZE: u32,
}

#[cfg(target_pointer_width="64")]
pub const ELF64_SUPPORT: bool = true;
#[cfg(target_pointer_width="32")]
pub const ELF64_SUPPORT: bool = false;

pub const ELF_FIRST_BYTE: u8 = 0x7f;
pub const ELF_MAGIC_BYTES: [u8; 3] = [0x45, 0x4c, 0x46];
pub const ELF_OS_ABI: u8 = 0x03; // Linux
pub const ELF_ABI_VERSION: u8 = 0x01; // Current version :)

// I'll think about this later