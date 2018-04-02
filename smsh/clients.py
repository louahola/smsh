import boto3


class SSM(object):
    _instance = None

    def __new__(cls):
        if SSM._instance is None:
            SSM._instance = boto3.client('ssm')
        return SSM._instance


class EC2(object):
    _instance = None

    def __new__(cls):
        if EC2._instance is None:
            EC2._instance = boto3.client('ec2')
        return EC2._instance


class S3(object):
    _instance = None

    def __new__(cls):
        if S3._instance is None:
            S3._instance = boto3.client('s3')
        return S3._instance


class STS(object):
    _instance = None

    def __new__(cls):
        if STS._instance is None:
            STS._instance = boto3.client('sts')
        return STS._instance
