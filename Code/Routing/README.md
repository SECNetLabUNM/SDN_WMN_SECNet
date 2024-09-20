To compile the Rust code as a Python extension module:
1. [Install the rust compiler](https://www.rust-lang.org/tools/install): `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. Install [maturin](https://github.com/PyO3/maturin): `pip install maturin` or `mamba install maturin`
3. `cd` into the project: `cd Routing`
4. compile/build/add extension module: `maturin develop --release`

The `routing.pyi` file is what provides the type-hints for the LSP writing python. It might be out of date, but the `__doc__` and `__all__` attributes on all python objects should be correctly set when compiling.

You can also use `cargo doc --open` to view the docs for the Rust code directly.