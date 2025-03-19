import os
import sys

# Ensure that the directory of this file is in sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands import (
    HelpCommand, ExitCommand, EchoCommand, PwdCommand, CdCommand,
    TypeCommand, InvalidCommand, ExternalCommand, RedirectCommand
)
from parser import QuoteProcessor

class CommandFactory:
    @staticmethod
    def get_command(user_input: str):
        try:
            tokens = QuoteProcessor.split_input(user_input)
        except ValueError as e:
            return InvalidCommand(str(e))

        if not tokens:
            return InvalidCommand("")

        # Check for redirection operator ('>' or '1>')
        redir_index = None
        for i, token in enumerate(tokens):
            if token in (">", "1>"):
                redir_index = i
                break

        if redir_index is not None:
            # Must have a target file token after the operator.
            if redir_index == len(tokens) - 1:
                return InvalidCommand("No file specified for redirection")
            redir_target = tokens[redir_index + 1]
            # The command tokens are those before the redirection operator.
            command_tokens = tokens[:redir_index]
            # Reassemble the command string and recursively call get_command.
            command_str = " ".join(command_tokens)
            base_command = CommandFactory.get_command(command_str)
            return RedirectCommand(base_command, redir_target)

        # No redirection, process normally.
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