fn main() {
    println!("cargo:rustc-flags=-Clink-arg=-nostartfiles");
    // println!("cargo:rustc-link-arg=-Wl,--nostartfiles")
}