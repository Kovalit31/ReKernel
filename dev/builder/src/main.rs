use clap::{Parser};

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Arguments {
    action: Option<String>,
    #[clap(short, long)]
    verbose: bool,
    #[clap(short, long)]
    debug: bool,
}

fn main() {
    let args = Arguments::parse();
    println!("{:?}", args);
}
