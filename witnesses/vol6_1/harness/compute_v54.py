"""Typed finite selection calculations. MIT. Never identify sections with policies."""
from __future__ import annotations
from itertools import product
from math import prod
import json


def jkey(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),sort_keys=True)

def groups(values: dict) -> dict:
    cells={}
    for m,v in sorted(values.items()):cells.setdefault(jkey(v),[]).append(m)
    return dict(sorted(cells.items()))

def cell_choices(cells: dict, allowed: dict, obligation: str) -> dict:
    records={};tables={};count=1
    for cid,ms in sorted(cells.items()):
        common=set(allowed[ms[0]])
        for m in ms[1:]:common.intersection_update(allowed[m])
        vals=sorted(common)
        def out(v):return list(v) if type(v) is tuple else v
        records[cid]={'members':sorted(ms),'allowed_by_member':{m:[out(v) for v in sorted(allowed[m])] for m in sorted(ms)},'common_choices':[out(v) for v in vals],'conflict':not vals}
        count*=len(vals)
        if vals:tables[cid]=out(vals[0])
    return {'obligation_type':obligation,'cells':records,'exists':count>0,'count':count,'table':tables if count else None}

def section_summary(display: dict) -> dict:
    cells=groups(display);count=prod(len(ms) for ms in cells.values())
    # Each key is a JSON encoding of the actual display value; no ambient base added.
    return {'count':count,'exists':count>0,'table':{k:ms[0] for k,ms in cells.items()} if count else None,'fibers':cells}

def info(y:list,k:int,cls:str):
    if cls=='offline':return y
    if cls=='causal':return y[:k+1]
    r=0 if cls=='memoryless' else int(cls.split('_')[1])
    return y[max(0,k-r):k+1]

def toy_a(s:dict) -> dict:
    variants={};n=len(next(iter(s['lifts'].values())))
    for cls in s['variants']:
        by_time=[]
        for k in range(n):
            cells=groups({m:info(y,k,cls) for m,y in s['displayed_paths'].items()})
            choices=cell_choices(cells,{m:{path[k]} for m,path in s['lifts'].items()},'state_component')
            by_time.append({'time':k,**choices})
        ok=all(r['exists'] for r in by_time)
        # The full path for every display is explicitly supplied and unique.
        variants[cls]={'full_path_selector_exists':ok,'selector_count':1 if ok else 0,
                       'per_time':by_time,'selected_paths':dict(sorted(s['lifts'].items())) if ok else None,
                       'selector_tables':[r['table'] for r in by_time] if ok else None}
    return {'obligation_type':'all_time_path_selector_on_given_unique_lifts','variants':variants,
            'offline_section':section_summary({m:s['displayed_paths'][m] for m in s['displayed_paths']})}

def toy_b(s:dict) -> dict:
    allowed={m:{tuple(e) for e in es} for m,es in s['bridge_edges'].items()}
    c=cell_choices(s['information_cell'],allowed,'abstract_edge_choice')
    return {'obligation_type':'abstract_member_dependent_edge_choice','choice':c,
            'common_left_support':sorted(set.intersection(*[{e[0] for e in es} for es in allowed.values()])),
            'common_right_support':sorted(set.intersection(*[{e[1] for e in es} for es in allowed.values()])),
            'same_member_left_supports':len({tuple(sorted({e[0] for e in es})) for es in allowed.values()})==1,
            'full_path_selector_status':'not_checked',
            'fixed_transition_bridge_realization_claimed':False}

def toy_c(s:dict) -> dict:
    reachable={b for a,b in s['transitions']['T0'] if a==s['shared_prefix']}
    choices={m:{a for a,b in s['transitions']['T1'] if a in reachable and b==f['terminal']} for m,f in s['futures'].items()}
    local=cell_choices({'shared_prefix':sorted(s['futures'])},choices,'one_prefix_continuation_choice')
    conflict=not local['exists']
    return {'obligation_type':'prefix_nonexistence_certificate_only','locally_reachable_choices':sorted(reachable),
            'continuation_choice':local,'each_future_liftable':all(choices.values()),
            'full_path_selector_exists':False if conflict else None,
            'full_path_selector_status':'ruled_out_by_prefix_conflict' if conflict else 'not_checked',
            'general_controller_synthesis_claimed':False}

def toy_d(s:dict) -> dict:
    worlds={}
    for name,world in sorted(s['worlds'].items()):
        allowed={m:{d['required_action']} for m,d in world.items()}
        policies={}
        for cls in s['memory_classes']:
            cells=groups({m:info(d['tilt_history'],len(d['tilt_history'])-1,cls) for m,d in world.items()})
            policies[cls]=cell_choices(cells,allowed,'terminal_common_action_policy')
        aug={m:[d['tilt_history'],d['mode']] for m,d in world.items()}
        policies['retained_mode_augmented']=cell_choices(groups(aug),allowed,'terminal_common_action_policy')
        worlds[name]={'policies':policies,
                      'original_display_section':section_summary({m:d['tilt_history'] for m,d in world.items()}),
                      'augmented_display_section':section_summary(aug)}
    return {'obligation_type':'terminal_action_policy_not_path_section','worlds':worlds,
            'retained_mode_is_additional_information':True,'closed_loop_guarantee_claimed':False}

def toy_ef(s:dict) -> dict:
    M=s['hidden_members'];rho=s['quotient_map'];display=s['display_images']
    cells={z:sorted(m for m in M if rho[m]==z) for z in sorted(set(rho.values()))}
    commutes=all(len({display[m] for m in ms})==1 for ms in cells.values())
    qdisplay={z:display[ms[0]] for z,ms in cells.items()} if commutes else None
    allowed={m:{s['required_actions'][m]} for m in M}
    pre=cell_choices(groups({m:m for m in M}),allowed,'member_identifying_common_action_policy')
    post=cell_choices(groups(rho),allowed,'quotient_common_action_policy')
    original_policy=cell_choices(groups(display),allowed,'original_display_common_action_policy')
    return {'obligation_type':'separate_sections_and_action_policies',
            'exact':len(set(rho[m] for m in M))==len(M),
            'target_sound':all(len({s['target_verdict'][m] for m in ms})==1 for ms in cells.values()),
            'square_commutes':commutes,'quotient_cells':cells,'quotient_display':qdisplay,
            'original_display_section':section_summary(display),
            'quotient_display_section':section_summary(qdisplay) if commutes else None,
            'pre_member_policy':pre,'post_quotient_policy':post,'original_display_policy':original_policy,
            'pre_information':'member_identity','post_information':'quotient_map',
            'common_action_policy_preserved':pre['exists'] and post['exists'],
            'cpre_claim_status':'not_certified'}

def solve(wid:str,s:dict) -> dict:
    letter=wid.split('_')[2]
    if letter=='A':
        c=toy_a(s);v=c['variants']
        checks={'offline_sections_exist':c['offline_section']['exists'],
                'memoryless_fails':not v['memoryless']['full_path_selector_exists'],
                'lookback_1_succeeds':v['lookback_1']['full_path_selector_exists']}
    elif letter=='B':
        c=toy_b(s)
        checks={'nonempty_common_coordinate_supports':bool(c['common_left_support']) and bool(c['common_right_support']),
                'common_edge_choice_fails':not c['choice']['exists']}
    elif letter=='C':
        c=toy_c(s)
        checks={'local_choices_exist':bool(c['locally_reachable_choices']),
                'each_full_future_liftable':c['each_future_liftable'],
                'prefix_conflict':not c['continuation_choice']['exists']}
    elif letter=='D':
        c=toy_d(s);t=c['worlds']['traceable']['policies'];z=c['worlds']['silent']['policies']
        checks={'traceable_memoryless_fails':not t['memoryless']['exists'],
                'traceable_lookback_1_succeeds':t['lookback_1']['exists'],
                'silent_full_history_policy_fails':not z['offline']['exists'],
                'silent_retained_policy_succeeds':z['retained_mode_augmented']['exists'],
                'silent_section_exists':c['worlds']['silent']['original_display_section']['exists']}
    elif letter in ('E','F'):
        c=toy_ef(s)
        checks={'nonexact':not c['exact'],'target_sound':c['target_sound'],'commuting_square':c['square_commutes'],
                'original_section_exists':c['original_display_section']['exists'],
                'quotient_section_exists':c['quotient_display_section'] is not None and c['quotient_display_section']['exists'],
                'pre_policy_exists':c['pre_member_policy']['exists'],
                'post_policy_lost' if letter=='E' else 'post_policy_retained':not c['post_quotient_policy']['exists'] if letter=='E' else c['post_quotient_policy']['exists']}
    else:raise ValueError('unsupported v54 id')
    c['claim_checks']=checks;c['registered_claim_holds']=all(checks.values())
    return c
