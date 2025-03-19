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
        return os.getcwd()


class CdCommand(Command):
    """Command to change the current working directory."""
    def __init__(self, target_directory):
        self.target_directory = target_directory

    def execute(self):
        try:
            target = os.path.expanduser(self.target_directory)
            os.chdir(target)
        except FileNotFoundError:
            return f"cd: {self.target_directory}: No such file or directory"
        except NotADirectoryError:
            return f"cd: {self.target_directory}: Not a directory"
        except PermissionError:
            return f"cd: {self.target_directory}: Permission denied"


class TypeCommand(Command):
    """Command to check the type of a command."""
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        builtins = ["help", "exit", "echo", "type", "pwd", "cd"]
        if self.command_name in builtins:
            return f"{self.command_name} is a shell builtin"
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for path_dir in path_dirs:
            command_path = os.path.join(path_dir, self.command_name)
            if os.path.exists(command_path):
                return f"{self.command_name} is {command_path}"
        return f"{self.command_name}: not found"


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
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for directory in path_dirs:
            full_path = os.path.join(directory, self.command_name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                try:
                    result = subprocess.run(
                        [self.command_name] + self.arguments,
                        executable=full_path,
                        capture_output=True,
                        text=True
                    )
                    print(result.stdout, end="")
                    if result.stderr:
                        print(result.stderr, file=sys.stderr, end="")
                    return
                except Exception as e:
                    return print(f"Error while executing {self.command_name}: {e}")
        return print(f"{self.command_name}: command not found")


# Quote handling for single and double quotes with backslash support
class QuoteProcessor:
    """Processes quoted strings using a shell-like state machine."""

    @staticmethod
    def split_input(user_input: str):
        """
        Splits the user input into tokens, concatenating adjacent segments
        (quoted or unquoted) into a single token.
        """
        words = []
        current_word = ""
        i = 0
        n = len(user_input)

        while i < n:
            # Skip whitespace as a delimiter if current_word is empty;
            # if not empty, it means we've reached the end of a word.
            if user_input[i].isspace():
                # finish current word if we have one
                while i < n and user_input[i].isspace():
                    i += 1
                if current_word != "":
                    words.append(current_word)
                    current_word = ""
                continue

            char = user_input[i]

            # Handle single quotes: take content literally.
            if char == "'":
                i += 1
                start = i
                while i < n and user_input[i] != "'":
                    current_word += user_input[i]
                    i += 1
                if i >= n:
                    raise ValueError("Unclosed single quote in input")
                i += 1  # Skip closing quote
                continue

            # Handle double quotes, processing escapes.
            if char == '"':
                i += 1
                while i < n and user_input[i] != '"':
                    if user_input[i] == "\\" and i + 1 < n:
                        next_char = user_input[i + 1]
                        if next_char in ['"', "\\", "$", "\n"]:
                            current_word += next_char
                            i += 2
                        else:
                            current_word += "\\" + next_char
                            i += 2
                    else:
                        current_word += user_input[i]
                        i += 1
                if i >= n:
                    raise ValueError("Unclosed double quote in input")
                i += 1  # Skip closing quote
                continue

            # Handle backslash outside quotes.
            if char == "\\":
                if i + 1 < n:
                    current_word += user_input[i + 1]
                    i += 2
                else:
                    current_word += "\\"
                    i += 1
                continue

            # Regular character: add to current word.
            current_word += char
            i += 1

        if current_word != "":
            words.append(current_word)
        return words


# Command Factory to process input and return commands.
class CommandFactory:
    @staticmethod
    def get_command(user_input):
        try:
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
            message = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return EchoCommand(message)
        elif command_name == "pwd":
            return PwdCommand()
        elif command_name == "cd":
            target_directory = tokens[1] if len(tokens) > 1 else os.path.expanduser("~")
            return CdCommand(target_directory)
        elif command_name == "type":
            if len(tokens) > 1:
                return TypeCommand(tokens[1])
            else:
                return InvalidCommand("type")
        else:
            return ExternalCommand(command_name, tokens[1:])


# The Shell class (REPL)
class Shell:
    """The REPL structure"""
    def __init__(self):
        self.running = True

    def read(self):
        sys.stdout.write("$ ")
        sys.stdout.flush()
        return input().strip()

    def eval(self, user_input):
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


if __name__ == "__main__":
    shell = Shell()
    shell.loop()