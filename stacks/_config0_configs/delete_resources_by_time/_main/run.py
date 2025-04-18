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

def sorted_keystr(items, key, reverse=None):
    """Sort items by string representation of a specific key."""
    from operator import itemgetter

    key_str = f"_tmp_sort_{str(key)}-str"

    for item in items:
        item[key_str] = str(item[key])

    new_items = sorted(items,
                       key=itemgetter(key_str),
                       reverse=reverse)

    for new_item in new_items:
        del new_item[key_str]

    return new_items


def _get_delete_resources(stack, keep_resource_ids=None):
    """Get resources to delete, excluding those in keep_resource_ids."""
    parallel_overides = []
    parallel_resources = []
    sequentialize_resources = []
    added_ids = []

    ref_schedule_ids = stack.to_list(stack.ref_schedule_ids)

    for ref_schedule_id in ref_schedule_ids:
        _resources = stack.get_resource(ref_schedule_id=ref_schedule_id)

        if not _resources:
            continue

        for _resource in _resources:
            _id = _resource["_id"]
            if _id in added_ids:
                continue
            if keep_resource_ids and _id in keep_resource_ids:
                continue
            added_ids.append(_id)

            if _resource.get("query_only") or _resource.get("parent"):
                parallel_resources.append(_resource)
                continue

            try:
                _resource["checkin"] = int(_resource["checkin"])
            except:
                # just set it to pass so it gets added last
                _resource["checkin"] = 1000000000

            sequentialize_resources.append(_resource)

    stack.logger.debug(f"parallel_resources ids {[_r['_id'] for _r in parallel_resources]}")
    stack.logger.debug(f"sequentialize_resources ids {[_r['_id'] for _r in sequentialize_resources]}")

    if parallel_resources:
        parallel_overides.extend(parallel_resources)
    if sequentialize_resources:
        parallel_overides.extend(sequentialize_resources)

    results = {
        "parallel_resources": parallel_resources,
        "parallel_overides": parallel_overides,
        "sequentialize_resources": sorted_keystr(sequentialize_resources,
                                                key="checkin",
                                                reverse=True),
        "added_ids": added_ids
    }

    return results


def _get_keep_resources(stack):
    """Gather IDs for resources to keep."""
    # Gather the id for the keep resources
    if not stack.get_attr("keep_resources"):
        return

    _resources = stack.to_json(stack.keep_resources)
    stack.logger.debug(f"keep resources first include {_resources}")

    _resource_ids = []

    for _resource in _resources:
        for ref_schedule_id in stack.ref_schedule_ids:
            _resource["ref_schedule_id"] = ref_schedule_id
            stack.logger.debug(f"searching for keep resource {_resource}")
            resources = stack.get_resource(**_resource)
            if not resources:
                continue

            for resource in resources:
                stack.logger.debug(f"keep resource id {resource['_id']}")
                _resource_ids.append(resource["_id"])

    stack.logger.debug(f"keep resource ids {_resource_ids}")

    return _resource_ids


def run(stackargs):
    """Main function to process stack arguments and manage resources."""
    stack = newStack(stackargs)

    # required stack args
    stack.parse.add_required(key="keep_resources",
                             default="null")

    stack.parse.add_required(key="ref_schedule_ids")

    stack.parse.add_optional(key="parallel_overide",
                             default="null")

    # Initialize Variables in stack
    stack.init_variables()

    keep_resource_ids = _get_keep_resources(stack)

    all_resources = _get_delete_resources(stack,
                                          keep_resource_ids=keep_resource_ids)

    stack.set_parallel()

    # parallel overide set True
    if stack.get_attr("parallel_overide") and all_resources.get("parallel_overides"):
        stack.logger.debug("Parallel overide set True")
        stack.logger.debug("Executing destroy resources in parallel")

        for resource in all_resources["parallel_overides"]:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        return stack.get_results(None)

    # parallel and sequential
    if all_resources.get("parallel_resources"):
        for resource in all_resources["parallel_resources"]:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)

    # Set unset_parallel
    stack.unset_parallel()

    # Wait until all actions complete
    stack.wait_all()

    for resource in all_resources["sequentialize_resources"]:
        stack.logger.debug(f"removing resource {resource}")
        stack.remove_resource(**resource)

    return stack.get_results(None)