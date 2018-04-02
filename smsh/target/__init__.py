import re

from smsh import clients
from smsh.target.instance import Instance

INSTANCE_ID_PATTERN = re.compile("^i-[a-zA-Z0-9]*$")
IP_PATTERN = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
ECS_CONTAINER_ID_PATTERN = re.compile("[a-zA-Z0-9]*")


class InvalidTargetException(Exception):
    pass


def _get_instance_id(*, filter_name, filter_value):
    instance_id = None

    client = clients.EC2()
    resp = client.describe_instances(
        Filters=[
            {
                "Name": filter_name,
                "Values": [filter_value]
            }
        ]
    )
    for reservation in resp.get("Reservations", []):
        for ec2_instance in reservation.get("Instances", []):
            instance_id = ec2_instance["InstanceId"]
            break

    return instance_id


def create(target):
    if INSTANCE_ID_PATTERN.match(target):
        return Instance(instance_id=target)
    elif IP_PATTERN.match(target):
        instance_id = _get_instance_id(
            filter_name="private-ip-address",
            filter_value=target
        )
        if not instance_id:
            instance_id = _get_instance_id(
                filter_name="ip-address",
                filter_value=target
            )
        if not instance_id:
            raise InvalidTargetException(target, "No Instance-ID could be found for IP")

        return Instance(instance_id=instance_id)
    else:
        raise NotImplementedError("{} did not match either an instance ID or instance IP pattern".format(target))
