import sys
import os
import subprocess


# Define a base Command class
class Command:
    """Base Command class; all commands inherit from this."""
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")


# Define specific commands
class HelpCommand(Command):
    def execute(self):
        return "Available commands: help, exit, echo [message], type [command], pwd, cd [directory]"


class ExitCommand(Command):
    def __init__(self, exit_code):
        self.exit_code = exit_code

    def execute(self):
        sys.exit(self.exit_code)


class EchoCommand(Command):
    def __init__(self, message):
        self.message = message

    def execute(self):
        return self.message


class PwdCommand(Command):
    """Command to print the current working directory."""
    def execute(self):
        return os.getcwd()  # Return the absolute path of the current working directory


class CdCommand(Command):
    """Command to change the current working directory."""
    def __init__(self, target_directory):
        self.target_directory = target_directory

    def execute(self):
        try:
            # Expand `~` to the home directory
            target = os.path.expanduser(self.target_directory)

            # Change the current working directory
            os.chdir(target)
        except FileNotFoundError:
            return f"cd: {self.target_directory}: No such file or directory"
        except NotADirectoryError:
            return f"cd: {self.target_directory}: Not a directory"
        except PermissionError:
            return f"cd: {self.target_directory}: Permission denied"


class InvalidCommand(Command):
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        return print(f"{self.command_name}: command not found")


class ExternalCommand(Command):
    def __init__(self, command_name, arguments):
        self.command_name = command_name
        self.arguments = arguments

    def execute(self):
        # Use PATH to find the executable
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for directory in path_dirs:
            full_path = os.path.join(directory, self.command_name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                try:
                    # Execute the external program with arguments
                    # Pass the command name (not the full path) as Arg #0
                    result = subprocess.run(
                        [self.command_name] + self.arguments,
                        executable=full_path,  # Use the resolved full path to execute the program
                        capture_output=True,
                        text=True
                    )
                    # Print the program's standard output
                    print(result.stdout, end="")
                    # Print the program's standard error (if any)
                    if result.stderr:
                        print(result.stderr, file=sys.stderr, end="")
                    return
                except Exception as e:
                    return print(f"Error while executing {self.command_name}: {e}")

        # Command not found in PATH
        return print(f"{self.command_name}: command not found")


# Quote handling for single and double quotes
class QuoteProcessor:
    """Processes quoted strings in input."""

    @staticmethod
    def handle_single_quotes(text):
        """Handles text enclosed in single quotes."""
        if text.startswith("'") and text.endswith("'"):
            # Strip the surrounding single quotes
            return text[1:-1]  # Return the literal content inside the single quotes
        return text

    @staticmethod
    def preprocess(tokens):
        """
        Preprocess tokens to handle quoted arguments.
        """
        processed_tokens = []
        for token in tokens:
            if token.startswith("'") and token.endswith("'"):
                # Handle single-quoted strings
                processed_tokens.append(QuoteProcessor.handle_single_quotes(token))
            else:
                # Leave other tokens as is (for now)
                processed_tokens.append(token)
        return processed_tokens


# Command Factory to process user input and create commands
class CommandFactory:
    @staticmethod
    def get_command(user_input):
        # Split input into tokens
        tokens = user_input.split()

        # Preprocess tokens to handle quotes
        tokens = QuoteProcessor.preprocess(tokens)

        if not tokens:
            return InvalidCommand("")

        command_name = tokens[0]
        if command_name == "help":
            return HelpCommand()
        elif command_name == "exit":
            try:
                exit_code = int(tokens[1]) if len(tokens) > 1 else 0
                return ExitCommand(exit_code)
            except (ValueError, IndexError):
                return InvalidCommand("exit")
        elif command_name == "echo":
            message = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return EchoCommand(message)
        else:
            return InvalidCommand(command_name)


# The Shell class
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