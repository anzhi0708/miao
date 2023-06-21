# Miao

A Python script for generating CMake files, with a user-friendly, Cargo-like command line interface.

(UNDER CONSTRUCTION❕)

## Usage

- Creating a new project
```bash
miao new hello_world

# Example
./miao new 'hello world' --language c --standard 99
Created   hello_world
Added     CMakelists.txt
(debug)   ```set(CMAKE_C_STANDARD 99)
        file(GLOB_RECURSE SOURCES "src/*.c")```
Created   `src` directory
Created   `build` directory
```
