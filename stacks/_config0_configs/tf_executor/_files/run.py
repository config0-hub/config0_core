"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json
from config0_publisher.loggerly import Config0Logger
from config0_publisher.utilities import print_json


class CmEnvVars(object):
    """
    Some common methods to be inherited
    """

    def __init__(self, stack):
        self.classname = "CmEnvVars"
        self.stack = stack
        self.env_vars = {}

        # ref/revisit 543524
        # phases working with tag 0.103
        self.common_keys = [
            "TMP_BUCKET",
            "LOG_BUCKET",
            "APP_DIR",
            "STATEFUL_DIR",
            "STATEFUL_ID"
            "REMOTE_STATEFUL_BUCKET",
            "RUN_SHARE_DIR",
            "SHARE_DIR",
            "CONFIG0_RESOURCE_JSON_FILE",
            "CONFIG0_PHASES_JSON_FILE",
            "PHASES_PARAMS_HASH",
            "SCHEDULE_ID",
            "RUN_ID",
            "JOB_INSTANCE_ID",
            "TIMEOUT",
            "TF_RUNTIME"
        ]

        self.standard_codebuild_keys = [
            "BUILD_TIMEOUT",
            "CODEBUILD_IMAGE",
            "CODEBUILD_COMPUTE_TYPE",
            "CODEBUILD_IMAGE_TYPE"
        ]

        self.standard_lambda_keys = [
            "BUILD_TIMEOUT"
        ]

        self.env_vars = {}

    @staticmethod
    def _default():
        return {
            "TIMEOUT": "600"
        }

    @staticmethod
    def _default_codebuild():
        return {
            "AWS_DEFAULT_REGION": "us-east-1",
            "CODEBUILD_IMAGE": "aws/codebuild/standard:4.0",
            "CODEBUILD_COMPUTE_TYPE": "BUILD_GENERAL1_SMALL",
            "CODEBUILD_IMAGE_TYPE": "LINUX_CONTAINER"
        }

    @staticmethod
    def _default_lambda():
        return {
            "AWS_DEFAULT_REGION": "us-east-1"
        }

    def add(self, keys, default_values=None, clobber=False):
        if default_values:
            keys.extend(default_values.keys())

        for key in list(set(keys)):
            if key in self.env_vars and not clobber:
                continue
            if self.stack.get_attr(key.lower()):
                self.env_vars[key] = self.stack.get_attr(key.lower())
            elif os.environ.get(key):
                self.env_vars[key] = os.environ[key]
            elif default_values and key in default_values:
                self.env_vars[key] = default_values[key]

    def set_lambda(self, reset=False):
        if reset:
            self.reset()

        self.add(self.standard_lambda_keys,
                 self._default_lambda())

    def set_codebuild(self, reset=False):
        if reset:
            self.reset()

        self.add(self.standard_codebuild_keys,
                 self._default_codebuild())

    def set_resource(self, reset=False):
        if reset:
            self.reset()

        try:
            env_vars = self.stack.resource_configs["env_vars"]
        except Exception:
            env_vars = {}

        self.update(env_vars)

    def update(self, env_vars=None):
        if not env_vars:
            return

        for key, value in env_vars.items():
            if key.upper() in self.env_vars:
                continue
            self.env_vars[key.upper()] = value

    def set_common(self, reset=False):
        if reset:
            self.reset()

        self.add(self.common_keys,
                 self._default())

    def reset(self):
        self.env_vars = {}

    def validate(self, env_vars=None, include_num=None):
        if not env_vars:
            env_vars = self.env_vars

        for _key, _value in env_vars.items():
            if include_num:
                try:
                    number_value = int(_value)
                except Exception:
                    number_value = None
                if number_value:
                    env_vars[_key] = f"{_value}"
                    continue
            if _value is True:
                env_vars[_key] = "True"
            elif _value is False:
                env_vars[_key] = "False"
            elif _value is None:
                env_vars[_key] = "None"

    def insert(self, env_vars=None, add_env_vars=None, include_num=None):
        # this env vars is for the stack and execgroup execution
        # we need to specify create which will then

        if not add_env_vars:
            return

        if not env_vars:
            env_vars = self.env_vars

        for _key, _value in add_env_vars.items():
            if _key in env_vars:
                continue

            env_vars[_key] = _value

        self.validate(env_vars,
                      include_num=include_num)


class TFRunExec(object):
    """
    The runtimes include AWS Codebuild, Lambda function, or docker container
    to execute the Terraform/OpenTofu code
    """

    def __init__(self, stack):
        self.stack = stack
        self._set_tf_runtime()

        self.cmvars = CmEnvVars(stack=stack)
        self.cmvars.set_common()
        self.cmvars.set_lambda()
        self.cmvars.set_codebuild()

        # transfer the common vars here
        self.env_vars = self.cmvars.env_vars

        # ref 4532643623642
        if self.stack.get_attr("runtime_env_vars"):
            self.env_vars.update(self.stack.runtime_env_vars)

        # cloud specific variables storage
        self._add_aws_ssm()

        self.cmvars.validate(self.env_vars,
                             include_num=True)

    # ref 3241245124321
    def _set_tf_runtime(self):
        _tf_binary = None
        _tf_version = None

        if self.stack.get_attr("tf_runtime"):
            _binary, _version = self.stack.tf_runtime.split(":")
            _tf_binary = "tofu" if _binary in ["tofu", "opentofu"] else "terraform"
            _tf_version = _version
        if not _tf_binary:
            _tf_binary = "terraform"
            _tf_version = "1.5.4"

        self.stack.set_variable("tf_runtime",
                                f"{_tf_binary}:{_tf_version}")

    def _add_aws_ssm(self):
        if not self.stack.get_attr("ssm_name"):
            return

        self.env_vars["SSM_NAME"] = self.stack.ssm_name


class Config0Resource:
    """
    This variables and settings to insert the resource, which
    is typically a cloud infrastructure in the Config0 resource db.
    They include things like query keys, lables, etc that we use
    to interact with Config0 resource db
    """

    def __init__(self, stack):
        self.stack = stack

        # set additional vars
        self.provider = stack.provider
        self.type = stack.resource_type
        self.name = stack.resource_name
        self.resource_id = stack.resource_id

        self._parse_resource_configs()
        self._set_env_vars()

        self.tfrun_exec = TFRunExec(self.stack)

        self._set_base_values()

    def _parse_resource_configs(self):
        resource_configs = self.stack.resource_configs

        if resource_configs.get("output_keys"):
            self.output_keys = resource_configs["output_keys"]
        else:
            self.output_keys = []

        self.output_keys.extend([
            "remote_stateful_location",
            "tf_runtime"]
        )

        if resource_configs.get("output_prefix_key"):
            self.output_prefix_key = resource_configs["output_prefix_key"]
        else:
            self.output_prefix_key = self.name

        if resource_configs.get("values"):
            self.values = resource_configs["values"]
        else:
            self.values = {}

        if self.stack.get_attr("drift_protection"):
            self.values["drift_protection"] = True

    def _set_env_vars(self):
        cmvars = CmEnvVars(stack=self.stack)
        cmvars.set_common()
        cmvars.set_resource()
        self.env_vars = cmvars.env_vars

        cmvars.validate(self.env_vars,
                        include_num=False)

    def _set_base_values(self):
        self.values["resource_type"] = self.type
        self.values["name"] = self.name
        self.values["provider"] = self.provider
        self.values["tf_runtime"] = self.stack.tf_runtime

        if self.stack.resource_id:
            self.values["resource_id"] = self.stack.resource_id

    def get_inputargs(self):
        human_description = (
            f'creating resource type: "{self.type}" name: "{self.name}"'
        )

        inputargs = {
            "display": True,
            "env_vars": json.dumps(self.env_vars),
            "name": self.name,
            "human_description": human_description,
            "stateful_id": self.stack.stateful_id
        }

        if self.stack.get_attr("ssm_name"):
            inputargs["ssm_name"] = self.stack.ssm_name

        if self.stack.remote_stateful_bucket:
            inputargs["remote_stateful_bucket"] = self.stack.remote_stateful_bucket

        if self.stack.get_attr("timeout"):
            inputargs["timeout"] = self.stack.timeout

        inputargs["display_hash"] = self.stack.get_hash_object(inputargs)

        return inputargs

    def get_output_inputargs(self):
        if not self.output_keys:
            return

        overide_values = {
            "name": self.name,
            "resource_type": self.type,
            "ref_schedule_id": self.stack.schedule_id,
            "publish_keys_hash": self.stack.b64_encode(self.output_keys)
        }

        if self.stack.resource_id:
            overide_values["resource_id"] = self.stack.resource_id

        if self.output_prefix_key:
            overide_values["prefix_key"] = self.output_prefix_key

        return {
            "overide_values": overide_values,
            "automation_phase": "infrastructure",
            "human_description": f'Output resource name "{self.name}" type "{self.type}"',
        }


class TFConfigHelper(object):
    """
    The Terraform Execution Helper that helps organize and manage
    things like TF vars that are used to create terraform.tfvars file
    """
    def __init__(self, stack):
        self.classname = 'TFConfigHelper'
        self.logger = Config0Logger(self.classname)
        self.logger.debug(f"Instantiating {self.classname}")

        self.stack = stack
        self.type = self.stack.terraform_type
        self.resource_configs = self.stack.resource_configs
        self.stack.verify_variables()

        self.tf_vars = self.stack.tf_vars if self.stack.get_attr("tf_vars") else {}
        self.config0_resource = Config0Resource(self.stack)

    def _get_tf_configs(self):
        if self.stack.get_attr("cloud_tags_hash"):
            self.tf_vars["cloud_tags"] = {
                "value": json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash)),
                "type": "dict",
                "key": "cloud_tags"
            }

        tf_configs = {
            "tf_runtime": self.stack.tf_runtime,
            "tf_vars": self.tf_vars,
            "resource_configs": {}
        }

        if self.type:
            tf_configs["terraform_type"] = self.type

        keys_to_include = [
            "output_keys",
            "output_prefix_key"
        ]

        for key in keys_to_include:
            if not self.stack.resource_configs.get(key):
                continue
            tf_configs[key] = self.stack.resource_configs[key]

        keys_to_include = [
            "include_raw",
            "include_keys",
            "exclude_keys",
            "maps"
        ]

        for key in keys_to_include:
            if not self.stack.resource_configs.get(key):
                continue
            tf_configs["resource_configs"][key] = self.stack.resource_configs[key]

        self._add_provider_maps(tf_configs)

        return tf_configs

    def _add_provider_maps(self, tf_configs):
        if self.stack.get_attr("provider") == "aws":
            try:
                tf_configs["resource_configs"]["maps"] = {
                    "region": "aws_default_region"
                }
            except Exception:
                self.logger.debug("could not add map keys for aws")

        if self.stack.get_attr("provider") == "do":
            try:
                tf_configs["resource_configs"]["maps"] = {
                    "region": "do_region"
                }
            except Exception:
                self.logger.debug("could not add map keys for do")

    def _add_cloudprovider(self):
        # add cloud provider specific regions
        if self.config0_resource.values.get("aws_default_region"):
            self.config0_resource.values["region"] = self.config0_resource.values["aws_default_region"]
        elif self.config0_resource.values.get("do_region"):
            self.config0_resource.values["region"] = self.config0_resource.values["do_region"]

    def _get_config0_resource_exec_settings(self):
        self._add_cloudprovider()

        _settings = {
            "tf_runtime_settings_hash": self.stack.b64_encode({
                "env_vars": self.config0_resource.tfrun_exec.env_vars,
                "tf_configs": self._get_tf_configs()  # terraform variables and other settings
            }),  # runtime: e.g. Codebuild/Lambda
            "resource_runtime_settings_hash": self.stack.b64_encode({
                "env_vars": self.config0_resource.env_vars,
                "provider": self.config0_resource.provider,  # provider e.g. aws, config0, do
                "type": self.config0_resource.type,  # resource_type e.g. server, rds, load balancer
                "values": self.config0_resource.values
            })   # when executing config0 resource
        }

        if os.environ.get("DEBUG_STACK"):
            print_json(_settings)

        return _settings

    def get_execgroup_inputargs(self):
        # add the main env var
        _settings = self._get_config0_resource_exec_settings()
        self.config0_resource.env_vars["CONFIG0_RESOURCE_EXEC_SETTINGS_HASH"] = self.stack.b64_encode(_settings)

        return self.config0_resource.get_inputargs()

    def get_output_inputargs(self):
        return self.config0_resource.get_output_inputargs()


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_required(key="provider",
                             types="str")

    stack.parse.add_required(key="execgroup_ref",
                             types="str")

    stack.parse.add_required(key="resource_name",
                             types="str")

    stack.parse.add_required(key="resource_type",
                             types="str")

    stack.parse.add_required(key="resource_configs_hash",
                             types="str")

    stack.parse.add_optional(key="terraform_type",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="tf_vars_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_id",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="runtime_env_vars",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="timeout",
                             default=1650,
                             types="int")

    stack.parse.add_optional(key="cloud_tags_hash",
                             default='null',
                             types="str")

    stack.parse.add_optional(key="stateful_id",
                             default="_random",
                             types="str")

    stack.parse.add_optional(key="remote_stateful_bucket",
                             tags="resource,docker",
                             default="null",
                             types="str,null")

    stack.parse.add_optional(key="publish_to_saas",
                             default="true",
                             types="bool")

    stack.parse.add_optional(key="tf_runtime",
                             default="tofu:1.9.1",
                             types="str")

    stack.parse.add_optional(key="iac_ci_pr_strategy",
                             default="branch",
                             choices=["branch", "folder"],
                             types="str")

    stack.parse.add_optional(key="drift_protection",
                             default=True,
                             types="bool,str")

    stack.parse.add_optional(key="ssm_name",
                             tags="resource,docker",
                             types="str")

    # publish_resource -> output_resource_to_ui
    stack.add_substack('config0-publish:::output_resource_to_ui')

    # this will write the tf files to specific gitops repository
    stack.add_substack('config0-publish:::setup_iac_ci_on_github')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # add the execgroup
    stack.add_execgroup(stack.execgroup_ref,
                        "cloud_resource")

    stack.reset_execgroups()

    # terraform variables
    if stack.get_attr("tf_vars_hash"):
        stack.set_variable("tf_vars",
                           stack.b64_decode(stack.tf_vars_hash))

    # terraform executor runtime environment variables
    # e.g. Codebuild, Lambda, Docker Container
    if stack.get_attr("runtime_env_vars_hash"):
        stack.set_variable("runtime_env_vars",
                           stack.b64_decode(stack.runtime_env_vars_hash))

    # configures config0 resource db
    # e.g. values, env_vars, query keys, add_keys, exclude_keys, maps, etc.
    stack.set_variable("resource_configs",
                       stack.b64_decode(stack.resource_configs_hash))

    tfconfig = TFConfigHelper(stack)
    inputargs = tfconfig.get_execgroup_inputargs()
    stack.cloud_resource.insert(**inputargs)

    if stack.get_attr("publish_to_saas") and tfconfig.config0_resource.output_keys:
        output_inputargs = tfconfig.get_output_inputargs()
        stack.output_resource_to_ui.insert(display=True,
                                           **output_inputargs)

    # determine whether we need to setup iac ci
    if not stack.inputvars.get("iac_ci_repo"):
        return stack.get_results()

    arguments = {
        "stateful_id": stack.stateful_id,
        "resource_type": stack.resource_type,
        "iac_ci_pr_strategy": stack.iac_ci_pr_strategy
    }

    # only really tested for github, but
    # will expand to bitbucket and gitlab
    if stack.inputvars.get("iac_ci_repo_provider", "github") == "github":
        human_description = f'IAC CI Gitops setup stateful_id "{stack.stateful_id}"'

        inputargs = {"arguments": arguments,
                     "automation_phase": "continuous_delivery",
                     "human_description": human_description}

        stack.setup_iac_ci_on_github.insert(**inputargs)

    return stack.get_results()