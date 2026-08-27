"""Wait-row integration test stack (plan wait-all-wt-scoped-ordering, P9).

One stack, one required argument ``scenario``; each config0.yaml under
config0_yamls_repos/wait-tests/<scenario>/ targets one wait condition
(decision 16). Orders are cheap shell orders (echo / sleep / exit 1); no
cloud resource is created. Scenarios (e) and (h) reference the substack
config0-hub:::config0_core::wait_test_child (mode=slow / mode=fast).

Legend: ok = "echo ok", bad = "exit 1", slow = "sleep 20". E = this stack's
exec order. ** = the wait row (check-wait::api, role check/wait/instance,
dependencies.prior_all=true, retries=-1, base_wt=E, scoped to E.*). Inside a
parallel window every order depends on the anchor (the parent exec order
for a first emission, otherwise the order active before set_parallel()).

(a) plain wait:               set_parallel(); ok; ok; ok; wait_all(); ok
  E.005 ok  E.010 ok  E.015 ok  E.020 ** WAIT  E.025 ok deps=[WAIT]

(b) sibling fails, must_succeed default:
                              set_parallel(); ok; bad; ok; wait_all(); ok
  E.005 ok  E.010 bad  E.015 ok  E.020 ** WAIT  E.025 ok deps=[WAIT]

(c) sibling fails, must_succeed=False:
                              set_parallel(); ok; bad(must_succeed=False); ok; wait_all(); ok
  E.005 ok  E.010 bad(must_succeed=false)  E.015 ok  E.020 ** WAIT  E.025 ok deps=[WAIT]

(d1) wait_all(must_complete=True), two bad, must_succeed default:
                              set_parallel(); bad; bad; slow; wait_all(must_complete=True); ok
  E.005 bad  E.010 bad  E.015 slow  E.020 ** WAIT must_complete  E.025 ok deps=[WAIT]

(d2) as d1, must_succeed=False on both bad orders.

(e) grandchild holds the wait: set_parallel(); wait_test_child(slow); wait_all(); ok
  E.005      instruction/add wait_test_child
  E.005.005  slow           (grandchild, in no list)
  E.005.010  ** WAIT-child  base_wt=E.005
  E.005.015  ok
  E.010      ** WAIT        base_wt=E, held by E.005.*
  E.015      ok deps=[WAIT]

(g) sequential order before the batch: slow; set_parallel(); ok; ok; wait_all(); ok
  E.005 slow  E.010 ok deps=[slow]  E.015 ok deps=[slow]  E.020 ** WAIT  E.025 ok deps=[WAIT]

(h) parallel substacks B (fast) and C (slow), C must not hold B's wait:
                              set_parallel(); wait_test_child(fast) as B;
                              wait_test_child(slow) as C; wait_all(); ok
  E.005      instruction/add B (fast)              base_wt=E
  E.005.005  ok  E.005.010 ok  E.005.015 ok        base_wt=E.005
  E.005.020  ** WAIT-B                              base_wt=E.005
  E.005.025  ok deps=[WAIT-B]
  E.010      instruction/add C (slow)  deps=[anchor] base_wt=E
  E.010.005  slow                                   base_wt=E.010
  E.010.010  ** WAIT-C                              base_wt=E.010
  E.010.015  ok deps=[WAIT-C]
  E.015      ** WAIT-A  deps=[anchor]               base_wt=E, held by E.005.* and E.010.*
  E.020      ok deps=[WAIT-A]
"""

OK = "echo ok"
BAD = "exit 1"
SLOW = "sleep 20"

CHILD = "config0-hub:::config0_core::wait_test_child"

SCENARIOS = ["a", "b", "c", "d1", "d2", "e", "g", "h"]


def _ok(stack):
    return stack.add_external_cmd(cmd=OK, role="external/cli/execute")


def _bad(stack, must_succeed=True):
    order = stack.add_external_cmd(cmd=BAD, role="external/cli/execute")
    if not must_succeed:
        order["must_succeed"] = False
    return order


def _slow(stack):
    return stack.add_external_cmd(cmd=SLOW, role="external/cli/execute")


def _child(stack, mode):
    return stack.wait_child.insert(
        display=True,
        arguments={"mode": mode},
        human_description=f"wait_test_child mode={mode}",
    )


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_required(key="scenario", types="str", choices=SCENARIOS)
    stack.add_substack(CHILD, "wait_child")

    stack.init_variables()
    stack.init_substacks()

    scenario = stack.scenario

    if scenario == "g":
        _slow(stack)

    stack.set_parallel()

    if scenario in ("a", "g"):
        _ok(stack)
        _ok(stack)
        if scenario == "a":
            _ok(stack)
    elif scenario == "b":
        _ok(stack)
        _bad(stack)
        _ok(stack)
    elif scenario == "c":
        _ok(stack)
        _bad(stack, must_succeed=False)
        _ok(stack)
    elif scenario == "d1":
        _bad(stack)
        _bad(stack)
        _slow(stack)
    elif scenario == "d2":
        _bad(stack, must_succeed=False)
        _bad(stack, must_succeed=False)
        _slow(stack)
    elif scenario == "e":
        _child(stack, "slow")
    elif scenario == "h":
        _child(stack, "fast")
        _child(stack, "slow")
    else:
        raise ValueError(f"unsupported wait_test scenario: {scenario!r}")

    stack.wait_all(must_complete=scenario in ("d1", "d2"))
    _ok(stack)

    return stack.get_results()
