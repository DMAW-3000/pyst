"""
A Smalltalk environment implemented in Python
"""

PYST_DIR = "C:\\Users\\Daniel Wood\\Documents\\pyst"

import sys

def parse_break(argIn):
    """
    Parse a breakpoint definition.
        Class.method
    """
    if argIn is None:
        return None
    argList = argIn[0].split('.')
    if len(argList) != 2:
        print("error: bad breakpoint: ", argIn[0])
        sys.exit(-1)
    return argList


if __name__ == '__main__':

    from argparse import ArgumentParser
    from system import Smalltalk
    
    # setup command line parser
    parser = ArgumentParser(prog = "pyst.py",
                            description = "A Smalltalk environment implemented in python")
    #parser.add_argument("img_file", type=str, help = "system state image file")
    parser.add_argument("img_file",
                        type = str,
                        action = "store",
                        help = "image file name")
    parser.add_argument("-r", "--rebuild",
                        action = "store_true",
                        default = False,
                        help = "rebuild system image from scratch")
    parser.add_argument("-s", "--save",
                        action = "store_true",
                        default = False,
                        help = "save image file after rebuild or load")
    parser.add_argument("-v", "--verbose",
                        action = "store_true",
                        default = False,
                        help = "display verbose output")
    parser.add_argument("-b", "--breakpoint",
                        action = "store",
                        type = str,
                        nargs = 1,
                        help = "set debug breakpoint")
                        
    # get command line values
    args = parser.parse_args()

    # run the system
    if args.rebuild:
        context = Smalltalk.rebuild(args, PYST_DIR, parse_break(args.breakpoint))
    else:
        context = Smalltalk.load(args, PYST_DIR, parse_break(args.breakpoint))
    Smalltalk.run(context)
    
    
    