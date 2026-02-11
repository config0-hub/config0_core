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

def run(stackargs):

    stack = newStack(stackargs)

    # Required parameters
    stack.parse.add_required(key="vars_set_name")

    # Optional parameters with defaults
    stack.parse.add_optional(key="env_vars_hash", default='null')
    stack.parse.add_optional(key="labels_hash", default='null')
    stack.parse.add_optional(key="arguments_hash", default='null')
    stack.parse.add_optional(key="evaluate", default='null')

    # Initialize Variables in stack
    stack.init_variables()

    stack.set_variable("_env_vars", {})
    stack.set_variable("_labels", {})
    stack.set_variable("_arguments", {})

    resource = {
        'name': stack.vars_set_name,
        'label': stack.vars_set_name,
        'values': {}
    }

    if stack.get_attr("env_vars_hash"):
        resource["values"]["env_vars"] = stack.b64_decode(stack.env_vars_hash)

    if stack.get_attr("labels_hash"):
        stack.set_variable("_labels",
                           stack.b64_decode(stack.labels_hash))
        resource["values"]["labels"] = stack._labels

    if stack.get_attr("arguments_hash"):
        stack.set_variable("_arguments",
                           stack.b64_decode(stack.arguments_hash))
        resource["values"]["arguments"] = stack._arguments

    if stack.get_attr("_arguments") and stack.get_attr("evaluate"):
        arguments = stack.eval_vars(stack._arguments,
                                    strict=True)
        for _key, _value in arguments.items():
            resource["values"]["arguments"][_key] = _value

    if resource:
        stack.insert_vars_set(values=resource,
                              labels=stack._labels)
        description = f'added a variable set name {stack.vars_set_name}'
    else:
        description = f'failed to add variable set name {stack.vars_set_name}'

    stack.add_external_cmd(cmd="sleep 1",
                           order_type="empty_stack::shellout",
                           human_description=description,
                           display=True,
                           role="external/cli/execute")

    return stack.get_results(stackargs.get("destroy_instance"))