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


class TypeCommand(Command):
    """Command to check the type of a command."""
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        # Check if the command is a recognized builtin
        builtins = ["help", "exit", "echo", "type", "pwd", "cd"]
        if self.command_name in builtins:
            return f"{self.command_name} is a shell builtin"

        # Use PATH environment variable to search for executable commands
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for path_dir in path_dirs:
            command_path = os.path.join(path_dir, self.command_name)
            if os.path.exists(command_path):
                return f"{self.command_name} is {command_path}"
        else:
            return f"{self.command_name}: not found"


# Quote handling for single and double quotes with backslash support
class QuoteProcessor:
    """Processes quoted strings in input."""

    @staticmethod
    def handle_single_quotes(text):
        """Handles text enclosed in single quotes (literal values)."""
        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]  # Strip quotes
        return text

    @staticmethod
    def handle_double_quotes(text):
        """Handles text enclosed in double quotes (escape sequences allowed)."""
        if text.startswith('"') and text.endswith('"'):
            content = text[1:-1]  # Strip surrounding double quotes
            # Process escape sequences specific to double quotes
            processed = []
            i = 0
            while i < len(content):
                if content[i] == "\\" and i + 1 < len(content):
                    # Handle valid escape sequences
                    if content[i + 1] in ['"', "\\", "$", "\n"]:
                        processed.append(content[i + 1])
                        i += 2
                    else:
                        # Backslash followed by other characters, treat as literal
                        processed.append("\\")
                        processed.append(content[i + 1])
                        i += 2
                else:
                    processed.append(content[i])
                    i += 1
            return "".join(processed)
        return text

    @staticmethod
    def handle_unquoted_backslashes(token):
        """Handles backslashes in unquoted text."""
        processed = []
        i = 0
        while i < len(token):
            if token[i] == "\\" and i + 1 < len(token):
                # Keep the literal value of the next character
                processed.append(token[i+1])
                i += 2
            else:
                processed.append(token[i])
                i += 1
        return "".join(processed)

    @staticmethod
    def split_input(user_input):
        """Splits input into tokens and handles quotes and backslashes."""
        tokens = []
        current_token = []
        in_single_quote = False
        in_double_quote = False

        i = 0
        while i < len(user_input):
            char = user_input[i]

            if char == "'" and not in_double_quote:
                # Single quote toggle
                if in_single_quote:
                    in_single_quote = False  # Closing single quote
                else:
                    in_single_quote = True  # Opening single quote
            elif char == '"' and not in_single_quote:
                # Double quote toggle
                if in_double_quote:
                    in_double_quote = False  # Closing double quote
                else:
                    in_double_quote = True  # Opening double quote
            elif char == " " and not in_single_quote and not in_double_quote:
                # Space outside of quotes: finalize the current token
                if current_token:
                    tokens.append("".join(current_token))
                    current_token = []
            else:
                # Regular character or inside quotes
                current_token.append(char)

            i += 1

        # Append the last token if there is one
        if current_token:
            tokens.append("".join(current_token))

        # Handle unclosed quotes
        if in_single_quote:
            raise ValueError("Unclosed single quote in input")
        if in_double_quote:
            raise ValueError("Unclosed double quote in input")

        # Handle quotes and backslashes in tokens
        processed_tokens = []
        for token in tokens:
            if token.startswith("'") and token.endswith("'"):
                processed_tokens.append(QuoteProcessor.handle_single_quotes(token))
            elif token.startswith('"') and token.endswith('"'):
                processed_tokens.append(QuoteProcessor.handle_double_quotes(token))
            else:
                processed_tokens.append(QuoteProcessor.handle_unquoted_backslashes(token))

        return processed_tokens


# Command Factory to process user input and create commands
class CommandFactory:
    @staticmethod
    def get_command(user_input):
        try:
            # Split and preprocess input
            tokens = QuoteProcessor.split_input(user_input)
        except ValueError as e:
            return InvalidCommand(str(e))

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
            # Join the preprocessed tokens for the echo message
            message = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return EchoCommand(message)
        elif command_name == "pwd":
            return PwdCommand()
        elif command_name == "cd":
            # Check if a target directory is provided
            target_directory = tokens[1] if len(tokens) > 1 else os.path.expanduser("~")
            return CdCommand(target_directory)
        elif command_name == "type":
            # Check if a command name is provided to type
            if len(tokens) > 1:
                return TypeCommand(tokens[1])
            else:
                return InvalidCommand("type")
        else:
            # Treat it as an external command with arguments
            return ExternalCommand(command_name, tokens[1:])


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