# Copyright (C) 2018 Lou Ahola, HashChain Technology, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from smsh.command.buffered import BufferedCommand
from smsh.command.editor import EditorCommand
from smsh.command.exit import ExitCommand
from smsh.command.unbuffered import UnbufferedCommand

CMD_EXIT_PATTERN = re.compile("^(exit|quit)$")
CMD_EDITOR_PATTERN = re.compile("^(vi|vim|nano) \S+")
LICENSE_PATTERN = re.compile("^smsh\-license")


def create(command, buffered_output):
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
