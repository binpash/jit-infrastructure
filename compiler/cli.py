import argparse
import os


class BaseParser(argparse.ArgumentParser):
    """
    Base class for all Argument Parsers used by PaSh. It has two configurable flags
    by default: debug and log_file.

    Other flags are available by classes which inherit BaseParser
    """

    @staticmethod
    def _get_width():
        cpus = os.cpu_count()
        assert cpus is not None
        return cpus // 8 if cpus >= 16 else 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            "-t",
            "--output_time",  # FIXME: --time
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
            "--local-annotations-dir",
            default=None,
        )
        self.add_argument(
            "--interactive",
            help="Executes the script using an interactive internal shell session (experimental)",
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


class PreprocessorParser(BaseParser):
    """
    Parser for the preprocessor in compiler/preprocessor/preprocessor.py
    Generates two subparsers
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        subparser = self.add_subparsers(help="sub-command help")
        self.add_pash_subparser(subparser)

    @staticmethod
    def add_pash_subparser(subparser):
        parser_pash = subparser.add_parser(
            "pash", help="Preprocess the script so that it can be run with PaSh"
        )
        parser_pash.add_pash_args()
        parser_pash.add_argument("input", help="the script to be preprocessed")
        parser_pash.set_defaults(preprocess_mode="pash")

