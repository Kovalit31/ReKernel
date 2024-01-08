use core::arch::asm;

pub fn cpu_relax() -> () {
    unsafe {
        asm!("rep; nop");
    }
}
