import os
import json
from config0_publisher.loggerly import Config0Logger
from config0_publisher.utilities import print_json

class RuntimeSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]
        self.docker_runtime = kwargs.get("docker_runtime")

        if kwargs.get("runtime_env_vars"):
            self.env_vars = kwargs["runtime_env_vars"]
            self.to_env_var_value()
        else:
            self.env_vars = {}

        self.env_vars["STATEFUL_ID"] = self.stack.stateful_id

        if self.stack.get_attr("ssm_name"):
            self.env_vars["SSM_NAME"] = self.stack.ssm_name

        self.settings = { "env_vars":self.env_vars }

    def to_env_var_value(self):

        if not self.env_vars.items():
            return

        for _key,_value in self.env_vars.items():

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

    def insert_env_vars(self,env_vars):

        if not env_vars:
            return

        for _key,_value in env_vars.items():

            if _key in self.env_vars:
                continue

            self.env_vars[_key] = _value

        self.to_env_var_value()

class ResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

        # set additional vars
        self.provider = kwargs["provider"]
        self.type = kwargs["resource_type"]
        self.name = kwargs["resource_name"]
        self.tf_vars = kwargs.get("tf_vars")

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
            self.env_vars = kwargs["resource_env_vars"]
            self.to_env_var_value()
        else:
            self.env_vars = {}

        self.runtime_settings = RuntimeSettings(**kwargs)

        self._set_base_values()

    def to_env_var_value(self):

        if not self.env_vars.items():
            return

        for _key,_value in self.env_vars.items():

            if _value is True:
                self.env_vars[_key] = "True"
            elif _value is False:
                self.env_vars[_key] = "False"
            elif _value is None:
                self.env_vars[_key] = "None"

    def insert_env_vars(self,env_vars):

        if not env_vars:
            return

        for _key,_value in env_vars.items():

            if _key in self.env_vars:
                continue

            self.env_vars[_key] = _value

        self.to_env_var_value()

    def _set_base_values(self):

        # this env vars is for the stack and execgroup execution
        # we need to specify create which will then
        # pass it to the docker container

        self.env_vars["METHOD"] = "create"
        self.env_vars["STATEFUL_ID"] = self.stack.stateful_id

        self.values["resource_type"] = self.type
        self.values["name"] = self.name
        self.values["provider"] = self.provider
        self.values["docker_runtime"] = self.runtime_settings.docker_runtime

    def get_inputargs(self,env_vars):

        self.insert_env_vars(env_vars)

        human_description = "Creating name {} type {}".format(self.name,
                                                              self.type)
        
        inputargs = {"display":True}
        inputargs["env_vars"] = json.dumps(self.env_vars)
        inputargs["name"] = self.name
        inputargs["human_description"] = human_description
        inputargs["stateful_id"] = self.stack.stateful_id

        if self.stack.get_attr("ssm_name"):
            inputargs["ssm_name"] = self.stack.ssm_name

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

class TFExecutor(object):

    def __init__(self,**kwargs):

        self.classname = 'TFExecutor'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

        self.stack = kwargs["stack"]
        self.type = kwargs["terraform_type"]
        self.resource_params = kwargs["resource_params"]

        self.stack.verify_variables()

        # init vars
        if kwargs.get("tf_vars"):
            self.tf_vars = kwargs["tf_vars"]
        else:
            self.tf_vars = {}

        self.resource = ResourceSettings(**kwargs)

    def _get_tf_settings(self):

        if self.stack.get_attr("cloud_tags_hash"):

            self.tf_vars["cloud_tags"] = { "value":json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash)), 
                                           "type": "dict",
                                           "key": "cloud_tags" }

        tf_settings = { "tf_vars":self.tf_vars,
                        "terraform_type":self.type,
                        "resource_params": self.resource_params }

        return tf_settings

    def get_config0_resource_settings(self):

        self.resource.runtime_settings.settings["env_vars"]["RESOURCE_TAGS"] = "{},{}".format(self.resource.type, 
                                                                                    self.resource.name)

        expression = "self.resource.set_{}()".format(self.resource.provider)

        try:
            exec(expression)
        except:
            self.logger.warn("could not execute {} for the provider".format(expression))

        # specify the provider e.g. aws, config0, do
        config0_resource_settings = { "provider":self.resource.provider }

        # specify the resource_type e.g. server, rds, load balancer
        config0_resource_settings["resource_type"] = self.resource.type

        # provide the resource values to add
        config0_resource_settings["resource_values"] = self.resource.values

        # specify the docker settings to run terraform
        # testtest333
        # ref 4353453246
        config0_resource_settings["runtime"] = self.resource.runtime_settings.settings

        # specify terraform variables and other settings
        config0_resource_settings["terraform"] = self._get_tf_settings()

        if os.environ.get("DEBUG_STACK"):
            print_json(config0_resource_settings)

        return self.stack.b64_encode(config0_resource_settings)

    def get_execgroup_inputargs(self):

        env_vars = { "CONFIG0_RESOURCE_SETTINGS_HASH": self.get_config0_resource_settings() }

        return self.resource.get_inputargs(env_vars=env_vars)

    def get_output_inputargs(self):

        return self.resource.get_output_inputargs()

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

    stack.parse.add_optional(key="resource_params_hash",
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
                             default=1800,
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

    # publish_resource -> output_resource_to_ui
    stack.add_substack('config0-hub:::output_resource_to_ui')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # add the execgroup
    stack.add_execgroup(stack.execgroup_ref,"cloud_resource")  
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

    if stack.get_attr("tf_vars_hash"):
        inputargs["tf_vars"] = stack.b64_decode(stack.tf_vars_hash)

    if stack.get_attr("resource_params_hash"):
        inputargs["resource_params"] = stack.b64_decode(stack.resource_params_hash)

    if stack.get_attr("runtime_env_vars_hash"):
        inputargs["runtime_env_vars"] = stack.b64_decode(stack.runtime_env_vars)

    if stack.get_attr("resource_values_hash"):
        inputargs["resource_values"] = stack.b64_decode(stack.resource_values_hash)

    if stack.get_attr("resource_env_vars_hash"):
        inputargs["resource_env_vars"] = stack.b64_decode(stack.resource_env_vars_hash)

    if stack.get_attr("resource_output_keys_hash"):
        inputargs["resource_output_keys"] = stack.b64_decode(stack.resource_output_keys_hash)

    if stack.get_attr("resource_output_prefix_key"):
        inputargs["resource_output_prefix_key"] = stack.resource_output_prefix_key

    tfexecutor = TFExecutor(**inputargs)

    exec_inputargs = tfexecutor.get_execgroup_inputargs()
    stack.cloud_resource.insert(**exec_inputargs)

    if stack.get_attr("publish_to_saas") and inputargs.get("resource_output_keys"):
        output_inputargs = tfexecutor.get_output_inputargs()
        stack.output_resource_to_ui.insert(display=True,**output_inputargs)

    return stack.get_results()
