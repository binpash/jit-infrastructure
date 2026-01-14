import argparse
import os


class BaseParser(argparse.ArgumentParser):
    """
    Base class for all Argument Parsers used by PaSh. It has two configurable flags
    by default: debug and log_file.

    Other flags are available by classes which inherit BaseParser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            "-t",
            "--time",  # FIXME: --time
            help="(obsolete, time is always logged now) output the time it took for every step",
            action="store_true",
        )
        self.add_argument(
            "-d",
            "--debug",
            type=int,
            help="configure debug level; defaults to 0",
            default=0,
        )
        self.add_argument(
            "--log_file",
            help="configure where to write the log; defaults to stderr.",
            default="",
        )

    def add_pash_args(self):
        self.add_argument(
            "--version",
            action="version",
            version="%(prog)s {version}".format(
                version="0.12.2"
            ),  # What does this version mean?
        )



class RunnerParser(BaseParser):
    """
    Parser for the PaSh Runner in compiler/pash.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_pash_args()

        self.add_argument(
            "input",
            nargs="*",
            help="the script to be compiled and executed (followed by any command-line arguments",
        )
        self.add_argument(
            "--preprocess_only",
            help="only preprocess the input script and not execute it",
            action="store_true",
        )
        self.add_argument(
            "--output_preprocessed",
            help=" output the preprocessed script",
            action="store_true",
        )
        self.add_argument(
            "-c",
            "--command",
            help="Evaluate the following as a script, rather than a file",
            default=None,
        )
        ## This is not the correct way to parse these, because more than one option can be given together, e.g., -ae
        self.add_argument(
            "-a",
            help="Enabling the `allexport` shell option",
            action="store_true",
            default=False,
        )
        self.add_argument(
            "+a",
            help="Disabling the `allexport` shell option",
            action="store_false",
            default=False,
        )
        ## These two are here for compatibility with respect to bash
        self.add_argument(
            "-v",
            help="(experimental) prints shell input lines as they are read",
            action="store_true",
        )
        self.add_argument(
            "-x",
            help="(experimental) prints commands and their arguments as they execute",
            action="store_true",
        )
        self.add_argument(
            "--bash",
            help="(experimental) interpret the input as a bash script file",
            action="store_true",
        )

        self.set_defaults(preprocess_mode="pash")
