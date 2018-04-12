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

import time
import logging
import math

from botocore.exceptions import ClientError

from smsh import clients


class CommandInvocationFailureException(Exception):
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr


class InstanceNotFoundException(Exception):
    pass


class Target(object):
    INITIAL_POLLING_INTERVAL = 0.15
    MAX_POLLING_INTERVAL = 5
    MIN_POLLING_INTERVAL = 0.3

    def __init__(self, instance_id):
        instance = None

        client = clients.EC2()
        resp = client.describe_instances(
            InstanceIds=[instance_id],
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['pending', 'running', 'stopping', 'shutting-down']
                }
            ]
        )
        for reservation in resp.get('Reservations', []):
            for i in reservation.get('Instances', []):
                instance = i
                break

        if not instance:
            raise InstanceNotFoundException("No instance was found with ID {}".format(instance_id))

        self.instance = instance

        self.name = None
        if 'Tags' in self.instance:
            for tag in self.instance['Tags']:
                if tag['Key'] == 'Name':
                    self.name = tag['Value']
                    break
        if not self.name:
            self.name = instance_id

        self.vpc_name = self._get_vpc_name(self.instance.get('VpcId', ''))
        if not self.vpc_name:
            self.vpc_name = self.instance.get('VpcId', '')

        self.subnet_name = self._get_subnet_name(self.instance.get('SubnetId', ''))
        if not self.subnet_name:
            self.subnet_name = self.instance.get('SubnetId', '')

    @staticmethod
    def _get_vpc_name(vpc_id):
        client = clients.EC2()
        resp = client.describe_vpcs(
            VpcIds=[vpc_id]
        )
        for vpc in resp.get('Vpcs', []):
            for tag in vpc.get('Tags', []):
                if tag['Key'] == 'Name':
                    return tag['Value']

    @staticmethod
    def _get_subnet_name(subnet_id):
        client = clients.EC2()
        resp = client.describe_subnets(
            SubnetIds=[subnet_id]
        )
        for subnet in resp.get('Subnets', []):
            for tag in subnet.get('Tags', []):
                if tag['Key'] == 'Name':
                    return tag['Value']

    def get_instance_id(self):
        return self.instance['InstanceId']

    def get_details(self):
        return (
            "Instance Name: {instance_name}\n"
            "Instance ID: {instance_id}\n"
            "Instance Type: {instance_type}\n"
            "Public DNS: {public_dns}\n"
            "Public IP: {public_ip}\n"
            "Private DNS: {private_dns}\n"
            "Private IP: {private_ip}\n"
            "Subnet Name: {subnet_name}\n"
            "Subnet ID: {subnet_id}\n"
            "VPC Name: {vpc_name}\n"
            "VPC ID: {vpc_id}\n"
            "Instance Profile: {iam_role}\n"
            "Launch Time: {launch_time}\n"
            "Image ID: {image_id}"
        ).format(
            instance_name=self.name,
            instance_id=self.get_instance_id(),
            instance_type=self.instance.get('InstanceType', ''),
            public_dns=self.instance.get('PublicDnsName', ''),
            public_ip=self.instance.get('PublicIpAddress', ''),
            private_dns=self.instance.get('PrivateDnsName', ''),
            private_ip=self.instance.get('PrivateIpAddress', ''),
            subnet_name=self.subnet_name,
            subnet_id=self.instance.get('SubnetId', ''),
            vpc_name=self.vpc_name,
            vpc_id=self.instance.get('VpcId', ''),
            iam_role=self.instance.get('IamInstanceProfile', {}).get('Arn', ''),
            launch_time=self.instance.get('LaunchTime', ''),
            image_id=self.instance.get('ImageId', '')
        )

    def send_command(self, wd, command):
        raise NotImplementedError("Override This Method!")

    def wait_for_output(self, command_id):
        polling_count = 1

        info = self.describe_command(command_id)
        status = info['Status']
        while status == 'Pending' or status == 'InProgress':
            time_to_sleep = min(
                (max(self.MIN_POLLING_INTERVAL, math.pow(self.INITIAL_POLLING_INTERVAL * 10, polling_count) / 10)),
                self.MAX_POLLING_INTERVAL
            )
            logging.debug("sleeping for {}".format(time_to_sleep))
            time.sleep(time_to_sleep)
            polling_count += 1

            info = self.describe_command(command_id)
            status = info['Status']

        if status == 'Failed':
            raise CommandInvocationFailureException(
                stdout=info['StandardOutputContent'],
                stderr=info['StandardErrorContent']
            )

        return info['StandardOutputContent']

    def describe_command(self, command_id):
        client = clients.SSM()
        while True:
            try:
                resp = client.get_command_invocation(
                    InstanceId=self.get_instance_id(),
                    CommandId=command_id
                )
                return resp
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'InvocationDoesNotExist':
                    pass
                else:
                    raise ex

    def cancel_command(self, invocation_id):
        if invocation_id:
            logging.debug("canceling command id {}".format(invocation_id))
            client = clients.SSM()
            client.cancel_command(
                CommandId=invocation_id,
                InstanceIds=[self.get_instance_id()]
            )
