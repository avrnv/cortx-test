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
"""Test library for user and bucket quota related operations."""

import json
import math
import time
from http import HTTPStatus
from random import SystemRandom
from string import Template

from botocore.exceptions import ClientError
from commons import configmanager
from commons.constants import Rest as const
from libs.csm.rest.csm_rest_test_lib import RestTestLib
from libs.s3 import s3_misc

class GetSetQuota(RestTestLib):
    """RestIamUser contains all the Rest API calls for iam user operations"""

    def __init__(self):
        super(GetSetQuota, self).__init__()
        self.template_payload = Template(const.IAM_USER_DATA_PAYLOAD)
        self.iam_user = None
        self.cryptogen = SystemRandom()
        self.csm_conf = configmanager.get_config_wrapper(fpath="config/csm/test_rest_capacity.yaml")
        self.bucket = "iam-user-bucket-" + str(int(time.time_ns()))
        self.obj_name_prefix = "created_obj"
        self.obj_name = f'{self.obj_name_prefix}{time.perf_counter_ns()}'

    @RestTestLib.authenticate_and_login
    def get_user_quota(self, uid, **kwargs):
        """
        Get user or bucket quota
        :param uid: userid
        :param header: header for api authentication
        :return: response
        """
        self.log.info("Get IAM user request....")
        if "headers" in kwargs.keys():
            header = kwargs["headers"]
        else:
            header = self.headers
        endpoint = self.config["get_set_quota"]
        endpoint = endpoint.format(uid)
        response = self.restapi.rest_call("get", endpoint=endpoint,
                                          headers=header)
        self.log.info("Get user quota request successfully sent...")
        return response

    #pylint disable=no-self-use
    def iam_user_quota_payload(self,quota_type: str, enabled: str,
                        max_size: int, max_objects: int):
        """
        Create IAM user quota payload
        """
        payload = {}
        payload.update({"quota_type": quota_type})
        payload.update({"enabled": enabled})
        payload.update({"max_size": max_size})
        payload.update({"max_objects" : max_objects})
        self.log.info("Payload: %s", payload)
        return payload

    @RestTestLib.authenticate_and_login
    def set_user_quota(self, uid, payload: dict, **kwargs):
        """
        Set user or bucket quota
        :param uid: userid
        :param header: header for api authentication
        :param payload: IAM User quota payload
        :return: response
        """
        self.log.info("Get IAM user request....")
        if "headers" in kwargs.keys():
            header = kwargs["headers"]
        else:
            header = self.headers
        endpoint = self.config["get_set_quota"]
        endpoint = endpoint.format(uid)
        response = self.restapi.rest_call("put", endpoint=endpoint,
                                          json_dict=json.dumps(payload),
                                          headers=header)
        self.log.info("Set user quota request successfully sent...")
        return response

    def verify_get_set_user_quota(self, uid: str, payload: dict, verify_response=False,
                                  expected_response = HTTPStatus.CREATED,
                                  login_as="csm_admin_user"):
        """
        Verify get and set user quota
        """
        set_response = self.set_user_quota(uid, payload, login_as=login_as)
        result = True
        if set_response.status_code == expected_response:
            self.log.info("SET response check passed.")
        else:
            self.log.error("SET response check failed")
            result = False
            return result, set_response
        get_response = self.get_user_quota(uid, login_as=login_as)
        if get_response.status_code == expected_response:
            result = True
            get_response = get_response.json()
            if verify_response:
                self.log.info("Checking response...")
                for key, value in get_response.items():
                    self.log.info("Expected response for %s: %s", key, value)
                    if key in ("enabled","max_size","max_objects","check_on_raw"):
                        continue
                    if key == "max_size_kb":
                        payload.update({"max_size_kb":get_response["max_size"]/1000})
                    self.log.info("Actual response for %s: %s", key, payload[key])
                    if value != payload[key]:
                        self.log.error("Actual and expected response for %s didnt match", key)
                        result = False
        else:
            self.log.error("Status code check failed.")
            result = False
        return result, get_response

    def verify_max_size(self, max_size: int, akey: str, skey: str):
        """
	Verify put object of random size fails after exceeding max size limit
        """
        err_msg = ""
        self.log.info("Perform Put operation for 1 object of max size")
        res = s3_misc.create_put_objects(self.obj_name, self.bucket,
                       akey, skey, object_size=max_size)
        if res:
            self.log.info("Perform Put operation of Random size and 1 object")
            random_size = self.cryptogen.randrange(1, max_size)
            try:
                resp = s3_misc.create_put_objects(self.obj_name, self.bucket,
                      akey, skey, object_size=random_size)
                res = False
                err_msg = "Put operation passed for object size above max size"
            except ClientError as error:
                self.log.info("Expected exception received %s", error)
                res = resp['Error']['Code'] == "....."
                err_msg = "Message check verification failed for object size above max size"
        else:
            err_msg = "Put operation failed for less than max size"
        return res, err_msg

    def verify_max_objects(self, max_size: int, max_objects: int, akey: str, skey: str):
        """
        Verify put object of random size fails after exceeding max number of objects limit
        """
        self.log.info("Perform Put operation of small size and N object")
        small_size = math.floor(max_size / max_objects)
        err_msg = ""
        for _ in range(0, max_objects):
            res = s3_misc.create_put_objects(self.obj_name, self.bucket,
                                              akey, skey, object_size=small_size)
        if res:
            self.log.info("Perform Put operation of Random size and 1 object")
            random_size = self.cryptogen.randrange(1, max_size)
            try:
                resp = s3_misc.create_put_objects(self.obj_name, self.bucket,
                                          akey, skey, object_size=random_size)
                res = False
                err_msg = "Put operation passed for object size above random size"
            except ClientError as error:
                self.log.info("Expected exception received %s", error)
                res = resp['Error']['Code'] == "......."#TODO
                err_msg = "Message check verification failed for objects more than max objects"
        else:
            err_msg = "Put operation failed for less than max objects"
        return res, err_msg
