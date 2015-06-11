"""
Convert a Python-template based file using the environment
"""

__author__ = 'Aron Matskin'


import string
import sys
import os


def parse_args():
    """Parse command-line parameters"""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('template_file',
                        metavar='TEMPLATE_FILE',
                        help="template file to process")

    return parser.parse_args()


if __name__ == '__main__':
    _args = parse_args()

    with open(_args.template_file, 'r') as file:
        sys.stdout.write(string.Template(file.read()).substitute(os.environ))
