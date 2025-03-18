import sys
import os
import subprocess

# Define a base QuoteHandler class
class QuoteHandler:
    """Base class for handling quoted input."""
    def handle(self, text):
        raise NotImplementedError("Subclasses must implement the handle method")

class SingleQuoteHandler(QuoteHandler):
    """Handles text enclosed in single quotes."""
    def handle(self, text):
        if text.startswith("'") and text.endswith("'"):
            # Strip the surrounding single quotes
            return text[1:-1]
        else:
            raise ValueError("Invalid single-quoted string")

class DoubleQuoteHandler(QuoteHandler):
    """Handles text enclosed in double quotes."""
    def handle(self, text):
        if text.startswith('"') and text.endswith('"'):
            # Strip the surrounding double quotes and handle escaped characters
            content = text[1:-1]
            return content.replace('\\"', '"').replace("\\\\", "\\")
        else:
            raise ValueError("Invalid double-quoted string")

class BackslashInSingleQuoteHandler(QuoteHandler):
    """Handles backslashes within single quotes."""
    def handle(self, text):
        if text.startswith("'") and text.endswith("'"):
            # Backslashes are literal in single quotes
            return text[1:-1]  # Just strip the quotes, no escaping inside single quotes
        else:
            raise ValueError("Invalid single-quoted string with backslashes")

class BackslashInDoubleQuoteHandler(QuoteHandler):
    """Handles backslashes within double quotes."""
    def handle(self, text):
        if text.startswith('"') and text.endswith('"'):
            # Interpret backslashes for escaping in double quotes
            content = text[1:-1]
            content = content.encode("utf-8").decode("unicode_escape")  # Process escape sequences
            return content
        else:
            raise ValueError("Invalid double-quoted string with backslashes")

# Define a base Command class
class Command:
    """Base Command class; all commands inherit from this."""
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")

# Define specific commands
class HelpCommand(Command):
    def execute(self):
        return "Available commands: help, exit, echo [message], type [command], pwd, cd [directory]"

class EchoCommand(Command):
    def __init__(self, message):
        self.message = message

    def execute(self):
        return self.message

# Define a CommandFactory
class CommandFactory:
    @staticmethod
    def preprocess_input(user_input):
        """Preprocesses the user input, handling quotes and escape characters."""
        # Check for single quotes
        if user_input.startswith("'") and user_input.endswith("'"):
            return SingleQuoteHandler().handle(user_input)
        # Check for double quotes
        elif user_input.startswith('"') and user_input.endswith('"'):
            return DoubleQuoteHandler().handle(user_input)
        # Check for backslashes inside single quotes
        elif user_input.startswith("'\\") and user_input.endswith("'"):
            return BackslashInSingleQuoteHandler().handle(user_input)
        # Check for backslashes inside double quotes
        elif user_input.startswith('"\\') and user_input.endswith('"'):
            return BackslashInDoubleQuoteHandler().handle(user_input)
        else:
            return user_input  # Default case: Return unprocessed input

    @staticmethod
    def get_command(user_input):
        user_input = CommandFactory.preprocess_input(user_input)
        tokens = user_input.split()
        command_name = tokens[0] if tokens else ""
        if command_name == "help":
            return HelpCommand()
        elif command_name == "echo":
            message = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return EchoCommand(message)
        else:
            return InvalidCommand(command_name)

class InvalidCommand(Command):
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        return print(f"{self.command_name}: command not found")

class Shell:
    """The REPL structure"""
    def __init__(self):
        self.running = True

    def read(self):
        """Reads user input"""
        sys.stdout.write("$ ")
        sys.stdout.flush()
        return input().strip()
    
    def eval(self, user_input):
        """Evaluates the user input by delegating to the CommandFactory."""
        return CommandFactory.get_command(user_input)
    
    def print(self, output):
        """Prints the command's output"""
        if output:
            print(output)

    def loop(self):
        """The core REPL loop"""
        while self.running:
            try:
                # Read
                user_input = self.read()

                # Evaluate
                command = self.eval(user_input)

                # Execute and get output
                output = command.execute()

                # Print output
                self.print(output)
            except KeyboardInterrupt:
                print("\nCtrl+C detected. Type 'exit' to quit.")
            except EOFError:
                print("\nEOF detected. Type 'exit' to quit.")

if __name__ == "__main__":
    shell = Shell()
    shell.loop()