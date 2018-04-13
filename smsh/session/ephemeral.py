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

import logging

from smsh.target.target import CommandInvocationFailureException
from smsh.command import create as create_command
from smsh.command.exit import UserInitiatedExit
from smsh.session.session import Session


class EphemeralSession(Session):
    def __init__(self, command, configuration, target):
        Session.__init__(self, configuration=configuration, target=target)
        self.command = command

    def __enter__(self):
        self.invocation = None
        return self

    def start(self):
        try:
            user_input = self.command.strip()
            if user_input:
                try:
                    command = create_command(
                        command=user_input,
                        buffered_output=self.buffered_output
                    )

                    self.invocation = command.invoke(
                        session_context=self.session_context,
                        target=self.target
                    )
                    self.invocation.wait()

                    self.invocation.clear()
                    self.invocation = None
                except (KeyboardInterrupt, SystemExit):
                    self.invocation.cancel()
                    self.invocation = None
                except UserInitiatedExit:
                    pass
                except CommandInvocationFailureException as ex:
                    print(ex.stderr)
                    self.invocation.clear()
                    self.invocation = None

        except (KeyboardInterrupt, SystemExit):
            print()
