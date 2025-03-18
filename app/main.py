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
        return "Available commands: help, exit, echo [message], type [command]"
    
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
        path_dirs = os.environ.get("PATH", "").split(":")
        for directory in path_dirs:
            full_path = os.path.join(directory, self.command_name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                try:
                    # Execute the external program with arguments
                    result = subprocess.run(
                        [full_path] + self.arguments,
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


        

# New TypeCommand class
class TypeCommand(Command):
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        # Check if the command is a recognized builtin
        builtins = ["help", "exit", "echo", "type"]
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

#Define a CommandFactory
class CommandFactory:
    @staticmethod
    def get_command(user_input):
        tokens = user_input.split()
        command_name = tokens[0] if tokens else ""
        if command_name == "help":
            return HelpCommand()
        elif command_name == "exit":
            try:
                exit_code = int(tokens[1]) if len(tokens) > 1 else 0
                return ExitCommand(exit_code)
            except (ValueError, IndexError):
                return InvalidCommand("exit")
        elif command_name == "echo":
            # Check if a message exist to echo, otherwise return an invalid command
            message = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return EchoCommand(message) if message else InvalidCommand("echo")
        elif command_name == "type":
            # Check if a command name is provided to type
            if len(tokens) > 1:
                return TypeCommand(tokens[1])
            else:
                return InvalidCommand("type")
        else:
            return ExternalCommand(command_name, tokens[1:])
        
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
