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

    import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="resource_type",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="name",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="match_hash",
                             types="str",
                             default="null")  # match hash in base64

    stack.parse.add_optional(key="ref_schedule_id",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="labels_hash",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="publish_keys_hash",
                             types="str",
                             default="null")  # keys in the resource to publish in base64

    stack.parse.add_optional(key="map_keys_hash",
                             types="str",
                             default="null")  # map keys b64 (dict) is use to change the key name that shows up on the UI

    stack.parse.add_optional(key="prefix_key",
                             types="str",
                             default="null")  # prefix is prefix for each key

    # Initialize Variables in stack
    stack.init_variables()

    if stack.get_attr("match_hash"):
        match = stack.b64_decode(stack.match_hash)
    else:
        match = {"resource_type": stack.resource_type}

        if stack.get_attr("name"):
            match["name"] = stack.name

        if stack.get_attr("ref_schedule_id"):
            match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("labels_hash"):
        for _key, value in stack.b64_decode(stack.labels_hash).items():
            key = f"label-{_key}"
            match[key] = value

    resource_info = list(stack.get_resource(match=match,
                                           must_be_one=True))

    data = None

    if isinstance(resource_info, list):
        data = resource_info[0]
    elif isinstance(resource_info, dict):
        data = resource_info

    if not data:
        raise Exception(f"resource not found for match {match}")

    resource = data

    if stack.get_attr("publish_keys_hash"):
        keys2pass = stack.b64_decode(stack.publish_keys_hash)
        resource = {}

        for _key in keys2pass:
            if not data.get(_key):
                continue

            if isinstance(data[_key], list):
                try:
                    _value = ",".join(data[_key])
                except:
                    _value = data[_key]
            elif isinstance(data[_key], dict):
                try:
                    _value = json.dumps(data[_key])
                except:
                    _value = data[_key]
            else:
                _value = data[_key]

            resource[_key] = _value

    if not resource:
        stack.logger.warn("resource to publish is empty")
        return stack.get_results()

    if stack.get_attr("map_keys_hash"):
        for _key, _map_key in stack.b64_decode(stack.map_keys_hash).items():
            if _key not in resource:
                continue

            value = resource[_key]
            del resource[_key]
            resource[_map_key] = value

    # add prefix if necessary
    if stack.get_attr("prefix_key"):
        _changes = []

        for _key, _value in resource.items():
            _changes.append({"new_key": f"{stack.prefix_key}/{_key}",
                            "old_key": _key,
                            "value": _value})

        for _change in _changes:
            del resource[_change["old_key"]]
            resource[_change["new_key"]] = _change["value"]

    stack.output_to_ui(resource)

    return stack.get_results()
