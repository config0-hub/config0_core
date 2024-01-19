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

class RunCommon(object):

    '''
    some common methods to be inherited
    '''

    def __init__(self,stack):
        self.classname = "RunCommon"
        self.stack = stack
        self.env_vars = []
        self.get_common_env_vars()

    def get_common_env_vars(self):

        self.env_vars["STATEFUL_ID"] = self.stack.stateful_id
        self.env_vars["METHOD"] = "create"

        if self.stack.get_attr("remote_stateful_bucket") not in ["null", None]:
            self.env_vars["REMOTE_STATEFUL_BUCKET"] = self.stack.remote_stateful_bucket

        if self.stack.get_attr("timeout"):
            self.env_vars["TIMEOUT"] = self.stack.timeout


        keys  = {
            "tmp_bucket",
            "log_bucket",
            "app_dir",
            "stateful_id",
            "remote_stateful_bucket",
            "run_share_dir",
            "share_dir"
        }

    # this env vars is for the stack and execgroup execution
    # we need to specify create which will then
    # pass it to the docker container
    ##############################################
    # ref/revisit 543524
    # phases working with tag 0.103
    # but needs more testing
    # phases params in stack
    # if self.phases_params_hash:
    #    self.env_vars["PHASES_PARAMS_HASH"] = self.phases_params_hash  # send to tf resource_wrapper
    ##############################################

    #"build_image",
    #"image_type",
    #"compute_type",
    #"codebuild_basename",

    def validate_env_vars(self,include_num=None):

        if not self.env_vars.items():
            return

        for _key,_value in self.env_vars.items():

            if include_num:
                try:
                    number_value = int(_value)
                except:
                    number_value = None

                if number_value:
                    self.env_vars[_key] = "{}".format(_value)
                    continue

            if _value is True:
                self.env_vars[_key] = "True"
            elif _value is False:
                self.env_vars[_key] = "False"
            elif _value is None:
                self.env_vars[_key] = "None"
    def insert_env_vars(self,env_vars,include_num=None):

        if not env_vars:
            return

        for _key,_value in env_vars.items():

            if _key in self.env_vars:
                continue

            self.env_vars[_key] = _value

        self.validate_env_vars(include_num=include_num)

class TFRuntime(RunCommon):

    '''
    The runtimes include AWS Codebuild, Lambda function, or docker container
    to execute the Terraform/OpenTofu code
    '''

    def __init__(self,**kwargs):

        RunCommon.__init__(self,
                           stack=kwargs['stack'])

        self.docker_runtime = kwargs.get("docker_runtime")

        # ref 4532643623642
        if kwargs.get("runtime_env_vars"):
            self.env_vars.update(kwargs["runtime_env_vars"])
            self.validate_env_vars(include_num=True)

        self.add_aws_runtime()

        self.configs = { "env_vars":self.env_vars }
    def add_aws_runtime(self):

        if self.stack.get_attr("ssm_name"):
            self.env_vars["SSM_NAME"] = self.stack.ssm_name

class Config0Resource(RunCommon):

    '''
    This variables and settings to insert the resource, which
    is typically a cloud infrastructure in the Config0 resource db.
    They include things like query keys, lables, etc that we use
    to interact with Config0 resource db
    '''

    def __init__(self,**kwargs):

        RunCommon.__init__(self,
                           stack=kwargs['stack'])

        # set additional vars
        self.provider = kwargs["provider"]
        self.type = kwargs["resource_type"]
        self.name = kwargs["resource_name"]
        self.tf_vars = kwargs.get("tf_vars")

        # ref/revisit 543524
        #self.phases_params = self.stack.get_attr("phases_params")
        #self.phases_params_hash = self.stack.get_attr("phases_params_hash")

        if kwargs.get("resource_output_keys"):
            self.output_keys = kwargs["resource_output_keys"]

            self.output_keys.extend( [ "remote_stateful_location",
                                       "docker_runtime" ] )

        else:
            self.output_keys = []

        if kwargs.get("resource_prefix_key"):
            self.output_prefix_key = kwargs["resource_output_prefix_key"]
        else:
            self.output_prefix_key = self.name

        if kwargs.get("resource_values"):
            self.values = kwargs["resource_values"]
        else:
            self.values = {}

        if kwargs.get("resource_env_vars"):
            self.env_vars.update(kwargs["resource_env_vars"])
            self.validate_env_vars(include_num=False)

        self.tf_runtime = TFRuntime(**kwargs)
        self._set_base_values()

    def _set_base_values(self):

        self.values["resource_type"] = self.type
        self.values["name"] = self.name
        self.values["provider"] = self.provider
        self.values["docker_runtime"] = self.tf_runtime.docker_runtime

    def get_inputargs(self,env_vars):

        self.insert_env_vars(env_vars)

        human_description = "Creating name {} type {}".format(self.name,
                                                              self.type)
        
        inputargs = {"display": True,
                     "env_vars": json.dumps(self.env_vars),  # self._set_base_values
                     "name": self.name,
                     "human_description": human_description,
                     "stateful_id": self.stack.stateful_id}

        if self.stack.get_attr("ssm_name"):
            inputargs["ssm_name"] = self.stack.ssm_name

        # ref/revisit 543524
        #if self.phases_params:
        #    inputargs["phases_params"] = self.phases_params

        if self.stack.get_attr("remote_stateful_bucket") not in ["null", None]:
            inputargs["remote_stateful_bucket"] = self.stack.remote_stateful_bucket

        if self.stack.get_attr("timeout"):
            inputargs["timeout"] = self.stack.timeout

        inputargs["display_hash"] = self.stack.get_hash_object(inputargs)

        return inputargs

    def get_output_inputargs(self):

        if not self.output_keys:
            return

        overide_values = { "name":self.name,
                           "resource_type":self.type,
                           "ref_schedule_id":self.stack.schedule_id,
                           "publish_keys_hash":self.stack.b64_encode(self.output_keys) }

        if self.output_prefix_key:
            overide_values["prefix_key"] = self.output_prefix_key

        inputargs = {"overide_values": overide_values,
                     "automation_phase": "infrastructure",
                     "human_description": 'Output resource name "{}" type "{}"'.format(self.name,
                                                                                       self.type)}

        return inputargs

class TFConfigScope(object):

    '''
    The Terraform Execution Helper that helps organize and manage
    things like TF vars that are used to create terraform.tfvars file
    '''
    def __init__(self,**kwargs):

        self.classname = 'TFConfigScope'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

        self.stack = kwargs["stack"]
        self.type = kwargs["terraform_type"]
        self.resource_configs = kwargs["resource_configs"]

        self.stack.verify_variables()

        # init vars
        if kwargs.get("tf_vars"):
            self.tf_vars = kwargs["tf_vars"]
        else:
            self.tf_vars = {}

        self.config0_resource = Config0Resource(**kwargs)

    def _get_tf_configs(self):

        if self.stack.get_attr("cloud_tags_hash"):

            self.tf_vars["cloud_tags"] = {
                "value":json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash)),
                "type": "dict",
                "key": "cloud_tags"
            }

        return {
            "tf_vars":self.tf_vars,
            "terraform_type":self.type,
            "resource_configs": self.resource_configs
        }

    def get_config0_config0_resource(self):

        self.config0_resource.tf_runtime.configs["env_vars"]["RESOURCE_TAGS"] = "{},{}".format(self.config0_resource.type,
                                                                                              self.config0_resource.name)

        expression = "self.config0_resource.set_{}()".format(self.config0_resource.provider)

        try:
            exec(expression)
        except:
            self.logger.warn("could not execute {} for the provider".format(expression))

        # ref 4353453246
        _settings = {
            "provider": self.config0_resource.provider,  # provider e.g. aws, config0, do
            "resource_type": self.config0_resource.type,  # resource_type e.g. server, rds, load balancer
            "resource_values": self.config0_resource.values,  # resource values to extend in config0 db
            "runtime": self.config0_resource.tf_runtime.configs,  # runtime setting to extend tf
            "terraform": self._get_tf_configs()  # terraform variables and other settings
        }

        if os.environ.get("DEBUG_STACK"):
            print_json(_settings)

        return self.stack.b64_encode(_settings)

    def get_execgroup_inputargs(self):

        env_vars = { "CONFIG0_RESOURCE_SETTINGS_HASH": self.get_config0_config0_resource() }

        return self.config0_resource.get_inputargs(env_vars=env_vars)

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

    stack.parse.add_required(key="terraform_type",
                             types="str")

    stack.parse.add_optional(key="tf_vars_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_configs_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="runtime_env_vars",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_values_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_env_vars_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_output_keys_hash",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="resource_output_prefix_key",
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
                             types="str,null")

    stack.parse.add_optional(key="publish_to_saas",
                             default="true",
                             types="bool")

    stack.parse.add_optional(key="docker_runtime",
                             default="elasticdev/terraform-run-env:1.3.7",
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

    inputargs = { "docker_runtime":stack.docker_runtime,
                  "provider": stack.provider,
                  "stateful_id": stack.stateful_id,
                  "execgroup_ref": stack.execgroup_ref,
                  "resource_name": stack.resource_name,
                  "resource_type": stack.resource_type,
                  "terraform_type": stack.terraform_type,
                  "stack":stack }

    if stack.get_attr("remote_stateful_bucket") not in ["null", None]:
        inputargs["remote_stateful_bucket"] = stack.remote_stateful_bucket

    if stack.get_attr("ssm_name"):
        inputargs["ssm_name"] = stack.ssm_name

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
        inputargs["tf_vars"] = stack.b64_decode(stack.tf_vars_hash)

    # terraform executor runtime environment variables
    # e.g. Codebuild, Lambda, Docker Container
    if stack.get_attr("runtime_env_vars_hash"):
        inputargs["runtime_env_vars"] = stack.b64_decode(stack.runtime_env_vars)

    # configures config0 resource db
    # e.g. query keys, add_keys, remove_keys, map_keys, etc.
    # testtest456
    if stack.get_attr("resource_configs_hash"):
        inputargs["resource_configs"] = stack.b64_decode(stack.resource_configs_hash)

    # add values to output values from the terraform execution
    # for the Config0 resource db entry
    if stack.get_attr("resource_values_hash"):
        inputargs["resource_values"] = stack.b64_decode(stack.resource_values_hash)

    # env vars to include in the Config0 resource execution
    # that calls tf runtime executor
    if stack.get_attr("resource_env_vars_hash"):
        inputargs["resource_env_vars"] = stack.b64_decode(stack.resource_env_vars_hash)

    # output keys from the resource to display on the UI output section
    if stack.get_attr("resource_output_keys_hash"):
        inputargs["resource_output_keys"] = stack.b64_decode(stack.resource_output_keys_hash)

    # prefix for resource output keys to insert
    if stack.get_attr("resource_output_prefix_key"):
        inputargs["resource_output_prefix_key"] = stack.resource_output_prefix_key

    tfconfig = TFConfigScope(**inputargs)

    exec_inputargs = tfconfig.get_execgroup_inputargs()
    stack.cloud_resource.insert(**exec_inputargs)

    if stack.get_attr("publish_to_saas") and inputargs.get("resource_output_keys"):
        output_inputargs = tfconfig.get_output_inputargs()
        stack.output_resource_to_ui.insert(display=True,
                                           **output_inputargs)

    return stack.get_results()