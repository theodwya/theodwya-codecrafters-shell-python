import sys


# Define a base Command class
class Command:
    def execute(self):
        return
    # raise NotImplementedError("Subclasses must implement the execute method")
    
# Define specific commands
class HelpCommand(Command):
    def execute(self):
        return "Available commands: help, exit"
    
class ExitCommand(Command):
    def execute(self):
        sys.exit("Exiting the shell...")

class InvalidCommand(Command):
    def __init__(self, command_name):
        self.command_name = command_name

    def execute(self):
        return print(f"{self.command_name}: command not found")

#Define a CommandFactory
class ComamandFactory:
    @staticmethod
    def get_command(command_name):
        if command_name == "help":
            return HelpCommand()
        elif command_name == "exit":
            return ExitCommand()
        else:
            return InvalidCommand(command_name)

def main():
    while True:
        #Uncomment this block to pass the first stage
        sys.stdout.write("$ ")

        # Get user input
        user_input = input().strip()

        # Get the appropriate comand object from the factory
        command = ComamandFactory.get_command(user_input)

        # Execute the command
        output = command.execute()

        # If the command produces output, display
        if output:
            print(output)

    # Wait for user input
    # input()


if __name__ == "__main__":
    main()
