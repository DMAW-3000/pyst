"""
A Smalltalk environment implemented in Python
"""

from system import Smalltalk

if __name__ == '__main__':

    from argparse import ArgumentParser
    
    parser = ArgumentParser(prog = "pyst.py",
                            description = "A Smalltalk environment implemented in python")
    #parser.add_argument("img_file", type=str, help = "system state image file")
    args = parser.parse_args()

    Smalltalk.rebuild()
    