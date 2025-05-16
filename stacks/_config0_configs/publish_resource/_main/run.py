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

    import copy

    stack = newStack(stackargs)

    stack.parse.add_required(key="resource_type", 
                             default="null")

    stack.parse.add_optional(key="name", 
                             default="null")

    stack.parse.add_optional(key="ref_schedule_id", 
                             default="null")

    stack.parse.add_optional(key="labels_hash", 
                             default="null")

    # keys in the resource to publish in base64
    stack.parse.add_optional(key="publish_keys_hash", 
                             default="null")

    # map keys b64 (dict) is use to change the key name that shows up on the UI
    stack.parse.add_optional(key="map_keys_hash", 
                             default="null")

    # prefix is prefix for each key
    stack.parse.add_optional(key="prefix_key", 
                             default="null")

    # Initialize Variables in stack
    stack.init_variables()

    match = {"resource_type": stack.resource_type}

    if stack.get_attr("name"):
        match["name"] = stack.name

    if stack.get_attr("ref_schedule_id"):
        match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("labels_hash"):
        for _key, value in stack.b64_decode(stack.labels_hash).items():
            key = f"label-{_key}"
            match[key] = value

    match["must_be_one"] = True
    resource_info = list(stack.get_resource(**match))

    data = None

    if isinstance(resource_info, list):
        data = resource_info[0]
    elif isinstance(resource_info, dict):
        data = resource_info

    if not data:
        raise Exception(f"resource not found for match {match}")

    if stack.get_attr("publish_keys_hash"):
        resource = stack.keys_to_dict(stack.b64_decode(stack.publish_keys_hash),
                                      {}, 
                                      data)
    else:
        resource = data

    if not resource:
        stack.logger.warn("resource to publish is empty")
        return stack.get_results()

    copied_dict = copy.deepcopy(resource)

    if stack.get_attr("map_keys_hash"):
        resource = stack.keys_to_dict(stack.b64_decode(stack.publish_keys_hash),
                                      {}, 
                                      data)
    else:
        resource = data

    if not resource:
        stack.logger.warn("resource to publish is empty")
        return stack.get_results()

    copied_dict = copy.deepcopy(resource)

    if stack.get_attr("map_keys_hash"):
        for _key, _map_key in stack.b64_decode(stack.map_keys_hash).items():
            if _key not in resource:
                continue

            resource[_map_key] = copied_dict[_key]
            del resource[_key]

    if stack.get_attr("prefix_key"):
        for _key, _value in copied_dict.items():
            resource[f"{stack.prefix_key}/{_key}"] = _value
            del resource[_key]

    stack.output_to_ui(resource)

    return stack.get_results()
