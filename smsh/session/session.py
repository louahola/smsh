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

import datetime

from smsh import clients


class SessionConfiguration(object):
    def __init__(self, buffered_output, environment_variables, user, working_directory):
        self.buffered_output = buffered_output
        self.environment_variables = environment_variables
        self.user = user
        self.working_directory = working_directory


class SessionContext(object):
    EXPORTS_FILE_NAME = 'exports'
    SETS_FILE_NAME = 'sets'

    def __init__(self, temp_dir, user, working_directory):
        self._temp_dir = temp_dir
        self._user = user
        self._cwd = working_directory
        self._exit_code = 0

    def get_cwd(self):
        return self._cwd

    def set_cwd(self, cwd):
        self._cwd = cwd

    def get_exit_code(self):
        return self._exit_code

    def set_exit_code(self, exit_code):
        self._exit_code = exit_code

    def get_temp_dir(self):
        return self._temp_dir

    def get_sets_file_path(self):
        return "{}/{}".format(self._temp_dir, self.SETS_FILE_NAME)

    def get_exports_file_path(self):
        return "{}/{}".format(self._temp_dir, self.EXPORTS_FILE_NAME)

    def get_user(self):
        return self._user

    def set_user(self, user):
        self._user = user


class Session(object):
    def __init__(self, configuration, target):
        self.buffered_output = configuration.buffered_output

        self.target = target
        self.iam_arn = clients.STS().get_caller_identity()['Arn']

        epoch = datetime.datetime.utcfromtimestamp(0)
        now = datetime.datetime.utcnow()
        timestamp = (now - epoch).total_seconds()
        self.session_id = "{}-{}".format(self.iam_arn, timestamp)

        self.session_context = SessionContext(
            temp_dir="/tmp/smsh/{}".format(self.session_id),
            user=configuration.user,
            working_directory=configuration.working_directory
        )

        self.invocation = None

    def __enter__(self):
        raise NotImplementedError("Override this method!")

    def start(self):
        raise NotImplementedError("Override this method!")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.invocation:
            self.invocation.cancel()
