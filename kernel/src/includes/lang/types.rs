// Pointers

#[macro_export]
macro_rules! sync_raw_ptr {
    ($t:ty, $name:ident) => {
        #[repr(C)]
        pub struct $name(pub $t);
        unsafe impl Sync for $name {}
    };
}

sync_raw_ptr!(*const u16, ptr_u16);
sync_raw_ptr!(*const u32, ptr_u32);
