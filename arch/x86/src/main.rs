#![no_main]
#![no_std]
#![feature(lang_items)]

use core::arch::asm;
use core::panic::PanicInfo;

extern "C" const PROG_END: u32;

const HEAP_START: *const char = PROG_END;
const HEAP_END: *const char = PROG_END; /* No heap */

pub const STACK_SIZE: usize = 1024;

pub fn cpu_relax() -> () {
    unsafe {
        asm!("rep; nop")
    }
}

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
