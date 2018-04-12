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

from smsh.target.target import Target
from smsh import clients


class Instance(Target):
    DEFAULT_EXECUTION_TIMEOUT = '900'
    DEFAULT_DOCUMENT = 'AWS-RunShellScript'

    def __init__(self, instance_id):
        Target.__init__(self, instance_id)

    def send_command(self, wd, command):
        logging.debug("Sending command {} to instance {}".format(command, self.get_instance_id()))
        client = clients.SSM()
        resp = client.send_command(
            InstanceIds=[
                self.get_instance_id()
            ],
            DocumentName=self.DEFAULT_DOCUMENT,
            Parameters={
                'workingDirectory': [wd],
                'commands': [command],
                'executionTimeout': [self.DEFAULT_EXECUTION_TIMEOUT]
            }
        )
        return resp.get('Command', {}).get('CommandId')
