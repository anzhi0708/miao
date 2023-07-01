#!/usr/bin/env python3


import os
import re
import sys
import fire
import enum
import jinja2
import inspect
import datetime
import colorama
import subprocess
from typing import Union, Callable


__VERSION__: str = "20230627"


class Miao:
    """
    Project manager for generating CMake file
    """

    sep: str = os.sep
    width: int = 20 if not sys.stdout.isatty() else os.get_terminal_size()[0]

    # Basic CMakeLists.txt file
    basic_template: str = """
cmake_minimum_required(VERSION 3.0)
project({{ project_name }})

# begin_language_options
{{ language_options }}
# end_language_options

# begin_find_library
{{ libraries_to_find }}
# end_find_library

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_executable({{ project_name }}.exe ${SOURCES})

# begin_include_directories
{{ directories_to_include }}
# end_include_directories

# begin_link_libraries
{{ libraries_to_link }}
# end_link_libraries
    """.strip()

    # CXX language options
    template_cpp: str = """
set(CMAKE_CXX_STANDARD {{ lang_standard }})
file(GLOB_RECURSE SOURCES "src/*.cpp")
    """.strip()

    # C language options
    template_c: str = """
set(CMAKE_C_STANDARD {{ lang_standard }})
file(GLOB_RECURSE SOURCES "src/*.c")
    """.strip()

    class _ConsoleOutputType(enum.Enum):
        """
        Apply different colors according to the different output types."
        """

        LOG = enum.auto()
        WARNING = enum.auto()
        ERROR = enum.auto()

    globals()["ERROR"] = _ConsoleOutputType.ERROR
    globals()["WARNING"] = _ConsoleOutputType.WARNING
    globals()["LOG"] = _ConsoleOutputType.LOG

    @property
    def __version_info__(self) -> str:
        version_info: str = __VERSION__
        version_info = f"Miao Version {version_info}"
        return version_info

    def __init__(self, use_color: bool = True):
        """
        If the standard output is TTY,
        then enable color; otherwise, do not enable it.
        """
        self.use_color: bool = use_color

    def version(self):
        """
        Print version info and exit.
        """
        print(self.__version_info__)

    def help(self):
        """
        Print help.
        """
        print(self.__version_info__)
        print()
        methods: list = [
            func
            for func in dir(Miao)
            if callable(getattr(Miao, func)) and not func.startswith("_")
        ]
        method_name_longest: int = max(map(lambda name: len(name), methods))
        for cmd in methods:
            print(
                " ", self._ljust(cmd), end=(lplaceholder := " " * method_name_longest)
            )
            docstring: Union[str, None] = getattr(Miao, cmd).__doc__
            if docstring is not None:
                docstring = docstring.strip().replace(
                    "\n", "\n" + lplaceholder + " " * len(cmd) + " "
                )
            else:
                docstring = ""
            print(docstring)

    @property
    def current_directory(self) -> str:
        return os.getcwd()

    def _print(
        self,
        text: str = "",
        prefix: str = "",
        output_type: _ConsoleOutputType = LOG,
    ):
        if self.use_color:
            if output_type is ERROR:
                prefix = f"{colorama.Fore.RED}{prefix}{colorama.Fore.RESET}"
            elif output_type is WARNING:
                prefix = f"{colorama.Fore.YELLOW}{prefix}{colorama.Fore.RESET}"
            else:
                prefix = f"{colorama.Fore.GREEN}{prefix}{colorama.Fore.RESET}"
        print(f"{prefix} {text}")

    def _find_project_root(self, start, filename: str) -> Union[str, None]:
        current = start
        while True:
            if filename in os.listdir(current):
                return current
            else:
                parent = os.path.dirname(current)
                if parent == current:
                    return None
                else:
                    current = parent

    def find_project_root(self) -> Union[str, None]:
        return self._find_project_root(self.current_directory, "CMakeLists.txt")

    def run(self):
        """
        Run the current project.
        """

        executable: str = self.build()
        time_now: str = str(datetime.datetime.now())
        print()
        print(f"{time_now.center(self.width, '=')}")
        self._print(executable + "\n", "\nRunning")
        print(self.width * "=")
        run_result = subprocess.run([executable])
        if run_result:
            print()
            print(f"Process finished with exit code {run_result.returncode}")

    def _enter_build_dir(self, *, echo: bool = True) -> str:
        """
        If the path does not exist,
        create the directory.
        This function will establish some instance variables so that they can be used in other functions that call it.
        This function also returns the path to the build directory for further use,
        such as in the clean command.
        Since CMake does not come with a built-in clean command,
        the best practice suggested online is to delete the build directory.
        """
        root: Union[str, None] = self.find_project_root()
        if root is None:
            self._print(
                f"could not find `CMakeLists.txt` in `{self.current_directory}` or any parent directory",
                "error",
                ERROR,
            )
            sys.exit(2)
        if echo:
            self._print(root, "Project")
        self.project_name = root.split(self.sep)[-1]
        old_dir: str = self.current_directory
        if echo:
            self._print(old_dir, "PWD")
        if os.path.exists(build_dir := f"{root}/build"):
            if echo:
                self._print(build_dir, ("Entering"))
            os.chdir(build_dir)
        else:
            self._print(build_dir, "Created")
            os.mkdir(build_dir)
            if echo:
                self._print(build_dir, "Entering")
            os.chdir(build_dir)
        self.project_root: str = root
        self.old_dir: str = old_dir
        self.build_dir: str = build_dir
        return build_dir

    def build(self) -> str:
        """
        Compile the current project.
        """

        def error_exit():
            self._print("failed to build", "error", ERROR)

        build_dir: str = self._enter_build_dir()
        src_dir: str = build_dir.replace("/build", "/src")
        run_cmake_result = subprocess.run(["cmake", self.project_root])
        if run_cmake_result:
            if run_cmake_result.returncode == 0:
                self._print(
                    f"Successfully executed the command: {run_cmake_result.args}",
                    "SUCCESS",
                )
            else:
                error_exit()
            run_make_result = subprocess.run(["make"])
            if run_make_result:
                if run_make_result.returncode == 0:
                    self._print(
                        f"Successfully executed the command: {run_make_result.args}",
                        "SUCCESS",
                    )
                    copy_compile_commands_result = subprocess.run(
                        ["cp", "compile_commands.json", src_dir]
                    )
                    if copy_compile_commands_result:
                        if copy_compile_commands_result.returncode == 0:
                            pass
                        else:
                            self._print(
                                "failed to copy `compile_commands.json`",
                                "WARN",
                                WARNING,
                            )
                    else:
                        self._print(
                            "failed to copy `compile_commands.json`",
                            "WARN",
                            WARNING,
                        )
                    pass
                else:
                    error_exit()
            else:
                error_exit()
        else:
            error_exit()

        os.chdir(self.old_dir)
        return f"{self.build_dir}/{self.project_name}.exe"

    def clean(self):
        """
        Remove the build directory.
        """
        build_dir: str = self._enter_build_dir(echo=False)
        self._print(build_dir, "Removing")
        subprocess.run(["rm", "-rf", build_dir])

    def new(self, project_name: str = "", *, language: str = "cpp", standard: str = ""):
        """
        Create a new project.
        """
        project_name = project_name.replace(" ", "_")

        # Check if project name is valid.
        def is_valid_string(s: str) -> bool:
            return bool(re.fullmatch(r"^[\w-]+$", s))

        if (
            project_name == ""
            or project_name[0].isdigit()
            or not is_valid_string(project_name)
        ):
            self._print(
                "invalid project name",
                "error",
                ERROR,
            )
            sys.exit(1)

        language_options: str = ""
        language = language.lower()

        if language not in ("c", "cpp", "cxx", "c++"):
            self._print(
                "invalid language option",
                "error",
                ERROR,
            )
            sys.exit(1)
        else:
            if language in ("cpp", "cxx", "c++"):
                language_options += self.template_cpp
                if standard == "":
                    standard = "17"
            elif language == "c":
                language_options += self.template_c
                if standard == "":
                    standard = "11"
            else:
                sys.exit(1)

            # Embed it into the template string later.
            self.language_options = jinja2.Template(language_options).render(
                lang_standard=standard
            )

        # Check if directory exists
        for file_name in os.listdir():
            if project_name == file_name:
                # Instead of
                # ```raise RuntimeError("Already exists")```,
                # handle it more elegantly
                self._print(
                    f"directory `{project_name}` already exists",
                    "error",
                    ERROR,
                )
                sys.exit(1)

        # Creating project directory
        os.mkdir(project_name)
        self.project_name = project_name
        self._print(self.project_name, self._ljust("Created"))
        project_directory: str = f"{self.current_directory}/{self.project_name}"

        # Creating `CMakeLists.txt`
        with open(f"{project_directory}/CMakeLists.txt", "w") as cmake_list:
            cmake_list.write(
                jinja2.Template(self.basic_template).render(
                    project_name=self.project_name,
                    language_options=self.language_options,
                )
            )
            self._print("CMakelists.txt", self._ljust("Added"))

        # for debugging purpose,
        # so that users will know what was written to
        # the CMake file immediately & directly from
        # their terminal
        __tmp: str = self.language_options.replace("\n", self._ljust("\n    "))
        # self._print(f"```{__tmp}```", self._ljust("(debug)"))

        # Creating `src` directory
        os.mkdir(f"{project_directory}/src")
        self._print("`src/` directory", self._ljust("Created"))

        # Creating minimum source file
        source_code_file_name: str = f"main.{'c' if language == 'c' else 'cpp'}"
        with open(
            f"{project_directory}/src/{source_code_file_name}", "w"
        ) as minimum_source_code:
            MINIMUM_SOURCE_CODE: str = """
#include <stdio.h>


int main(int argc, char** argv) {

    puts("Hello, world!");
    return 0;
}
            """.strip()
            minimum_source_code.write(MINIMUM_SOURCE_CODE)
            self._print(source_code_file_name, self._ljust("Added"))

        # Creating `build` directory
        os.mkdir(f"{project_directory}/build")
        self._print("`build/` directory", self._ljust("Created"))

    def init(self):
        self._todo()

    def config(self):
        """
        ...
        """
        self._todo()

    def add(self, *libs: Union[list[str], None], **kwargs):
        """
        Add dependencies.
        Use `--include_dirs` to add header file directories.
        Use `--lib_dirs` to add library file directories.
        """
        project_root_dir: str = self.find_project_root()
        project_name: str = project_root_dir.split(os.sep)[-1]

        if not libs:
            self._print(f"invalid argument: {libs}", "error", ERROR)
            sys.exit(3)

        # code to embed into CmakeLists.txt
        cmake_code_include_directories: str = ""
        lib_dirs_to_embed: str = ""

        #

        # Header Files Directories
        if "include_dirs" in kwargs:
            header_directories: list[str] = kwargs.get("include_dirs").split(",")
            header_directories = list(filter(lambda e: e != "", header_directories))

            # Check if these ARE actually valid paths
            for directory in header_directories:
                if not os.path.isdir(directory):
                    self._print(f"invalid directory {directory}", "error", ERROR)
                    sys.exit(4)

            cmake_code_include_directories = f"target_include_directories({project_name}.exe PRIVATE {' '.join(header_directories)})"

        # Library Directories
        if "lib_dirs" in kwargs:
            lib_dirs: list[str] = kwargs.get("lib_dirs").split(",")
            lib_dirs = list(filter(lambda e: e != "", lib_dirs))
            for lib_dir in lib_dirs:
                if not os.path.isdir(lib_dir):
                    self._print(f"invalid lib directory {lib_dir}", "error", ERROR)
                    sys.exit(4)

            lib_dirs_to_embed: str = " ".join(lib_dirs)
        else:
            lib_dirs_to_embed = ""

        cmake_lists_txt: str = f"{project_root_dir}/CMakeLists.txt"
        cmake_code_find_library: str = ""
        self._print(f"{libs} for `{project_name}`", "Adding")

        # `find_library(XXX NAMES xxxXx PATHS /x/y/z/)`
        with open(cmake_lists_txt, "r+") as cmake_lists:
            ori_content: str = cmake_lists.read()
            libs_to_link: list = []
            for lib_name in libs:
                cmake_code_find_library += f"find_library({lib_name} NAMES {lib_name}"
                cmake_code_find_library += "{{ LIB_DIRS }}"  # For jinja2 Template
                cmake_code_find_library += ")\n"

                lib_to_link: str = "${" + lib_name + "}"
                libs_to_link.append(lib_to_link)

            cmake_code_link_libraries: str = (
                f"target_link_libraries({project_name}.exe {' '.join(libs_to_link)})"
            )

            cmake_code_find_library = (
                jinja2.Template(cmake_code_find_library).render(
                    LIB_DIRS=f" PATHS {lib_dirs_to_embed}"
                )
                if lib_dirs_to_embed
                else jinja2.Template(cmake_code_find_library).render(LIB_DIRS="")
            )

            # Render
            print(f"""
{cmake_code_find_library}
{cmake_code_include_directories}
{cmake_code_link_libraries}
            """.strip())

            ori_content = (
                ori_content.replace(
                    "# begin_find_library",
                    "# begin_find_library\n" + "{{ libraries_to_find }}",
                )
                .replace(
                    "# begin_link_libraries",
                    "# begin_link_libraries\n" + "{{ libraries_to_link }}",
                )
                .replace(
                    "# begin_include_directories",
                    "# begin_include_directories\n" + "{{ directories_to_include }}",
                )
            )

            updated_cmake: str = jinja2.Template(ori_content).render(
                libraries_to_find=cmake_code_find_library.strip(),
                libraries_to_link=cmake_code_link_libraries,
                directories_to_include=cmake_code_include_directories,
            )

            cmake_lists.seek(0)
            cmake_lists.truncate()
            cmake_lists.write(updated_cmake)

    def remove(self, dep: str):
        """
        ...
        """
        self._todo()

    def _todo(self):
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        caller_name = caller_frame[1][3]
        self._print("comming soon", f"`{caller_name}`", WARNING)
        self._print("not implemented", f"`{caller_name}`", WARNING)

    def _ljust(self, s: str) -> str:
        return " " + s.ljust(9, " ")


def main():
    fire.Fire(Miao(True if sys.stdout.isatty() else False))


if __name__ == "__main__":
    main()
