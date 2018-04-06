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


class Command(object):
    def invoke(self, session_context, target):
        raise NotImplementedError("Overwrite This Method!")


class CommandInvocation(object):
    def __init__(self):
        pass

    def wait(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
