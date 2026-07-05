"""Vol.5.4 (selector) witness compute functions.

M1-M3 (retained-coordinate typing / cell-level selector inconsistency / CPre exclusion) are
LOCKED (2026-07-05, Obsidian 03_Working_Memos/Vol6_1/v54_selector_model_resolution_M1_M3.md,
D-v54-01..06). Canonical specs land in specs/v54/ FIRST, then the compute function for that
witness is filled in (D13 sequencing) -- Toy A through Toy F are all live.

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


@witness("v54_toy_C_nonblocking")
def _(spec):
    """Toy C (Vol.5.4 SS5.7): local common feasibility does not imply causal
    non-blocking choice. A shared prefix has locally-feasible choices (both reachable
    via T0), but each future admits continuation (via T1) through a DIFFERENT prefix
    choice -- so the nonblocking-prefix choice set must be member-relative (V_k^nb(y),
    not a bare V_k^nb) or this conflict can't be represented (M2 SS2.1 point 3).
    choice_kind=nonblocking_prefix: a conflict here (as in this witness) IS a sound
    nonexistence certificate, but the converse -- selector_exists=true -- is NOT
    certified for this choice_kind without additionally showing cross-time
    consistency (M2 point 6, still deferred). This witness is nonexistence-only."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "nonblocking_prefix")
    shared_prefix = s["shared_prefix"]
    local_choices = set(s["local_choices"])
    futures = s["futures"]
    t0 = {tuple(e) for e in s["transitions"]["T0"]}
    t1 = {tuple(e) for e in s["transitions"]["T1"]}

    reachable_choices = {c for (frm, c) in t0 if frm == shared_prefix and c in local_choices}

    members_choice = {}
    for future_name, info in futures.items():
        terminal = info["terminal"]
        members_choice[future_name] = [c for c in reachable_choices if (c, terminal) in t1]

    cert, exists = _cell_conflict(
        members_choice, cell_id=f"{shared_prefix}:futures",
        choice_kind=choice_kind, obstructed_property="nonblocking_selector")

    return {
        "choice_kind": choice_kind,
        "time": s.get("time"),
        "selector_class": s.get("selector_class"),
        "shared_prefix": shared_prefix,
        "cell_conflict": cert,
        "selector_exists": exists,
        "verdict": VERDICT_BY_WITNESS[spec["id"]],
    }


def _display_cell_key(display_model, info):
    """What a given display_model actually SHOWS about a world member -- the key two
    members share iff that display model cannot tell them apart."""
    tilt = tuple(info["tilt_history"])
    if display_model == "original":
        return "tilt:" + ",".join(str(x) for x in tilt)
    if display_model == "augmented_retained_mode":
        return f"mode:{info['mode']}"
    raise ValueError(f"unknown display_model {display_model!r}")


def _toy_d_variant(world, display_model, choice_kind):
    """world: {member: {tilt_history, mode, required_action}}. Groups members into
    information cells by what display_model shows, then certifies the M2 action-level
    cell_conflict per cell. D-v54-04: an existence claim (selector_exists=true) is
    only made alongside an explicit selector_table witness -- never bare."""
    cells = {}
    for member, info in world.items():
        cells.setdefault(_display_cell_key(display_model, info), []).append(member)

    per_cell = {}
    overall_exists = True
    for cell_id, members in sorted(cells.items()):
        members_choice = {m: [world[m]["required_action"]] for m in members}
        cert, exists = _cell_conflict(
            members_choice, cell_id=cell_id,
            choice_kind=choice_kind, obstructed_property="action_valued_selector")
        per_cell[cell_id] = cert
        overall_exists = overall_exists and exists

    result = {"cells": per_cell, "selector_exists": overall_exists}
    if overall_exists:
        result["selector_table"] = {cid: cert["common_choice_set"][0] for cid, cert in per_cell.items()}
    return result


@witness("v54_toy_D_retention_memory")
def _(spec):
    """Toy D (Vol.5.4 SS5.8): retained coordinate and selector memory are different
    resources (M1), and Toy D's failure certification depends on M2's action-level
    cell_conflict, not on M1's type distinction alone (M1 SS1.3 Must-fix 2: SILENT
    alone does not imply selector failure). Three variants (D-v54-03):
      traceable_original    -- differing tilt_history separates stable/slip under
                                the ORIGINAL display; no augmentation needed.
      silent_original       -- IDENTICAL tilt_history under the original display ->
                                forced action conflict (stable requires 'n', slip
                                requires 'r').
      silent_augmented      -- retained mode breaks the tie even though
                                tilt_history is identical -> conflict resolved, with
                                an explicit selector_table witness (D-v54-04:
                                selector_exists=true alone is not enough)."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "action")
    worlds = s["worlds"]

    variants = {
        "traceable_original": _toy_d_variant(worlds["traceable"], "original", choice_kind),
        "silent_original": _toy_d_variant(worlds["silent"], "original", choice_kind),
        "silent_augmented": _toy_d_variant(worlds["silent"], "augmented_retained_mode", choice_kind),
    }

    return {
        "choice_kind": choice_kind,
        "variants": variants,
        "verdict": VERDICT_BY_WITNESS[spec["id"]],
    }


def _toy_ef_quotient(s, choice_kind):
    """Shared M3 quotient/selector-preservation compute for Toy E/F (M3 lock SS3.1-3.2):
    groups hidden_members by quotient_map, derives exact/target_sound/square_commutes
    generically from the spec's own display_images/target_verdict (never hardcoded),
    and certifies an action cell_conflict per quotient cell via the same M2 Gamma
    machinery used by Toy A/B/C/D. cpre_claim_status is always 'not_certified' (M3:
    CPre inclusion is out of scope unless a must/may abstraction mode is fixed)."""
    hidden_members = s["hidden_members"]
    quotient_map = s["quotient_map"]
    display_images = s["display_images"]
    target_verdict = s["target_verdict"]
    required_actions = s["required_actions"]
    display_quotient = s.get("display_quotient")

    # exact(rho_A) iff rho_A is injective on admissible full paths (M3 SS4).
    exact = len(set(quotient_map.values())) == len(hidden_members)

    quotient_cells = {}
    for m in hidden_members:
        quotient_cells.setdefault(quotient_map[m], []).append(m)
    quotient_cells = {z: sorted(ms) for z, ms in quotient_cells.items()}

    # target_sound(rho_A) iff members merged into the same cell share one target
    # verdict (M3 SS5).
    target_sound = all(len({target_verdict[m] for m in ms}) == 1
                        for ms in quotient_cells.values())

    # square_commutes, grounded for the identity display quotient (M3 SS3.1): members
    # merged into the same quotient cell must already share one displayed image.
    square_commutes = None
    quotient_display = None
    if display_quotient == "identity":
        square_commutes = all(len({display_images[m] for m in ms}) == 1
                               for ms in quotient_cells.values())
        if square_commutes:
            quotient_display = {z: display_images[ms[0]] for z, ms in quotient_cells.items()}

    quotient_common_choice_set = {}
    overall_exists = True
    for z, ms in quotient_cells.items():
        members_choice = {m: [required_actions[m]] for m in ms}
        cert, exists = _cell_conflict(
            members_choice, cell_id=z, choice_kind=choice_kind,
            obstructed_property="quotient_selector_preserving")
        quotient_common_choice_set[z] = cert["common_choice_set"]
        overall_exists = overall_exists and exists

    result = {
        "choice_kind": choice_kind,
        "display_quotient": display_quotient,
        "display_images": dict(display_images),
        "quotient_display": quotient_display,
        "square_commutes": square_commutes,
        "exact": exact,
        "quotient_cells": quotient_cells,
        "target_verdict_by_member": dict(target_verdict),
        "target_sound": target_sound,
        "choice_sets": {m: [required_actions[m]] for m in hidden_members},
        "quotient_common_choice_set": quotient_common_choice_set,
        "quotient_selector_exists": overall_exists,
        "selector_preserving_action": overall_exists,
        "cpre_claim_status": "not_certified",
    }
    if overall_exists:
        result["selector_table"] = {z: v[0] for z, v in quotient_common_choice_set.items()}
    return result


@witness("v54_toy_E_target_sound_not_selector")
def _(spec):
    """Toy E (Vol.5.4 SS5.9, M3 lock SS8): target-sound quotient need not preserve
    selector existence. x0, x1 merge into one quotient cell z (target-sound: both
    target verdicts are 'good'), but their required actions (a vs b) conflict ->
    quotient selector does not exist. CPre inclusion is not certified here (M3)."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "action")
    result = _toy_ef_quotient(s, choice_kind)
    result["verdict"] = VERDICT_BY_WITNESS[spec["id"]]
    return result


@witness("v54_toy_F_safe_nonexact")
def _(spec):
    """Toy F (Vol.5.4 SS5.9, M3 lock SS9): non-exact forgetting can still be
    target-sound and action-selector-preserving (positive control for Toy E). x0,
    x1 merge into one quotient cell (target-sound: both 'good', so still not
    exact), but this time both require the SAME action 'n' -> quotient selector
    exists, with an explicit selector_table witness. CPre inclusion is not
    certified here (M3)."""
    s = spec["spec"]
    choice_kind = s.get("choice_kind", "action")
    result = _toy_ef_quotient(s, choice_kind)
    result["verdict"] = VERDICT_BY_WITNESS[spec["id"]]
    return result
