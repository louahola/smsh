import re

from smsh.command.buffered import BufferedCommand
from smsh.command.editor import EditorCommand
from smsh.command.exit import ExitCommand
from smsh.command.unbuffered import UnbufferedCommand

CMD_EXIT_PATTERN = re.compile("^(exit|quit)$")
CMD_EDITOR_PATTERN = re.compile("^(vi|vim|nano) \S+")


def create(*, command, buffered_output):
    if CMD_EXIT_PATTERN.match(command.lower()):
        command = ExitCommand()
    elif CMD_EDITOR_PATTERN.match(command.lower()):
        cmd_parts = command.lower().split(" ")
        ide = cmd_parts[0]
        file = cmd_parts[1]
        command = EditorCommand(ide=ide, file=file)
    elif buffered_output:
        command = BufferedCommand(command)
    else:
        command = UnbufferedCommand(command)
    return command
