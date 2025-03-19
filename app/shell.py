import os
import sys

# Ensure that the directory of this file is in sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_factory import CommandFactory

class Shell:
    """The REPL (Read-eval-print-loop) class."""
    def __init__(self):
        self.running = True

    def read(self):
        sys.stdout.write("$ ")
        sys.stdout.flush()
        return input().strip()

    def eval(self, user_input: str):
        return CommandFactory.get_command(user_input)

    def print(self, output):
        if output:
            print(output)

    def loop(self):
        while self.running:
            try:
                user_input = self.read()
                command = self.eval(user_input)
                output = command.execute()
                self.print(output)
            except KeyboardInterrupt:
                print("\nCtrl+C detected. Type 'exit' to quit.")
            except EOFError:
                print("\nEOF detected. Type 'exit' to quit.")