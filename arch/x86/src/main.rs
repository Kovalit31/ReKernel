#![no_main]
#![no_std]
#![feature(lang_items)]

pub mod boot_data;

use core::panic::PanicInfo;
use self::boot_data::boot::cpu_relax;
use linux_rs::includes::lang::types::ptr_u16;

extern "C" {
    #[no_mangle]
    static mut PROG_END: ptr_u16;
}

static HEAP_START: ptr_u16 = PROG_END;
static HEAP_END: ptr_u16 = PROG_END; /* No heap */

pub const STACK_SIZE: usize = 1024;

fn copy_boot_params() -> () {
    #[repr(C)]
    struct OldCmdline {
        cl_magic: u16,
        cl_offset: u16
    }
    /* TODO old_cmdline */
    /* TODO BUILD_BUG_ON */

}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    loop {}
}


#[panic_handler]
fn _panic(_: &PanicInfo) -> ! {
    loop {}
}

#[lang = "eh_personality"]
extern "C" fn eh_personality() {}
