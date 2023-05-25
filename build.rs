fn main() {
    println!("cargo:rustc-link-arg='-nostartfiles,-Wl,--allow-multiple-definition'")
}