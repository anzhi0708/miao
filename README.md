# Miao

![Lines of code](https://img.shields.io/tokei/lines/github/anzhi0708/miao)  ![PyPI](https://img.shields.io/pypi/v/miao-make)  ![PyPI - License](https://img.shields.io/pypi/l/miao-make)  ![PyPI - Format](https://img.shields.io/pypi/format/miao-make)

<br>

<div align="center">

  <img src="miao.png" alt="Miao Logo" width="13%"/>

  <p>A Python script for generating CMake files, with a user-friendly, Cargo-like command line interface. (UNDER CONSTRUCTION)</p>

</div>

<br>

---

TODO:

<br>

- ☑ miao help
- ☑ miao new
  - ☑ miao new --language --standard 
  - ☐ miao new --lib
- ☑ miao build
- ☑ miao run
- ☑ miao clean
- ☐ miao init
- ☑ miao add
  - ☑ miao add --include_dir
- ☐ miao remove
- ☐ miao config

<br>

## Installation

```bash

# The PyPI version may be outdated.
# Please consider using `git clone` to 
# obtain the latest version.

pip3 install miao-make
```

## Usage

- `miao help`

```bash
$ miao help
Miao Version 20230624

   add                       Add dependencies.
                             Use `--include_dir` to add header file directories.
   build                     Compile the current project.
   clean                     Remove the build directory.
   config                    ...
   find_project_root
   help                      Print help.
   init
   new                       Create a new project.
   remove                    ...
   run                       Run the current project.
   version                   Print version info and exit.

```


- `miao new` - Creating a new project

```bash

# Create a new project

$ miao new my_project
 Created   my_project
 Added     CMakelists.txt
 (debug)   ```set(CMAKE_CXX_STANDARD 17)
        file(GLOB_RECURSE SOURCES "src/*.cpp")```
 Created   src/ directory
 Added     main.cpp
 Created   build/ directory


# The `--language` and `--standard` flags

$ miao new 'hello world' --language cpp --standard 20
 Created   hello_world
 Added     CMakelists.txt
 (debug)   ```set(CMAKE_CXX_STANDARD 20)
        file(GLOB_RECURSE SOURCES "src/*.cpp")```
 Created   src/ directory
 Added     main.cpp
 Created   build/ directory
```


- `miao add` - Adding libraries

```bash

# `cd` into it and add library & header file directory

$ cd my_project/

# adding libs and `include_dir`s

$ miao add ncurses --include_dir=(brew --prefix ncurses)/include
Adding header directories ['/usr/local/opt/ncurses/include']
Adding ('ncurses',) for `my_project`
```


- Run

```bash
$ miao run
 root:     /Users/4nji/dev/python/miao/src/my_project
 pwd:      /Users/4nji/dev/python/miao/src/my_project
 Entering  /Users/4nji/dev/python/miao/src/my_project/build
-- The C compiler identification is AppleClang 13.0.0.13000029
-- The CXX compiler identification is AppleClang 13.0.0.13000029
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done (1.5s)
-- Generating done (0.0s)
-- Build files have been written to: /Users/4nji/dev/python/miao/src/my_project/build
 Success   Successfully executed the command: ['cmake', '/Users/4nji/dev/python/miao/src/my_project']
[ 50%] Building CXX object CMakeFiles/my_project.exe.dir/src/main.cpp.o
[100%] Linking CXX executable my_project.exe
[100%] Built target my_project.exe
 Success   Successfully executed the command: ['make']

===========================2023-06-24 19:56:20.228994==========================

Running /Users/4nji/dev/python/miao/src/my_project/build/my_project.exe

===============================================================================
Hello, world!

Process finished with exit code 0

```


- Cleaning up

```
$ miao clean
Removing /Users/Me/dev/python/miao/src/hello_world/build

```
