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

from smsh import clients
from smsh.target.instance import Instance

INSTANCE_ID_PATTERN = re.compile("^i-[a-zA-Z0-9]*$")
IP_PATTERN = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
ECS_CONTAINER_ID_PATTERN = re.compile("[a-zA-Z0-9]*")


class InvalidTargetException(Exception):
    pass


def _get_instance_id(filter_name, filter_value):
    instance_id = None

    client = clients.EC2()
    resp = client.describe_instances(
        Filters=[
            {
                'Name': filter_name,
                'Values': [filter_value]
            }
        ]
    )
    for reservation in resp.get('Reservations', []):
        for ec2_instance in reservation.get('Instances', []):
            instance_id = ec2_instance['InstanceId']
            break

    return instance_id


def create(target):
    if INSTANCE_ID_PATTERN.match(target):
        return Instance(instance_id=target)
    elif IP_PATTERN.match(target):
        instance_id = _get_instance_id(
            filter_name='private-ip-address',
            filter_value=target
        )
        if not instance_id:
            instance_id = _get_instance_id(
                filter_name='ip-address',
                filter_value=target
            )
        if not instance_id:
            raise InvalidTargetException(target, "No Instance-ID could be found for IP")

        return Instance(instance_id=instance_id)
    else:
        raise NotImplementedError("{} did not match either an instance ID or instance IP pattern".format(target))
