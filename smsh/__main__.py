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
import sys

import argparse

from smsh import __version__ as version
from smsh.session import create as create_session
from smsh.session.session import SessionConfiguration
from smsh.target import create as create_target


DEFAULT_USER = 'root'
DEFAULT_WORKING_DIRECTORY = '/root'


def main():
    parser = argparse.ArgumentParser(description="SSH Into a Host")
    parser.add_argument('host', help="An EC2 instance IP (private or public), instance ID, or ECS container ID")
    parser.add_argument('-c', '--command', help="A single command to run", required=False)
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-e', '--env', action='append', help="Environment variables in the form of KEY=VALUE")
    parser.add_argument('-u', '--user', help="The local user to run as", default='root')
    parser.add_argument('-w', '--working-directory', help="Working directory", default=DEFAULT_WORKING_DIRECTORY)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('--buffered-output', action='store_true', default=False)
    args = parser.parse_args()

    # logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('boto').setLevel(logging.CRITICAL)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)

    logger = logging.getLogger('command_output')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    environment_variables = {}
    if args.env:
        for var in args.env:
            (key, value) = var.split('=', 1)
            environment_variables[key] = value

    configuration = SessionConfiguration(
        environment_variables=environment_variables,
        user=args.user,
        working_directory=args.working_directory,
        buffered_output=args.buffered_output
    )

    target = create_target(args.host)
    session = create_session(
        command=args.command,
        configuration=configuration,
        target=target
    )

    with session:
        session.start()
    sys.exit(int(session.session_context.get_exit_code()))


if __name__ == '__main__':
    main()
