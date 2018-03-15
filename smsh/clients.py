import boto3


class SSM(object):
    __instance = None

    def __new__(cls):
        if SSM.__instance is None:
            SSM.__instance = boto3.client("ssm")
        return SSM.__instance


class EC2(object):
    __instance = None

    def __new__(cls):
        if EC2.__instance is None:
            EC2.__instance = boto3.client("ec2")
        return EC2.__instance


class S3(object):
    __instance = None

    def __new__(cls):
        if S3.__instance is None:
            S3.__instance = boto3.client("s3")
        return S3.__instance


class STS(object):
    __instance = None

    def __new__(cls):
        if STS.__instance is None:
            STS.__instance = boto3.client("sts")
        return STS.__instance
