#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

"""Python Library using boto3 module to perform Object Versioning Operations."""

import logging

from libs.s3.s3_core_lib import S3Lib

LOGGER = logging.getLogger(__name__)


class Versioning(S3Lib):
    """Class containing methods to implement versioning functionality."""

    def put_bucket_versioning(self,
                              bucket_name: str = None,
                              status: str = None) -> dict:
        """
        Set/Update the versioning configuration of a bucket.

        :param bucket_name: Target bucket for the PUT Bucket Versioning call.
        :param status: Versioning status to be set, supported values - "Enabled" or "Suspended"
        :return: response
        """
        response = self.s3_client.put_bucket_versioning(
            Bucket=bucket_name, VersioningConfiguration={"Status": status})
        LOGGER.debug(response)

        return response

    def get_bucket_versioning(self,
                              bucket_name: str = None) -> dict:
        """
        Get the versioning configuration of a bucket.

        :param bucket_name: Target bucket for the GET Bucket Versioning call.
        :return: response
        """
        response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
        LOGGER.debug(response)

        return response

    def list_object_versions(self,
                             bucket_name: str = None) -> dict:
        """
        List all the versions and delete markers present in a bucket.

        :param bucket_name: Target bucket for the List Object Versions call.
        :return: response
        """
        response = self.s3_client.list_object_versions(Bucket=bucket_name)
        LOGGER.debug(response)

        return response

    def get_object_version(self,
                    bucket: str = None,
                    key: str = None,
                    version_id: str = None) -> dict:
        """
        Get a version of an object.

        :param bucket: Target bucket for GET Object with VersionId call.
        :param key: Target key for GET Object with VersionId call.
        :param version_id: Target version ID for GET Object with VersionId call.
        :return: response
        """
        response = self.s3_client.get_object(
            Bucket=bucket, Key=key, VersionId=version_id)
        LOGGER.debug(response)

        return response

    def head_object_version(self,
                    bucket: str = None,
                    key: str = None,
                    version_id: str = None) -> dict:
        """
        Get the metadata of an object's version.

        :param bucket: Target bucket for HEAD Object with VersionId call.
        :param key: Target key for HEAD Object with VersionId call.
        :param version_id: Target version ID for HEAD Object with VersionId call.
        :return: response
        """
        response = self.s3_client.head_object(
            Bucket=bucket, Key=key, VersionId=version_id)
        LOGGER.debug(response)

        return response

    def delete_object_version(self,
                    bucket: str = None,
                    key: str = None,
                    version_id: str = None) -> dict:
        """
        Delete an object's version

        :param bucket: Target bucket for DELETE Object with VersionId call.
        :param key: Target key for DELETE Object with VersionId call.
        :param version_id: Target version ID for DELETE Object with VersionId call.
        :return: response
        """
        response = self.s3_client.delete_object(
            Bucket=bucket, Key=key, VersionId=version_id)
        LOGGER.debug(response)

        return response
