import os
import sys
import subprocess

class Command:
    """Base Command class; all commands inherit from this."""
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")

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
    def execute(self):
        return os.getcwd()

class CdCommand(Command):
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
        return f"{self.command_name}: command not found"

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
                    # Print standard error directly to stderr.
                    if result.stderr:
                        print(result.stderr, file=sys.stderr, end="")
                    return result.stdout
                except Exception as e:
                    return f"Error while executing {self.command_name}: {e}"
        return f"{self.command_name}: command not found"

class RedirectCommand(Command):
    """
    A wrapper command that redirects the standard output of
    an inner command to a specified file.
    """
    def __init__(self, command, filename):
        self.command = command  # The inner command to execute.
        self.filename = filename

    def execute(self):
        output = self.command.execute()
        try:
            with open(self.filename, "w") as f:
                f.write(output)
        except Exception as e:
            print(f"Error writing to file {self.filename}: {e}", file=sys.stderr)
        # When output is redirected, nothing is printed to stdout.
        return ""