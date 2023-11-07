#![no_std]
#![no_main]
#![no_mangle]

use core::panic::PanicInfo;

fn _start() -> ! {
    loop {}
}

#[panic_handler]
#[inline(never)]
fn panic(_: &PanicInfo) -> ! {
    loop {}
}
