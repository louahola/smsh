#!/usr/bin/env python

import logging

import argparse

from smsh.session import create as create_session
from smsh.session.session import Session, SessionConfiguration
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
    parser.add_argument('--buffered-output', action='store_true', default=False)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('boto').setLevel(logging.CRITICAL)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)

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
    session = create_session(configuration, target, args.command)

    with session:
        session.start()


if __name__ == '__main__':
    main()
