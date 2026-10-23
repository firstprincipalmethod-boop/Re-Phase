"""Input contract and typed JSON utilities. MIT; correction candidate 2026-10-23.

No runtime validation relies on assert. This is a finite fixture contract, not a
schema for arbitrary control systems. Unknown fields are rejected, not ignored.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SUITE_VERSION = '2026-10-23'
SCHEMA_VERSION = 2
ROLES = {
 'v53_collapse':'pointwise_nonempty_pathwise_empty',
 'v53_gap_collapse':'empty_lift_without_live_cone_obstruction',
 'v53_unique_lift':'unique_lift_from_multiple_pointwise_candidates',
 'v53_feature_ambiguous_recoverable':'ambiguous_paths_with_recovered_feature',
 'v53_missing_cell':'feature_narrowing_without_recoverability',
 'v53_same_slices_different_edges':'same_surviving_slices_different_path_features',
 'v53_constant_velocity':'constant_velocity_observation_schedule_comparison',
 'v54_toy_A_memoryless_fail':'unique_lifts_no_memoryless_but_lookback_path_selector',
 'v54_toy_B_bridge_conflict':'abstract_member_dependent_common_edge_conflict',
 'v54_toy_C_nonblocking':'prefix_continuation_conflict_nonexistence_only',
 'v54_toy_D_retention_memory':'terminal_action_policy_memory_retention_separation',
 'v54_toy_E_target_sound_not_selector':'target_sound_section_exists_action_policy_lost',
 'v54_toy_F_safe_nonexact':'nonexact_target_sound_action_policy_retained',
}
REQUIRED_IDS = frozenset(ROLES)
SOURCE_DOIS={'Vol.5.3':'10.5281/zenodo.23499738','Vol.5.4':'10.5281/zenodo.23499819'}
SOURCE_SHA={'Vol.5.3':'4a2dd6ed2fa2f93a07d195220f203359b5989137fc8d758022e3a02551d2f6f3','Vol.5.4':'f692f7dc4b129a3647562bdeab020db1aa6c82b894f88fcf4e0fea2c22a0aa01'}

class ContractError(ValueError):
    """An input violates the declared finite contract."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)

def keys(obj: Any, expected: set[str], where: str) -> None:
    require(type(obj) is dict, f'{where}: expected object')
    require(set(obj)==expected, f'{where}: keys differ; missing={sorted(expected-set(obj))}, extra={sorted(set(obj)-expected)}')

def text(x: Any, where: str) -> None:
    require(type(x) is str and bool(x), f'{where}: expected nonempty string')

def integer(x: Any, where: str, minimum: int | None=None) -> None:
    require(type(x) is int, f'{where}: expected integer, not Boolean/float')
    require(minimum is None or x>=minimum, f'{where}: below minimum {minimum}')

def sequence(x: Any, where: str, nonempty: bool=False) -> None:
    require(type(x) is list, f'{where}: expected array')
    require(not nonempty or bool(x), f'{where}: must be nonempty')

def strings(x: Any, where: str, nonempty: bool=False) -> None:
    sequence(x,where,nonempty)
    for y in x:text(y,where)
    require(len(x)==len(set(x)),f'{where}: duplicate entries')

def domain_map(x: Any, domain: set[str], where: str) -> None:
    keys(x,domain,where)
    for v in x.values():text(v,where)

def partition(cells: Any, members: set[str], where: str) -> None:
    require(type(cells) is dict and bool(cells),f'{where}: nonempty cell object required')
    flat=[]
    for name,ms in cells.items():
        text(name,where);strings(ms,where,True);flat.extend(ms)
    require(set(flat)==members and len(flat)==len(members),f'{where}: cells must be a disjoint cover of all members')

def edges(es: Any, left: set[str], right: set[str], where: str) -> None:
    sequence(es,where)
    tuples=[]
    for e in es:
        require(type(e) is list and len(e)==2, f'{where}: edge must be a two-element array')
        require(type(e[0]) is str and type(e[1]) is str,f'{where}: string endpoints required')
        require(e[0] in left and e[1] in right,f'{where}: endpoint outside declared domain')
        tuples.append(tuple(e))
    require(len(tuples)==len(set(tuples)),f'{where}: duplicate edges')

def path_data(s: dict, variant: bool=False) -> None:
    expected={'state_sets','feature','target'}|({'transitions_variant_a','transitions_variant_b'} if variant else {'transitions'})
    keys(s,expected,'path spec')
    states=s['state_sets'];require(type(states) is dict and bool(states),'nonempty state_sets object required')
    n=len(states);keys(states,{f'X{k}' for k in range(n)},'state_sets')
    for k in range(n):strings(states[f'X{k}'],f'X{k}')
    for tk in (('transitions_variant_a','transitions_variant_b') if variant else ('transitions',)):
        keys(s[tk],{f'T{k}' for k in range(n-1)},tk)
        for k in range(n-1):edges(s[tk][f'T{k}'],set(states[f'X{k}']),set(states[f'X{k+1}']),f'{tk}/T{k}')
    strings(s['target'],'target')
    f=s['feature'];require(type(f) is dict,'feature object required')
    kind=f.get('kind')
    if kind=='terminal_state':keys(f,{'kind'},'feature')
    elif kind=='terminal_map':
        keys(f,{'kind','map'},'feature');domain_map(f['map'],set(states[f'X{n-1}']),'terminal map')
    elif kind=='all_branch_equal':
        keys(f,{'kind','labels','equal_value','different_value'},'feature')
        keys(f['labels'],set(states),'branch labels')
        for k in range(n):domain_map(f['labels'][f'X{k}'],set(states[f'X{k}']),f'labels/X{k}')
        text(f['equal_value'],'equal value');text(f['different_value'],'different value')
        require(f['equal_value']!=f['different_value'],'feature output labels must differ')
    else:raise ContractError('unsupported feature kind')

def validate_spec(o: Any) -> None:
    keys(o,{'id','source_volume','source_section','kind','role','status','count_objects','spec','schema_version','suite_version','source'},'spec envelope')
    wid=o['id'];text(wid,'id')
    require(re.fullmatch(r'[A-Za-z0-9_]+',wid) is not None,'unsafe id')
    require(wid in REQUIRED_IDS,'unregistered id')
    lane='v53' if wid.startswith('v53_') else 'v54'
    volume='Vol.5.3' if lane=='v53' else 'Vol.5.4'
    require(o['source_volume']==volume,'id/source_volume mismatch')
    require(o['kind']==('pathwise' if lane=='v53' else 'selector'),'kind/source mismatch')
    require(type(o['schema_version']) is int and o['schema_version']==SCHEMA_VERSION,'schema version mismatch')
    require(o['suite_version']==SUITE_VERSION,'suite version mismatch')
    require(o['role']==ROLES[wid],'role registry mismatch; role is metadata, not a verdict')
    require(o['status']=='correction_candidate','status mismatch')
    text(o['source_section'],'source_section')
    require(type(o['count_objects']) is dict and bool(o['count_objects']),'count_objects required')
    for k,v in o['count_objects'].items():text(k,'count_objects');text(v,'count_objects')
    source=o['source'];keys(source,{'doi','edition','layout','pdf_sha256','relation'},'source')
    require(source['doi']==SOURCE_DOIS[volume] and source['edition']=='2026-10-21','source edition mismatch')
    require(source['pdf_sha256']==SOURCE_SHA[volume],'wrong pinned source PDF hash')
    require(source['layout']==('noheader_r1' if lane=='v53' else 'original_2026-10-21'),'source layout mismatch')
    text(source['layout'],'layout');text(source['relation'],'source relation')
    s=o['spec'];require(type(s) is dict,'spec input must be object')
    if lane=='v53' and wid!='v53_constant_velocity':
        path_data(s,wid=='v53_same_slices_different_edges');return
    if wid=='v53_constant_velocity':
        keys(s,{'horizon','position_domain','velocity_domain','displayed_positions','feature','target','full_schedule','thinned_schedule'},'constant velocity')
        integer(s['horizon'],'horizon',0);require(s['horizon']==2,'this fixture contract uses horizon 2')
        for field in ('position_domain','velocity_domain','displayed_positions','target','full_schedule','thinned_schedule'):
            sequence(s[field],field,field in ('position_domain','velocity_domain','displayed_positions'))
            for x in s[field]:integer(x,field)
        for field in ('position_domain','velocity_domain','target','full_schedule','thinned_schedule'):
            require(len(s[field])==len(set(s[field])),field+': duplicate entries')
        require(len(s['displayed_positions'])==3,'display must have three entries')
        require(s['feature']=='initial_velocity','unsupported constant velocity feature')
        require(set(s['target'])<=set(s['velocity_domain']),'target outside velocity domain')
        for field in ('full_schedule','thinned_schedule'):
            require(set(s[field])<=set(range(3)),field+': observation index outside horizon')
        require(set(s['thinned_schedule'])<set(s['full_schedule']),'thinned schedule must be a strict subset')
        return
    if wid=='v54_toy_A_memoryless_fail':
        keys(s,{'choice_kind','time','variants','displayed_paths','lifts','information_cells'},'Toy A')
        require(s['choice_kind']=='state','Toy A choice_kind')
        integer(s['time'],'time',0)
        require(type(s['displayed_paths']) is dict and bool(s['displayed_paths']),'displayed_paths required')
        members=set(s['displayed_paths']);keys(s['lifts'],members,'lifts')
        n=None
        for m in members:
            text(m,'member')
            for field in ('displayed_paths','lifts'):
                sequence(s[field][m],field,True)
                for v in s[field][m]:text(v,field)
                if n is None:n=len(s[field][m])
                require(len(s[field][m])==n,'all paths/lifts must have same length')
        require(s['time']<n,'time outside horizon')
        require(len({tuple(v) for v in s['displayed_paths'].values()})==len(members),'base paths must be distinct')
        strings(s['variants'],'variants',True)
        require(set(s['variants'])=={'memoryless','lookback_1','causal','offline'},'unsupported or missing selector class')
        keys(s['information_cells'],{'memoryless_t1','lookback_1_t1'},'A information cells')
        require(s['time']==1,'redundant t1 declarations require time=1')
        for name,r in [('memoryless_t1',0),('lookback_1_t1',1)]:
            cells=s['information_cells'][name];partition(cells,members,name)
            declared={frozenset(ms) for ms in cells.values()}
            groups={}
            for m,y in s['displayed_paths'].items():groups.setdefault(tuple(y[max(0,1-r):2]),[]).append(m)
            require(declared=={frozenset(ms) for ms in groups.values()},name+': inconsistent with displayed information')
        return
    if wid=='v54_toy_B_bridge_conflict':
        keys(s,{'choice_kind','time','selector_class','information_cell','left_support','right_support','bridge_edges'},'Toy B')
        require(s['choice_kind']=='abstract_edge','Toy B is abstract edge choice')
        integer(s['time'],'time',0);require(s['selector_class']=='declared_information_partition','B selector class')
        strings(s['left_support'],'left support',True);strings(s['right_support'],'right support',True)
        require(type(s['bridge_edges']) is dict and bool(s['bridge_edges']),'member edges required')
        partition(s['information_cell'],set(s['bridge_edges']),'B cells')
        for m,es in s['bridge_edges'].items():
            text(m,'member');edges(es,set(s['left_support']),set(s['right_support']),'B edges')
            require({e[0] for e in es}==set(s['left_support']) and {e[1] for e in es}==set(s['right_support']),'B declared equal supports do not match member edge projections')
        return
    if wid=='v54_toy_C_nonblocking':
        keys(s,{'choice_kind','time','selector_class','shared_prefix','local_choices','futures','transitions'},'Toy C')
        require(s['choice_kind']=='nonblocking_prefix' and s['selector_class']=='causal','C choice type/class')
        require(type(s['time']) is int and s['time']==1,'Toy C time must be 1')
        text(s['shared_prefix'],'shared_prefix');strings(s['local_choices'],'local choices',True)
        require(type(s['futures']) is dict and bool(s['futures']),'futures must be nonempty')
        for m,f in s['futures'].items():
            text(m,'future');keys(f,{'terminal','required_prefix_choice'},'future')
            text(f['terminal'],'terminal');text(f['required_prefix_choice'],'prefix choice')
        keys(s['transitions'],{'T0','T1'},'C transitions')
        edges(s['transitions']['T0'],{s['shared_prefix']},set(s['local_choices']),'C T0')
        edges(s['transitions']['T1'],set(s['local_choices']),{f['terminal'] for f in s['futures'].values()},'C T1')
        reachable={e[1] for e in s['transitions']['T0']}
        for f in s['futures'].values():
            allowed={a for a,b in s['transitions']['T1'] if b==f['terminal'] and a in reachable}
            require(f['required_prefix_choice'] in allowed,'C redundant prefix choice has no continuation')
        return
    if wid=='v54_toy_D_retention_memory':
        keys(s,{'choice_kind','variants','worlds','display_models','memory_classes'},'Toy D')
        require(s['choice_kind']=='action','D choice_kind')
        require(s['variants']==['traceable_original','silent_original','silent_augmented'],'D variants')
        require(s['display_models']==['original','augmented_retained_mode'],'D display_models')
        strings(s['memory_classes'],'memory_classes',True)
        require(set(s['memory_classes'])=={'memoryless','lookback_1','lookback_2','offline'},'D memory class contract')
        keys(s['worlds'],{'traceable','silent'},'D worlds')
        for world in s['worlds'].values():
            require(type(world) is dict and bool(world),'D empty world')
            n=None
            for m,f in world.items():
                text(m,'member');keys(f,{'tilt_history','mode','required_action'},'D member')
                sequence(f['tilt_history'],'tilt_history',True)
                for v in f['tilt_history']:integer(v,'tilt observation')
                if n is None:n=len(f['tilt_history'])
                require(len(f['tilt_history'])==n,'D history lengths differ')
                text(f['mode'],'mode');text(f['required_action'],'action')
        return
    if wid.startswith(('v54_toy_E','v54_toy_F')):
        keys(s,{'choice_kind','hidden_members','display_images','quotient_map','target_verdict','required_actions','display_quotient','pre_information','post_information'},'Toy E/F')
        strings(s['hidden_members'],'hidden_members',True);members=set(s['hidden_members'])
        for field in ('display_images','quotient_map','target_verdict','required_actions'):domain_map(s[field],members,field)
        require(s['choice_kind']=='action','E/F choice kind')
        require(s['display_quotient']=='identity','only identity display quotient supported')
        require(s['pre_information']=='member_identity' and s['post_information']=='quotient_map','E/F information baseline')
        return
    raise ContractError('missing validator')

def _pairs(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ContractError(f'duplicate JSON key: {k}')
        result[k]=v
    return result

def load_json(path: Path | str) -> Any:
    def bad_constant(s):raise ContractError('non-finite JSON number: '+s)
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream,object_pairs_hook=_pairs,parse_constant=bad_constant)

def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')

def digest(obj: Any) -> str:return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def typed_equal(a: Any,b: Any) -> bool:
    if type(a) is not type(b):return False
    if type(a) is dict:return set(a)==set(b) and all(typed_equal(a[k],b[k]) for k in a)
    if type(a) is list:return len(a)==len(b) and all(typed_equal(x,y) for x,y in zip(a,b))
    return a==b

def load_suite(root: Path | str) -> list[dict]:
    root=Path(root);require(root.is_dir(),'specs directory missing')
    paths=sorted(root.rglob('*.json'));specs=[];seen=set()
    require(len(paths)==len(REQUIRED_IDS),'suite must contain exactly 13 spec files')
    for p in paths:
        require(not p.is_symlink(),'spec symlinks unsupported')
        o=load_json(p);validate_spec(o);wid=o['id']
        require(wid not in seen,'duplicate spec id');seen.add(wid)
        expected=Path('v53' if wid.startswith('v53_') else 'v54')/(wid+'.json')
        require(p.relative_to(root)==expected,'spec filename/bucket/id mismatch')
        require(p.resolve().is_relative_to(root.resolve()),'spec path escapes root')
        specs.append(o)
    require(seen==REQUIRED_IDS,'missing/unexpected suite ids')
    return sorted(specs,key=lambda o:o['id'])
