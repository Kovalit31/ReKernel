fn main() {
    println!("cargo:rustc-link-arg-bins=-nostartfiles");
    // println!("cargo:rustc-link-arg=-Wl,--nostartfiles")
}