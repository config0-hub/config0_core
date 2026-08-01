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

from config0_stack_runtime.resource_record import classify_delete_mode

# A recorded infrastructure teardown transports ONLY the row id. The CLI reads
# the immutable execution asset, merged mod_params/destroy_params, and tfstate
# pointer from that QHost row. Passing any asset here would permit the caller to
# destroy with a version other than the one that created the resource.
_TEARDOWN_KEYS = ("_id",)

# The record-only delete transports the row identity plus every state-pointer
# key, and nothing else: unrecord_resource's intake is closed to exactly these,
# so a projection that drifts raises instead of silently deleting.
_RECORD_DELETE_KEYS = (
    "_id",
    "resource_id",
    "stateful_id",
    "remote_stateful_location",
    "remote_stateful_bucket",
)


def _project(resource, keys):
    """Project one matched row onto *keys*, dropping unset values."""
    return {key: resource[key] for key in keys if resource.get(key) is not None}


def _teardown_projection(resource):
    """Project the matched row to its id-only immutable destroy request."""
    projected = _project(resource, _TEARDOWN_KEYS)
    if not projected.get("_id"):
        raise ValueError("state-backed resource teardown requires the recorded _id")
    return projected


def _dispatch_delete(stack, resource):
    """Route the matched row to its delete path — a full if/elif/else that raises.

    The split is the runtime's own named classifier, so this boundary and the
    unrecord_resource helper boundary can never disagree on the same row.
    """
    mode = classify_delete_mode(resource)

    if mode == "teardown":
        return stack.remove_resource(**_teardown_projection(resource))
    elif mode == "record":
        return stack.unrecord_resource(**_project(resource, _RECORD_DELETE_KEYS))
    else:
        raise ValueError(f"unknown delete mode {mode}")


def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_optional(key="db_id", default="null")
    stack.parse.add_optional(key="resource_type", default="null")
    stack.parse.add_optional(key="name", default="null")
    stack.parse.add_optional(key="hostname", default="null")
    stack.parse.add_optional(key="ref_schedule_id", default="null")
    stack.parse.add_optional(key="must_exists", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    _destroy_match = {}

    if stack.get_attr("db_id"):
        _destroy_match["_id"] = stack.db_id

    if stack.get_attr("hostname"):
        _destroy_match["hostname"] = stack.hostname

    if stack.get_attr("name"):
        _destroy_match["name"] = stack.name

    if stack.get_attr("ref_schedule_id"):
        _destroy_match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("resource_type"):
        _destroy_match["resource_type"] = stack.resource_type

    if stack.get_attr("must_exists"):
        _destroy_match["must_exists"] = True

    if not _destroy_match:
        error_msg = "match for destroy resource cannot be wide open"
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    _dinputargs = stack.get_resource(**_destroy_match)

    if _dinputargs and len(_dinputargs) == 1:
        _dispatch_delete(stack, _dinputargs[0])
    elif _dinputargs and len(_dinputargs) > 1:
        error_msg = f"More than resource found for {_destroy_match}"
        raise Exception(error_msg)

    return stack.get_results()
