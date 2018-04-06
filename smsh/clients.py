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
