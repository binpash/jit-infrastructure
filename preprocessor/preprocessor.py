#!/usr/bin/env python3
"""
Preprocessor - Transforms shell scripts by parsing, transforming ASTs, and unparsing.

This is a standalone executable that takes a shell script as input and outputs
a preprocessed version. It does NOT execute the script.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
import logging

import preprocess_ast_cases
from parse import parse_shell_to_asts, from_ast_objects_to_shell
from util import string_to_argument, make_command
from shasta.json_to_ast import to_ast_node


# Global state for runtime executable path
RUNTIME_EXECUTABLE = None


def log(*args, level=1):
    """Simple logging function"""
    if level >= 1:
        message = " ".join([str(a) for a in args])
        logging.info(f"PaSh: {message}")


def print_time_delta(prefix, start_time, end_time):
    """Print time difference between two datetime objects"""
    time_difference = (end_time - start_time) / timedelta(milliseconds=1)
    log("{} time:".format(prefix), time_difference, " ms")


class TransformationState:
    """Manages state during AST transformation and region replacement"""

    def __init__(self):
        self._node_counter = 0

    def get_next_id(self):
        new_id = self._node_counter
        self._node_counter += 1
        return new_id

    def get_current_id(self):
        return self._node_counter - 1

    def get_number_of_ids(self):
        return self._node_counter

    def replace_df_region(self, asts, disable_parallel_pipelines=False, ast_text=None):
        """Replace a dataflow region with a call to jit.sh runtime"""
        from util import ptempfile

        # Create sequential script file
        sequential_script_file_name = ptempfile()

        # Get shell text from ASTs
        if ast_text is None:
            text_to_output = from_ast_objects_to_shell(asts)
        else:
            text_to_output = ast_text

        # Write script to file
        with open(sequential_script_file_name, "w", encoding="utf-8") as script_file:
            script_file.write(text_to_output)

        # Create AST node that calls jit.sh
        # Generates: __jit_script_to_execute=<file> source jit.sh
        assignments = [
            ["__jit_script_to_execute", string_to_argument(sequential_script_file_name)],
        ]

        arguments = [
            string_to_argument("source"),
            string_to_argument(RUNTIME_EXECUTABLE),
        ]
        runtime_node = make_command(arguments, assignments=assignments)

        return to_ast_node(runtime_node)


def preprocess(input_script_path, bash_mode=False):
    """Preprocess a shell script by parsing, transforming, and unparsing ASTs"""
    ## 1. Execute the POSIX shell parser that returns the AST in JSON
    preprocessing_parsing_start_time = datetime.now()
    ast_objects = parse_shell_to_asts(input_script_path, bash_mode=bash_mode)
    preprocessing_parsing_end_time = datetime.now()
    print_time_delta(
        "Preprocessing -- Parsing",
        preprocessing_parsing_start_time,
        preprocessing_parsing_end_time,
    )

    ## 2. Preprocess ASTs by replacing possible candidates for compilation
    ##    with calls to the PaSh runtime.
    preprocessing_pash_start_time = datetime.now()
    preprocessed_asts = preprocess_asts(ast_objects)
    preprocessing_pash_end_time = datetime.now()
    print_time_delta(
        "Preprocessing -- PaSh",
        preprocessing_pash_start_time,
        preprocessing_pash_end_time,
    )

    ## 3. Translate the new AST back to shell syntax
    preprocessing_unparsing_start_time = datetime.now()
    preprocessed_shell_script = from_ast_objects_to_shell(preprocessed_asts)

    preprocessing_unparsing_end_time = datetime.now()
    print_time_delta(
        "Preprocessing -- Unparsing",
        preprocessing_unparsing_start_time,
        preprocessing_unparsing_end_time,
    )
    return preprocessed_shell_script


def preprocess_asts(ast_objects):
    """Transform AST objects by replacing regions with JIT runtime calls"""
    trans_state = TransformationState()
    preprocessed_asts = preprocess_ast_cases.replace_ast_regions(ast_objects, trans_state)
    return preprocessed_asts


def parse_args():
    """Parse command-line arguments for the preprocessor"""
    parser = argparse.ArgumentParser(
        description="Preprocess shell scripts for PaSh",
        prog="preprocessor.py"
    )

    parser.add_argument(
        "input_script",
        help="Path to the input shell script to preprocess"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the preprocessed output script"
    )

    parser.add_argument(
        "--runtime-executable",
        required=True,
        help="Path to the PaSh runtime executable (jit.sh)"
    )

    parser.add_argument(
        "--bash",
        action="store_true",
        default=False,
        help="Interpret the input as a bash script file (experimental)"
    )

    parser.add_argument(
        "-d",
        "--debug",
        type=int,
        default=0,
        help="Configure debug level; defaults to 0"
    )

    return parser.parse_args()


def main():
    """Main entry point for the preprocessor"""
    global RUNTIME_EXECUTABLE

    args = parse_args()

    # Initialize logging
    logging.basicConfig(format="%(message)s")
    if args.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.debug >= 2:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set runtime executable path
    RUNTIME_EXECUTABLE = args.runtime_executable

    log("Preprocessor starting...")
    log(f"Input script: {args.input_script}")
    log(f"Output file: {args.output}")
    log(f"Runtime executable: {args.runtime_executable}")
    log(f"Bash mode: {args.bash}")
    log("-" * 40)

    # Preprocess the script
    try:
        preprocessed_script = preprocess(args.input_script, bash_mode=args.bash)

        # Write the preprocessed script to output file
        with open(args.output, "wb") as output_file:
            preprocessed_script_bytes = preprocessed_script.encode("utf-8", errors="replace")
            output_file.write(preprocessed_script_bytes)

        log(f"Preprocessed script written to: {args.output}")
        log("-" * 40)
        sys.exit(0)

    except Exception as e:
        log(f"ERROR: Preprocessing failed: {e}", level=0)
        sys.exit(1)


if __name__ == "__main__":
    main()
