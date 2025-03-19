import os
import sys

# Ensure that the directory of this file is in sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shell import Shell

def main():
    shell = Shell()
    shell.loop()

if __name__ == "__main__":
    main()