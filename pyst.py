"""
A Smalltalk environment implemented in Python
"""

from system import Smalltalk

if __name__ == '__main__':

    from argparse import ArgumentParser
    
    # setup command line parser
    parser = ArgumentParser(prog = "pyst.py",
                            description = "A Smalltalk environment implemented in python")
    #parser.add_argument("img_file", type=str, help = "system state image file")
    parser.add_argument("-r", "--rebuild",
                        action = "store_true",
                        default = False,
                        help = "rebuild system image from scratch")
    parser.add_argument("-d", "--debug", 
                        action = "store_true", 
                        default = False, 
                        help = "enable interpreter debugger")
    parser.add_argument("-v", "--verbose",
                        action = "store_true",
                        default = False,
                        help = "display verbose output")
                        
    # get command line values
    args = parser.parse_args()

    # run the system
    Smalltalk.rebuild(args.debug)
    