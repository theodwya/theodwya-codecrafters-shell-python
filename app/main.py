import sys


# Define a base Command class
class Command:
    """Base Command class; all commands inherit from this."""
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")
    
# Define specific commands
class HelpCommand(Command):
    def execute(self):
        return "Available commands: help, exit, exho [message]"
    
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
        else:
            return InvalidCommand(command_name)
        
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
