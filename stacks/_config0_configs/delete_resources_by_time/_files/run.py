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

from datetime import datetime

# A recorded infrastructure teardown transports ONLY the row id. The CLI reads
# the immutable execution asset, merged mod_params/destroy_params, and tfstate
# pointer from that QHost row. Passing an asset here would let caller state drift
# away from the exact version that created the resource.
_TEARDOWN_KEYS = ("_id",)


def _teardown_projection(resource):
    """Project one recorded resource to its id-only immutable destroy request."""
    projected = {
        key: resource[key]
        for key in _TEARDOWN_KEYS
        if resource.get(key) is not None
    }
    if not projected.get("_id"):
        raise ValueError("state-backed resource teardown requires the recorded _id")
    return projected


def _get_keep_resources(stack):
    """Collect the _ids of resources the project explicitly retains.

    Each keep entry is a match dict (provider / resource_type / name /
    hostname) applied per target schedule id; every matching record's _id
    joins the exclusion set. keep_resources arrives as a real list — no
    deserialization step.
    """
    if not stack.get_attr("keep_resources"):
        return None

    _resource_ids = []

    for _keep_entry in stack.keep_resources:
        for ref_schedule_id in stack.to_list(stack.ref_schedule_ids):
            match = dict(_keep_entry)
            match["ref_schedule_id"] = ref_schedule_id
            stack.logger.debug(f"searching for keep resource {match}")
            resources = stack.get_resource(**match, overlay_tfstate=False)
            if not resources:
                continue
            for resource in resources:
                stack.logger.debug(f"keep resource id {resource['_id']}")
                _resource_ids.append(resource["_id"])

    stack.logger.debug(f"keep resource ids {_resource_ids}")
    return _resource_ids


_STATE_POINTER_KEYS = ("stateful_id",
                       "remote_stateful_location",
                       "remote_stateful_bucket")


def _has_state_pointer(resource):
    """A row carrying any state pointer is real infrastructure."""
    return any(resource.get(key) not in (None, "", "null", "None")
               for key in _STATE_POINTER_KEYS)


def _created_at_sort_key(resource):
    """Parse the rewrite resource row's authoritative creation timestamp."""
    return datetime.fromisoformat(resource["created_at"])


def _get_delete_resources(stack, keep_resource_ids=None):
    """Gather EVERY matched row per target schedule id - no row left behind.

    Every matched row of every resource_type per schedule id is classified:

    - a row carrying a state pointer is real infrastructure → an
      execution-backed ``remove_resource`` teardown order;
    - a record-only row (schedule_vars, job_vars, selectors, labels,
      reference, vars_set) has nothing to run. It is the destroy's own
      argument base and retry evidence (the addon destroy plan reads the
      install's ``schedule_vars`` row; a project destroy re-reads its rows),
      so it must outlive a FAILED destroy. It is collected here and unrecorded
      LAST, after every teardown order has settled (defect 45: deleting them
      at order-emit time consumed the base before the first teardown order
      ran, so a failed destroy could never be retried). The SaaS
      ``run_complete`` by-project sweep remains the primary backstop, gated on
      a COMPLETED destroy; the stack's trailing unrecord is the second safety.

    Teardown candidates are deduplicated by _id and filtered by the keep
    exclusion, then split into the original's two tiers
    (``_main/run.py:37-89``):

    - the PARALLEL tier: rows flagged ``query_only`` or ``parent`` —
      independent resources torn down concurrently;
    - the SEQUENTIAL tier: everything else, in reverse ``created_at`` order
      (newest first). This is the dependency-safe removal order where
      resources depend on one another. A missing or invalid timestamp raises.

    Returns ``(parallel_requests, sequential_requests, record_only_requests)``.
    The record-only requests are id-only projections, sorted by ``_id`` for a
    deterministic trailing unrecord step.
    """
    added_ids = []
    parallel_candidates = []
    sequential_candidates = []
    record_only_candidates = []
    matched_row_count = 0

    # A destroy enumerates the STORED rows: the teardown order carries only the
    # _id and the CLI reads the frozen state pointer off the row. Never overlay
    # here - a read-time overlay aborts the whole list on any row whose
    # artifacts it cannot reach, and then nothing can be torn down.
    for ref_schedule_id in stack.to_list(stack.ref_schedule_ids):
        _resources = stack.get_resource(ref_schedule_id=ref_schedule_id,
                                        overlay_tfstate=False)

        if not _resources:
            continue

        matched_row_count += len(_resources)
        for _resource in _resources:
            _id = _resource.get("_id")
            if _id in added_ids:
                continue
            if keep_resource_ids and _id in keep_resource_ids:
                continue
            if not _has_state_pointer(_resource):
                stack.logger.debug(
                    f"record-only row {_id} "
                    f"(resource_type={_resource.get('resource_type')}) - "
                    "unrecorded LAST, after every teardown order settles"
                )
                added_ids.append(_id)
                record_only_candidates.append(_resource)
                continue
            if _resource.get("removal_confirmed_at"):
                # The resources table is a durable PROGRESS LEDGER: this
                # row's engine destroy already succeeded (the CLI persisted
                # the confirmation) — a retry must never repeat a confirmed
                # removal.
                stack.logger.debug(
                    f"skipping removal-confirmed row {_id} "
                    f"(confirmed at {_resource['removal_confirmed_at']})"
                )
                continue
            added_ids.append(_id)
            if _resource.get("query_only") or _resource.get("parent"):
                parallel_candidates.append(_resource)
            else:
                sequential_candidates.append(_resource)

    # A repeated project destroy legitimately finds no rows after the first
    # sweep. Keep that retry idempotent, but make a broken project link visible.
    if matched_row_count == 0:
        warning = (
            "WARNING: zero resources matched the project's schedule ids "
            f"{stack.to_list(stack.ref_schedule_ids)!r}; nothing to destroy. "
            "If this project should still have resources, the resource-to-project "
            "link is broken."
        )
        stack.logger.warning(warning)
        stack.output_to_ui({"warning": warning})

    sequential_candidates = sorted(
        sequential_candidates,
        key=_created_at_sort_key,
        reverse=True,
    )

    # The record-only rows are independent row deletes; sort by _id only so the
    # trailing unrecord step is deterministic without requiring a created_at on
    # a non-infrastructure row.
    record_only_candidates = sorted(
        record_only_candidates,
        key=lambda r: r["_id"],
    )

    stack.logger.debug(
        f"parallel teardown candidate ids "
        f"{[r.get('_id') for r in parallel_candidates]}"
    )
    stack.logger.debug(
        f"sequential teardown candidate ids (reverse created_at order) "
        f"{[r.get('_id') for r in sequential_candidates]}"
    )
    stack.logger.debug(
        f"record-only candidate ids (unrecorded last) "
        f"{[r.get('_id') for r in record_only_candidates]}"
    )

    parallel_requests = [_teardown_projection(r) for r in parallel_candidates]
    sequential_requests = [_teardown_projection(r) for r in sequential_candidates]
    record_only_requests = [_teardown_projection(r) for r in record_only_candidates]
    return parallel_requests, sequential_requests, record_only_requests


def _unrecord_record_only_rows_last(stack, record_only_requests):
    """Emit the trailing unrecord STEP - delete the record-only rows LAST.

    The record-only rows are the destroy's argument base and retry evidence
    (defect 45), so their delete must run ONLY after every resource teardown
    order has settled, and NOT at all if one fails. An inline
    ``unrecord_resource`` runs during ``run.py`` evaluation - before any
    teardown order executes - so the delete is emitted as ORDERS instead:

    - ``wait_all(must_complete=True)`` emits one ``check-wait::api`` barrier
      whose ``prior_all`` scope is this stack's exec order, covering every
      teardown order in both tiers. A resource teardown carries the default
      ``must_succeed=True``; when one settles failed the job fate holds every
      order after the barrier, so no unrecord runs and the rows survive for
      the retry. ``must_complete=True`` also drains: all teardowns attempt
      before the job fails, maximizing removal per pass.
    - each row delete is a ``resource/remove/record`` order carrying
      ``{_id, destroy: False}``. The worker routes ``resource/remove`` to the
      CLI resource-remove handler, whose ``destroy=False`` branch deletes the
      matched record-only row (no engine teardown). ``remove_resource`` cannot
      emit this: its ``_id`` branch hardcodes ``destroy=True``, and a
      ``destroy=True`` on a pointer-less row has no state to tear down.

    Each unrecord order sets ``must_succeed=False``: the SaaS ``run_complete``
    by-project sweep is the PRIMARY backstop and is gated on a COMPLETED
    destroy. The CLI record-only delete fails loud on an already-gone row, so
    a must-succeed unrecord could fail an otherwise-complete destroy and block
    that primary sweep. The leave-in-place-on-failure guarantee is carried by
    ``must_succeed=True`` on the RESOURCE teardown orders, not these.
    """
    if not record_only_requests:
        return

    stack.wait_all(must_complete=True)

    for request in record_only_requests:
        stack.logger.debug(f"unrecording record-only row {request}")
        order = stack.add_resource(
            role="resource/remove/record",
            pargs="resource remove",
            order_type="resource_delete::proxy",
            default_values={**request, "destroy": False},
            human_description="Unrecord record-only row after teardown",
        )
        order["must_succeed"] = False


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

    parallel_requests, sequential_requests, record_only_requests = _get_delete_resources(
        stack,
        keep_resource_ids=keep_resource_ids)

    # parallel overide set True: remove everything concurrently (an explicit
    # caller opt-in for independent resources — no ordering guarantee).
    # Mirrors the original (_main/run.py:143-151): the combined tier list,
    # all removed inside one parallel window.
    if stack.get_attr("parallel_overide") and (parallel_requests or sequential_requests):
        stack.logger.debug("Parallel overide set True")
        stack.set_parallel()
        for resource in parallel_requests + sequential_requests:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        # wait_all(must_complete=True) inside closes the parallel window and
        # fences the record-only unrecords behind the whole concurrent batch.
        _unrecord_record_only_rows_last(stack, record_only_requests)
        return stack.get_results(None)

    # Two tiers, as the original (_main/run.py:153-167): the independent
    # (query_only/parent) tier torn down concurrently under set_parallel(),
    # then unset_parallel() emits the check-wait::api wait row so the
    # sequential tier waits on the whole batch.
    if parallel_requests:
        stack.set_parallel()
        for resource in parallel_requests:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        stack.unset_parallel()

    # The sequential reverse-created_at chain. Each remove order depends on
    # the previous one (queue_ids edge), so resources that depend on one
    # another are removed dependency-safe, newest-created first.
    for resource in sequential_requests:
        stack.logger.debug(f"removing resource {resource}")
        stack.remove_resource(**resource)

    # The record-only rows are unrecorded LAST, fenced behind every teardown
    # order by a wait_all(must_complete=True) barrier (user decision).
    _unrecord_record_only_rows_last(stack, record_only_requests)

    return stack.get_results(None)
