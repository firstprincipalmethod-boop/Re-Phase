"""Finite path computations. MIT. Adjacent relations only; nonempty guard explicit."""
from __future__ import annotations
from collections import Counter
from itertools import product, combinations
from math import prod
from typing import Callable, Any


def _json(x):
    if isinstance(x,(tuple,list)):return [_json(v) for v in x]
    if isinstance(x,set):return [_json(v) for v in sorted(x)]
    return x


def path_summary(F: list[set], T: list[set], feature: Callable, target: set) -> dict:
    """Forward path extension plus backward reachability; no removed state stages."""
    n=len(F)-1
    paths=[(x,) for x in sorted(F[0])]
    R=[set(F[0])]
    for k in range(n):
        paths=[p+(b,) for p in paths for b in sorted(F[k+1]) if (p[-1],b) in T[k]]
        R.append(F[k+1] & {b for a,b in T[k] if a in R[k]})
    S=[set() for _ in F];S[n]=set(F[n])
    for k in range(n-1,-1,-1):S[k]=F[k] & {a for a,b in T[k] if b in S[k+1]}
    V=[R[k]&S[k] for k in range(n+1)]
    bridges=[{(a,b) for a,b in T[k] if a in R[k] and b in S[k+1]} for k in range(n)]
    pt_features=sorted({feature(p) for p in product(*[sorted(f) for f in F])})
    hist=Counter(feature(p) for p in paths);lift_features=sorted(hist)
    tau=next((k for k,r in enumerate(R) if not r),None)
    target_check=('vacuous_empty_lift' if not paths else 'within_target' if set(lift_features)<=target else 'outside_target')
    return {
        'pt_size':prod(map(len,F)), 'lift_size':len(paths),
        'lift_status':'infeasible' if not paths else 'unique' if len(paths)==1 else 'ambiguous',
        'lifts':_json(sorted(paths)), 'fibers':_json([sorted(f) for f in F]),
        'forward_reachable':_json([sorted(r) for r in R]),
        'backward_survivable':_json([sorted(s) for s in S]),
        'surviving_slices':_json([sorted(v) for v in V]),
        'viable_bridges':_json([sorted(b) for b in bridges]),
        'live_cone_obstructions':[k for k,b in enumerate(bridges) if R[k] and S[k+1] and not b],
        'retrospective_break':[k for k,b in enumerate(bridges) if not b],
        'tau_pre':{'status':'no_failure' if tau is None else 'finite','k':tau},
        'feature_image_pt':pt_features, 'feature_image_lift':lift_features,
        'feature_lift_counts':[{'value':v,'count':hist[v]} for v in lift_features],
        'target':sorted(target), 'target_check':target_check,
        'recoverable':bool(paths) and set(lift_features)<=target,
    }


def feature_function(f: dict) -> Callable:
    if f['kind']=='terminal_state':return lambda p:p[-1]
    if f['kind']=='terminal_map':return lambda p:f['map'][p[-1]]
    if f['kind']=='all_branch_equal':
        def h(p):
            labels=[f['labels'][f'X{k}'][x] for k,x in enumerate(p)]
            return f['equal_value'] if len(set(labels))==1 else f['different_value']
        return h
    raise ValueError('unsupported feature')


def _path(s: dict, trans: str='transitions') -> dict:
    F=[set(s['state_sets'][f'X{k}']) for k in range(len(s['state_sets']))]
    T=[{tuple(e) for e in s[trans][f'T{k}']} for k in range(len(F)-1)]
    return path_summary(F,T,feature_function(s['feature']),set(s['target']))


def velocity(s: dict) -> dict:
    n=s['horizon'];X={(q,v) for q in s['position_domain'] for v in s['velocity_domain']}
    trans={(x,(x[0]+x[1],x[1])) for x in X if (x[0]+x[1],x[1]) in X}
    rows=[]
    for size in range(n+2):
        for J in combinations(range(n+1),size):
            F=[{x for x in X if x[0]==s['displayed_positions'][k]} if k in J else set(X) for k in range(n+1)]
            row=path_summary(F,[trans]*(n),lambda p:p[0][1],set(s['target']))
            rows.append({'schedule':list(J),**row})
    good=[r['schedule'] for r in rows if r['recoverable']]
    minimal=[j for j in good if not any(set(k)<set(j) for k in good)]
    full=next(r for r in rows if r['schedule']==sorted(s['full_schedule']))
    thin=next(r for r in rows if r['schedule']==sorted(s['thinned_schedule']))
    return {'obligation_type':'initial_velocity_recoverability', 'state_dimension':2,
            'state_stage_count':n+1,'schedules':rows,'minimal_sufficient_schedules':minimal,
            'full_context':full,'thinned_context':thin,
            'observation_thinning_confirmed':set(thin['schedule'])<set(full['schedule']) and full['recoverable'] and thin['recoverable'],
            'intermediate_state_removed':False}


def solve(wid: str,s: dict) -> dict:
    if wid=='v53_constant_velocity':
        c=velocity(s)
        checks={'full_context_recovers':c['full_context']['recoverable'],
                'thinner_context_recovers':c['observation_thinning_confirmed'],
                'no_single_observation_recovers':all(not r['recoverable'] for r in c['schedules'] if len(r['schedule'])==1),
                'every_pair_recovers':all(r['recoverable'] for r in c['schedules'] if len(r['schedule'])==2)}
    elif wid=='v53_same_slices_different_edges':
        a=_path(s,'transitions_variant_a');b=_path(s,'transitions_variant_b')
        c={'obligation_type':'path_feature_recoverability_comparison','variant_a':a,'variant_b':b,
           'same_input_fibers':a['fibers']==b['fibers'],
           'same_surviving_slices':a['surviving_slices']==b['surviving_slices'],
           'different_viable_bridges':a['viable_bridges']!=b['viable_bridges']}
        checks={'nonempty_both':a['lift_size']>0 and b['lift_size']>0,
                'same_surviving_slices':c['same_surviving_slices'],
                'different_lifts':a['lifts']!=b['lifts'],
                'different_features':a['feature_image_lift']!=b['feature_image_lift'],
                'a_recovers_b_does_not':a['recoverable'] and not b['recoverable']}
    else:
        c={'obligation_type':'path_feature_recoverability',**_path(s)}
        if wid=='v53_collapse':checks={'pointwise_nonempty':c['pt_size']>0,'lift_empty':c['lift_size']==0,'not_recoverable':not c['recoverable']}
        elif wid=='v53_gap_collapse':checks={'pointwise_nonempty':c['pt_size']>0,'lift_empty':c['lift_size']==0,'live_cone_obstructions_absent':not c['live_cone_obstructions']}
        elif wid=='v53_unique_lift':checks={'multiple_pointwise_candidates':c['pt_size']>1,'unique_lift':c['lift_size']==1,'recovers':c['recoverable']}
        elif wid=='v53_feature_ambiguous_recoverable':checks={'ambiguous_paths':c['lift_size']>1,'feature_recovers':c['recoverable']}
        elif wid=='v53_missing_cell':checks={'nonempty_lift':c['lift_size']>0,'strict_feature_narrowing':set(c['feature_image_lift'])<set(c['feature_image_pt']),'not_recoverable':not c['recoverable']}
        else:raise ValueError('unknown v53 id')
    c['claim_checks']=checks;c['registered_claim_holds']=all(checks.values())
    return c
