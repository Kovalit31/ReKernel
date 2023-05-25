fn main() {
    println!("cargo:rustc-link-arg=-Wl,--allow-multiple-definition");
    // println!("cargo:rustc-link-arg=-Wl,--nostartfiles")
}