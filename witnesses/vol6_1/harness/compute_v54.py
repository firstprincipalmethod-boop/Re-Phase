"""Vol.5.4 (selector) witness compute functions.

M1-M3 (retained-coordinate typing / cell-level selector inconsistency / CPre exclusion) are
LOCKED (2026-07-05, Obsidian 03_Working_Memos/Vol6_1/v54_selector_model_resolution_M1_M3.md,
D-v54-01..06). Canonical specs land in specs/v54/ FIRST, then the compute function for that
witness is filled in (D13 sequencing) -- Toy A and Toy B are live; Toy C-F remain as
specs/v54/*.json.example until their own compute functions are added.

Convention (D12/D-v54-02/03): family-level, not |Pt|/|Lift|. Counted objects are the
admissible base-path family, per-selector-class information cells, and member-relative
projected choice sets V^Q(y) for a fixed choice_kind Q. Every witness returns a flat dict
with a top-level 'verdict' (schema.VERDICT_BY_WITNESS) plus witness-specific detail; for
variant-bearing witnesses (Toy A, Toy D -- D-v54-03) the verdict is the PRIMARY certified
claim (D-v54-06), and full per-variant detail lives under 'variants', never flattened into
the verdict itself.

cell_conflict certificate shape (M2 lock, §2.1): for an information cell with member ->
choice-set data, the common choice set is the intersection across members; cell_conflict
is true iff that intersection is empty. Absence of conflict is NOT an existence proof in
general (M2 point 6) -- but for choice_kind in {state, bridge_edge, action} a nonempty
common choice set IS itself a constructive witness (pick any element), so selector_exists
:= not cell_conflict is sound for those kinds. choice_kind=nonblocking_prefix existence is
NOT certified this way (cross-time consistency required, still deferred).
"""
from compute import witness
from schema import VERDICT_BY_WITNESS


def _jsonable(choice):
    """Tuples (e.g. bridge edges) must serialize the same way whether freshly computed
    or round-tripped through golden JSON (which only knows lists) -- otherwise golden
    compare() sees ('A','B') != ['A','B'] and reports a false drift."""
    return list(choice) if isinstance(choice, tuple) else choice


def _cell_conflict(members_choice, cell_id, choice_kind, obstructed_property):
    """members_choice: {member: [choice, ...]} -- the member-relative admissible choice set
    V^Q(member) for one information cell under one choice_kind Q. Returns the M2 nonexistence
    certificate object (dict) plus whether a selector_exists witness is constructible."""
    common = None
    for choices in members_choice.values():
        s = set(choices)
        common = s if common is None else (common & s)
    common_sorted = sorted(common) if common else []
    conflict = len(common_sorted) == 0
    cert = {
        "status": "conflict" if conflict else "no_conflict",
        "cell_id": cell_id,
        "choice_kind": choice_kind,
        "obstructed_property": obstructed_property,
        "members": sorted(members_choice),
        "choice_sets": {m: [_jsonable(c) for c in sorted(v)] for m, v in members_choice.items()},
        "common_choice_set": [_jsonable(c) for c in common_sorted],
    }
    return cert, (not conflict)


def _split_edges(bridge_edges):
    """bridge_edges: {member: [[left, right], ...]}. Returns each member's left-endpoint
    set, right-endpoint set, and edge set (as hashable tuples)."""
    left = {m: {e[0] for e in edges} for m, edges in bridge_edges.items()}
    right = {m: {e[1] for e in edges} for m, edges in bridge_edges.items()}
    edge_tuples = {m: [tuple(e) for e in edges] for m, edges in bridge_edges.items()}
    return left, right, edge_tuples


def _intersect_all(sets_by_member):
    common = None
    for s in sets_by_member.values():
        common = set(s) if common is None else (common & set(s))
    return sorted(common) if common else []


@witness("v54_toy_A_memoryless_fail")
def _(spec):
    """Toy A (Vol.5.4 SS5.5): fiberwise liftability does not imply memoryless selector
    existence. Two variants over the SAME family (D-v54-03): memoryless (one shared
    information cell -> conflict) and lookback_1 (two singleton cells -> no conflict,
    trivially constructible witness). choice_kind=state, so selector_exists :=
    not cell_conflict is sound (M2 point 6)."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "state")
    time_k = s["time"]
    lifts = s["lifts"]
    info_cells = s["information_cells"]

    # V_k^state(path) = {the path's own lift value at time_k} -- each path has a unique
    # lift, so this is a singleton; the memoryless cell's conflict comes purely from
    # grouping two DIFFERENT paths' singletons into one information cell (see below).
    choice_at_k = {path: [lifts[path][time_k]] for path in lifts}

    variants = {}
    for cell_name, cells in info_cells.items():
        per_cell = {}
        cells_exist = True
        for label, members in cells.items():
            members_choice = {m: choice_at_k[m] for m in members}
            cert, exists = _cell_conflict(
                members_choice, cell_id=f"{cell_name}:{label}",
                choice_kind=choice_kind, obstructed_property="plain_adapted_selector")
            per_cell[label] = cert
            cells_exist = cells_exist and exists
        variants[cell_name] = {"cells": per_cell, "selector_exists": cells_exist}

    return {
        "choice_kind": choice_kind,
        "time": time_k,
        "variants": {
            "memoryless": variants["memoryless_t1"],
            "lookback_1": variants["lookback_1_t1"],
        },
        "verdict": VERDICT_BY_WITNESS[spec["id"]],
    }


@witness("v54_toy_B_bridge_conflict")
def _(spec):
    """Toy B (Vol.5.4 SS5.6): common state support does not imply common bridge-valid
    selector. Members u, v of a single information cell have overlapping left-endpoint
    and right-endpoint support (derived from bridge_edges, not asserted) -- but their
    allowed (left,right) EDGE pairs don't overlap, so the bridge_edge cell_conflict is
    nonempty statewise support / empty common edge choice."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "bridge_edge")
    cell_name, members = next(iter(s["information_cell"].items()))
    bridge_edges = s["bridge_edges"]

    left, right, edge_tuples = _split_edges(bridge_edges)
    common_left_support = _intersect_all(left)
    common_right_support = _intersect_all(right)

    members_choice = {m: edge_tuples[m] for m in members}
    cert, exists = _cell_conflict(
        members_choice, cell_id=cell_name, choice_kind=choice_kind,
        obstructed_property="bridge_valid_selector")

    return {
        "choice_kind": choice_kind,
        "time": s.get("time"),
        "selector_class": s.get("selector_class"),
        "common_left_support": common_left_support,
        "common_right_support": common_right_support,
        "cell_conflict": cert,
        "selector_exists": exists,
        "verdict": VERDICT_BY_WITNESS[spec["id"]],
    }


# --- Toy C-F: specs/v54/*.json.example only so far; compute functions land with their
# own live-spec promotion (D13 sequencing), one witness at a time. ---
