import os
import json
from config0_publisher.loggerly import Config0Logger
from config0_publisher.utilities import print_json

# ref/revisit 543524
#def _get_default_phase_parameters():
#
#    phases_params = {
#         "create": [
#            {
#                "name": "submit",
#                "timewait": None,
#            },
#            {
#                "name": "retrieve",
#                "timewait": 3,
#                "inputargs": {
#                    "interval": 10,
#                    "retries": 12
#                }
#            }
#         ],
#         "destroy": [
#            {
#                "name": "submit",
#                "timewait": None,
#            },
#            {
#                "name": "retrieve",
#                "timewait": 3,
#                "inputargs": {
#                    "interval": 10,
#                    "retries": 12
#                }
#            }
#         ]
#    }
#
#    return phases_params

class CmEnvVars(object):

    '''
    some common methods to be inherited
    '''

    def __init__(self,stack):

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
            "METHOD",
            "CONFIG0_RESOURCE_JSON_FILE",
            "CONFIG0_PHASES_JSON_FILE",
            "PHASES_PARAMS_HASH",
            "SCHEDULE_ID",
            "RUN_ID",
            "JOB_INSTANCE_ID",
            "TIMEOUT"
        ]

        self.standard_codebuild_keys = [
            "BUILD_TIMEOUT",
            "BUILD_IMAGE",
            "COMPUTE_TYPE",
            "IMAGE_TYPE",
            "CODEBUILD_BASENAME"
            ]

        self.standard_lambda_keys = [
            "BUILD_TIMEOUT"
            ]

        self.env_vars = {}

    def _default(self):

        return {
            "TIMEOUT": "600"
        }

    def _default_codebuild(self):

        return {
            "AWS_REGION": "us-east-1",
            "BUILD_IMAGE": "aws/codebuild/standard:4.0",
            "COMPUTE_TYPE": "BUILD_GENERAL1_SMALL",
            "IMAGE_TYPE": "LINUX_CONTAINER",
            "CODEBUILD_BASENAME":"config0-iac",
            "BUILDSPEC_FILE": "buildspec.yml"
        }

    def _default_lambda(self):

        return {
            "AWS_REGION": "us-east-1",
            "LAMBDA_FUNCTION_NAME": "config0-iac"
        }

    def add(self,keys,default_values=None,clobber=False):

        for key in keys:

            if key in self.env_vars and not clobber:
                continue

            if self.stack.get_attr(key.lower()):
                self.env_vars[key] = self.stack.get_attr(key.lower())
            elif os.environ.get(key):
                self.env_vars[key] = os.environ[key]
            elif key in default_values:
                self.env_vars[key] = default_values[key]

    def set_lambda(self,reset=False):

        if reset:
            self.reset()
        self.add(self.standard_lambda_keys,
                 self._default_lambda())
    def set_codebuild(self,reset=False):

        if reset:
            self.reset()
        self.add(self.standard_codebuild_keys,
                 self._default_codebuild())

        if "BUILD_TIMEOUT" not in self.env_vars:
            try:
               self.env_vars["BUILD_TIMEOUT"] = str(int(self.env_vars["TIMEOUT"]) - 60)
            except:
               self.env_vars["BUILD_TIMEOUT"] = self.env_vars["TIMEOUT"]

    def set_resource(self,reset=False):

        if reset:
            self.reset()

        try:
            env_vars = self.stack.resource_configs["env_vars"]
        except:
            env_vars = {}

        # testtest456
        self.stack.logger.debug("0"*32)
        self.stack.logger.debug(env_vars)
        self.stack.logger.debug(type(env_vars))

        self.update(env_vars)

    def update(self,env_vars=None):

        if not env_vars:
            return

        for key,value in env_vars.items():
            if key.upper() in self.env_vars:
                continue
            self.env_vars[key.upper()] = value

    def set_common(self,reset=False):

        if reset:
            self.reset()

        self.add(self.common_keys,
                 self._default())

    def set_all(self,reset=False):

        if reset:
            self.reset()

        self.set_resource()
        self.set_common()
        self.set_codebuild()
        self.set_lambda()
        self.validate()

    def reset(self):
        self.env_vars = {}

    def validate(self,env_vars=None,include_num=None):

        if not env_vars:
            env_vars = self.env_vars

        for _key,_value in env_vars.items():

            if include_num:
                try:
                    number_value = int(_value)
                except:
                    number_value = None

                if number_value:
                    env_vars[_key] = "{}".format(_value)
                    continue

            if _value is True:
                env_vars[_key] = "True"
            elif _value is False:
                env_vars[_key] = "False"
            elif _value is None:
                env_vars[_key] = "None"

    def insert(self,env_vars=None,add_env_vars=None,include_num=None):

        # this env vars is for the stack and execgroup execution
        # we need to specify create which will then

        if not add_env_vars:
            return

        if not env_vars:
            env_vars = self.env_vars

        for _key,_value in add_env_vars.items():

            if _key in env_vars:
                continue

            env_vars[_key] = _value

        self.validate(env_vars,
                      include_num=include_num)

class TFRuntime(object):

    '''
    The runtimes include AWS Codebuild, Lambda function, or docker container
    to execute the Terraform/OpenTofu code
    '''

    def __init__(self,stack):

        self.stack = stack

        self.cmvars = CmEnvVars(stack=stack)
        self.cmvars.set_common()
        self.cmvars.set_lambda()
        self.cmvars.set_codebuild()
        self.env_vars = self.cmvars.env_vars

        # ref 4532643623642
        if self.stack.get_attr("runtime_env_vars"):

            # testtest456
            self.stack.logger.debug("1" * 32)
            self.stack.logger.debug(self.stack.get_attr("runtime_env_vars"))
            self.stack.logger.debug(type(self.stack.get_attr("runtime_env_vars")))

            self.env_vars.update(self.stack.runtime_env_vars)

        # cloud specific variables storage
        self._add_aws_runtime()
        self._set_misc()

        self.cmvars.validate(self.env_vars,
                             include_num=True)

    def _add_aws_runtime(self):

        if not self.stack.get_attr("ssm_name"):
            return

        self.env_vars["SSM_NAME"] = self.stack.ssm_name

    def _set_misc(self):

        #self.docker_runtime = self.stack.docker_runtime

        self.env_vars["RESOURCE_TAGS"] = "{},{}".format(self.stack.resource_type,
                                                        self.stack.resource_name)

class Config0Resource(object):

    '''
    This variables and settings to insert the resource, which
    is typically a cloud infrastructure in the Config0 resource db.
    They include things like query keys, lables, etc that we use
    to interact with Config0 resource db
    '''

    def __init__(self,stack):

        self.stack = stack

        # set additional vars
        self.provider = stack.provider
        self.type = stack.resource_type
        self.name = stack.resource_name

        # ref/revisit 543524
        #self.phases_params = self.stack.get_attr("phases_params")
        #self.phases_params_hash = self.stack.get_attr("phases_params_hash")

        self._parse_resource_configs()
        self._set_env_vars()
        self._set_base_values()

        self.tf_runtime = TFRuntime(self.stack)

    def _parse_resource_configs(self):

        resource_configs = self.stack.resource_configs

        if resource_configs.get("output_keys"):
            self.output_keys = resource_configs["output_keys"]
        else:
            self.output_keys = []

        self.output_keys.extend([
            "remote_stateful_location",
            "docker_runtime"]
        )

        if resource_configs.get("output_prefix_key"):
            self.output_prefix_key = resource_configs["output_prefix_key"]
        else:
            self.output_prefix_key = self.name

        if resource_configs.get("values"):
            self.values = resource_configs["values"]
        else:
            self.values = {}

        # this is include in cmvars -> set_resource
        #try:
        #    self.env_vars = self.stack.resource_configs["env_vars"]
        #except:
        #    self.env_vars = {}

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
        self.values["docker_runtime"] = self.stack.docker_runtime

    def get_inputargs(self):

        human_description = "Creating name {} type {}".format(self.name,
                                                              self.type)

        inputargs = {
            "display": True,
            "env_vars": json.dumps(self.env_vars),
            "name": self.name,
            "human_description": human_description,
            "stateful_id": self.stack.stateful_id
        }

        if self.stack.get_attr("ssm_name"):
            inputargs["ssm_name"] = self.stack.ssm_name

        # ref/revisit 543524
        #if self.phases_params:
        #    inputargs["phases_params"] = self.phases_params

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
            "name":self.name,
            "resource_type":self.type,
            "ref_schedule_id":self.stack.schedule_id,
            "publish_keys_hash":self.stack.b64_encode(self.output_keys)
        }

        if self.output_prefix_key:
            overide_values["prefix_key"] = self.output_prefix_key

        return {
            "overide_values": overide_values,
            "automation_phase": "infrastructure",
            "human_description": 'Output resource name "{}" type "{}"'.format(self.name,
                                                                              self.type)
        }

class TFConfigHelper(object):

    '''
    The Terraform Execution Helper that helps organize and manage
    things like TF vars that are used to create terraform.tfvars file
    '''
    def __init__(self,stack):

        self.classname = 'TFConfigHelper'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

        self.stack = stack
        self.type = self.stack.terraform_type
        self.resource_configs = self.stack.resource_configs
        self.tf_version = self.stack.tf_version

        self.stack.verify_variables()

        if self.stack.get_attr("tf_vars"):
            self.tf_vars = self.stack.tf_vars
        else:
            self.tf_vars = {}

        self.config0_resource = Config0Resource(self.stack)

    def _get_tf_configs(self):

        if self.stack.get_attr("cloud_tags_hash"):
            self.tf_vars["cloud_tags"] = {
                "value":json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash)),
                "type": "dict",
                "key": "cloud_tags"
            }

        tf_configs = {
            "tf_vars":self.tf_vars,
            "tf_version": self.tf_version,
            "terraform_type":self.type,
            "resource_configs":{}
        }

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
            "map_keys"
        ]

        for key in keys_to_include:
            if not self.stack.resource_configs.get(key):
                continue
            tf_configs["resource_configs"][key] = self.stack.resource_configs[key]

        return tf_configs

    def get_config0_resource(self):

        cmv_env_vars = CmEnvVars(self.stack)
        cmv_env_vars.set_common()

        # testtest456
        # add drift detection
        _settings = {
            "common_exec_hash": self.stack.b64_encode({
                "env_vars":cmv_env_vars.env_vars
            }),  # common env vars
            "runtime_exec_hash": self.stack.b64_encode({
                "env_vars":self.config0_resource.tf_runtime.env_vars,
                "exec_runtime": self.stack.exec_runtime,
                "tf_configs": self._get_tf_configs()  # terraform variables and other settings
            }),  # runtime: e.g. Codebuild/Lambda
            "resource_exec_hash": self.stack.b64_encode({
                "env_vars":self.config0_resource.env_vars,
                "method":self.config0_resource.env_vars["METHOD"],
                "provider":self.config0_resource.provider,  # provider e.g. aws, config0, do
                "type": self.config0_resource.type,  # resource_type e.g. server, rds, load balancer
                "values": self.config0_resource.values
            })   # when executing config0 resource
        }

        if os.environ.get("DEBUG_STACK"):
            print_json(_settings)

        return self.stack.b64_encode(_settings)

    def get_execgroup_inputargs(self):
        # add the main env var
        self.config0_resource.env_vars["CONFIG0_RESOURCE_SETTINGS_HASH"] = self.get_config0_resource()
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

    #stack.parse.add_optional(key="resource_values_hash",
    #                         default="null",
    #                         types="str")

    #stack.parse.add_optional(key="resource_env_vars_hash",
    #                         default="null",
    #                         types="str")

    #stack.parse.add_optional(key="resource_output_keys_hash",
    #                         default="null",
    #                         types="str")

    #stack.parse.add_optional(key="resource_output_prefix_key",
    #                         default="null",
    #                         types="str")

    stack.parse.add_required(key="terraform_type",
                             types="str")

    stack.parse.add_optional(key="tf_vars_hash",
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

    stack.parse.add_optional(key="docker_runtime",
                             default="elasticdev/terraform-run-env:1.3.7",
                             types="str")

    stack.parse.add_optional(key="tf_version",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="exec_runtime",
                             default="null",
                             choices=["None,"
                                      "codebuild",
                                      "lambda"],
                             types="str")

    stack.parse.add_optional(key="ssm_name",
                             tags="resource,docker",
                             types="str")

    # ref/revisit 543524
    #stack.parse.add_optional(key="phases_params_hash",
    #                         tags="resource,docker",
    #                         types="str")

    # publish_resource -> output_resource_to_ui
    stack.add_substack('config0-publish:::output_resource_to_ui')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # add the execgroup
    stack.add_execgroup(stack.execgroup_ref,
                        "cloud_resource")

    stack.reset_execgroups()

    ############################################################################################
    # ref/revisit 543524
    #stack.set_variable("phases_params", _get_default_phase_parameters())
    #stack.set_variable("phases_params_hash", stack.b64_encode(stack.phases_params))
    #if stack.get_attr("phases_params_hash"):
    #    stack.set_variable("phases_params", stack.b64_decode(stack.phases_params_hash))
    #    inputargs["phases_params"] = stack.phases_params
    #else:
    #    stack.set_variable("phases_params", None)
    #    stack.set_variable("phases_params_hash", None)
    ############################################################################################

    # terraform variables
    if stack.get_attr("tf_vars_hash"):
        stack.set_variable("tf_vars",
                           stack.b64_decode(stack.tf_vars_hash))

    if not stack.get_attr("tf_version"):
        try:
            tf_version = stack.docker_runtime.split(":")[-1]
        except:
            tf_version = "1.5.4"

        stack.set_variable("tf_version",
                           tf_version)

    # terraform executor runtime environment variables
    # e.g. Codebuild, Lambda, Docker Container
    if stack.get_attr("runtime_env_vars_hash"):
        stack.set_variable("runtime_env_vars",
                           stack.b64_decode(stack.runtime_env_vars_hash))

    # configures config0 resource db
    # e.g. values, env_vars, query keys, add_keys, remove_keys, map_keys, etc.
    stack.set_variable("resource_configs",
                       stack.b64_decode(stack.resource_configs_hash))

    tfconfig = TFConfigHelper(stack)
    inputargs = tfconfig.get_execgroup_inputargs()
    stack.cloud_resource.insert(**inputargs)

    if stack.get_attr("publish_to_saas") and tfconfig.output_keys:
        output_inputargs = tfconfig.get_output_inputargs()
        stack.output_resource_to_ui.insert(display=True,
                                           **output_inputargs)

    return stack.get_results()