#!/usr/bin/env python3
"""Independent finite evidence checker (MIT).

Imports only input-contract/JSON utilities, never compute*, golden, or stored
outputs as expectations. Re-enumerates products and finite tables from inputs.
The default CLI requires all thirteen registered specification/result pairs.
This is a second implementation in the same authoring session, not external review.
"""
from __future__ import annotations
from itertools import product,combinations
from collections import Counter
from math import prod
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from contract import (load_suite, load_json, validate_spec, REQUIRED_IDS, ROLES,
                      SUITE_VERSION, SCHEMA_VERSION, ContractError, canonical_bytes)


def canon(o):return json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def equal(a,b):return canon(a)==canon(b)
def req(condition,message):
    if not condition:raise ValueError(message)

def expect(actual,expected,where):req(equal(actual,expected),'independent mismatch: '+where)
def arr(x):
    if isinstance(x,(tuple,list)):return [arr(v) for v in x]
    return x

def summary(F,T,h,B):
    F=[sorted(f) for f in F];n=len(F)-1
    def paths(i,j):
        return [p for p in product(*F[i:j+1]) if all((p[k-i],p[k-i+1]) in T[k] for k in range(i,j))]
    pts=list(product(*F));lifts=paths(0,n)
    R=[{p[-1] for p in paths(0,k)} for k in range(n+1)]
    S=[{p[0] for p in paths(k,n)} for k in range(n+1)]
    V=[{p[k] for p in lifts} for k in range(n+1)]
    bridges=[{(p[k],p[k+1]) for p in lifts} for k in range(n)]
    # Verify exact bridge projections equal forward/backward linking, separately.
    req(all(bridges[k]=={(a,b) for a,b in T[k] if a in R[k] and b in S[k+1]} for k in range(n)),'bridge characterization')
    hp=sorted({h(p) for p in pts});hl=sorted({h(p) for p in lifts});hist=Counter(h(p) for p in lifts)
    tau=next((k for k in range(n+1) if len(paths(0,k))==0),None)
    return {'pt_size':len(pts),'lift_size':len(lifts),'lift_status':'infeasible' if len(lifts)==0 else 'unique' if len(lifts)==1 else 'ambiguous',
            'lifts':arr(sorted(lifts)),'fibers':arr(F), 'forward_reachable':arr([sorted(r) for r in R]),
            'backward_survivable':arr([sorted(s) for s in S]),'surviving_slices':arr([sorted(v) for v in V]),
            'viable_bridges':arr([sorted(b) for b in bridges]),
            'live_cone_obstructions':[k for k in range(n) if len(R[k])>0 and len(S[k+1])>0 and len(bridges[k])==0],
            'retrospective_break':[k for k in range(n) if len(bridges[k])==0],
            'tau_pre':{'status':'finite' if tau is not None else 'no_failure','k':tau},
            'feature_image_pt':hp,'feature_image_lift':hl,'feature_lift_counts':[{'value':v,'count':hist[v]} for v in hl],
            'target':sorted(B),'target_check':'vacuous_empty_lift' if not lifts else 'within_target' if all(h(p) in B for p in lifts) else 'outside_target',
            'recoverable':len(lifts)>0 and all(h(p) in B for p in lifts)}

def source_h(f):
    def h(p):
        if f['kind']=='terminal_state':return p[-1]
        if f['kind']=='terminal_map':return f['map'][p[-1]]
        labels=[f['labels']['X'+str(k)][v] for k,v in enumerate(p)]
        return f['equal_value'] if all(v==labels[0] for v in labels) else f['different_value']
    return h

def path_truth(s, field='transitions'):
    F=[s['state_sets']['X'+str(k)] for k in range(len(s['state_sets']))]
    T=[set(map(tuple,s[field]['T'+str(k)])) for k in range(len(F)-1)]
    return summary(F,T,source_h(s['feature']),s['target'])

def key(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),sort_keys=True)
def cells_of(values):
    members=sorted(values);out={}
    for m in members:
        cid=key(values[m]);out[cid]=sorted(n for n in members if equal(values[n],values[m]))
    return dict(sorted(out.items()))

def choice_truth(cells,allowed,obligation):
    records={};all_common=[]
    for cid,ms in sorted(cells.items()):
        universe=sorted(set.union(*[set(allowed[m]) for m in ms]))
        common=[a for a in universe if all(a in allowed[m] for m in ms)]
        records[cid]={'members':sorted(ms),'allowed_by_member':{m:arr(sorted(allowed[m])) for m in sorted(ms)},'common_choices':arr(common),'conflict':len(common)==0}
        all_common.append(common)
    mappings=list(product(*all_common))
    table={cid:arr(v) for cid,v in zip(sorted(cells),mappings[0])} if mappings else None
    return {'obligation_type':obligation,'cells':records,'exists':len(mappings)>0,'count':len(mappings),'table':table}

def section_truth(display):
    cells=cells_of(display);maps=list(product(*cells.values()))
    table=dict(zip(cells,maps[0])) if maps else None
    return {'count':len(maps),'exists':bool(maps),'table':table,'fibers':cells}

def information(y,k,cls):
    if cls=='offline':return list(y)
    start=0 if cls=='causal' else max(0,k-(0 if cls=='memoryless' else int(cls[len('lookback_'):])) )
    return y[start:k+1]


class IndependentMismatch(ValueError):
    """An actual result differs from the independently derived full contract."""


def compare_complete(actual, expected, path='$'):
    """Recursive key/type/value equality; no missing/null or bool/int coercion."""
    if type(actual) is not type(expected):
        raise IndependentMismatch(path+': type mismatch')
    if type(expected) is dict:
        if set(actual) != set(expected):
            raise IndependentMismatch(path+': key set mismatch; missing='+
                repr(sorted(set(expected)-set(actual)))+' extra='+
                repr(sorted(set(actual)-set(expected))))
        for name in sorted(expected):
            compare_complete(actual[name],expected[name],path+'/'+str(name))
    elif type(expected) is list:
        if len(actual) != len(expected):
            raise IndependentMismatch(path+': array length mismatch')
        for i,(a,b) in enumerate(zip(actual,expected)):
            compare_complete(a,b,path+'/'+str(i))
    elif actual != expected:
        raise IndependentMismatch(path+': value mismatch')


def derive_expected_record(spec):
    """Build the COMPLETE expected record without receiving the actual result.

    Input validation/constants are shared. All numerical/set-valued computations
    below use this module's separate complete-product/finite-table enumeration.
    Fixed scope declarations are contract values, not new mathematical results.
    """
    validate_spec(spec)
    wid=spec['id'];s=spec['spec']
    if wid.startswith('v53_'):
        if wid=='v53_constant_velocity':
            n=s['horizon'];X=set(product(s['position_domain'],s['velocity_domain']))
            T=[{(a,b) for a in X for b in X if b[0]-a[0]==a[1] and b[1]==a[1]} for _ in range(n)]
            rows=[]
            for size in range(n+2):
                for J in combinations(range(n+1),size):
                    F=[{x for x in X if k not in J or x[0]==s['displayed_positions'][k]} for k in range(n+1)]
                    truth=summary(F,T,lambda p:p[0][1],s['target'])
                    analytic=[[(q+k*v,v) for k in range(n+1)] for q,v in X
                        if all((q+k*v,v) in X for k in range(n+1))
                        and all(q+k*v==s['displayed_positions'][k] for k in J)]
                    expect(truth['lifts'],arr(sorted(analytic)),'velocity closed form')
                    rows.append({'schedule':list(J),**truth})
            good=[r['schedule'] for r in rows if r['recoverable']]
            minimal=[j for j in good if all(not(set(k)<set(j)) for k in good)]
            full=next(r for r in rows if r['schedule']==sorted(s['full_schedule']))
            thin=next(r for r in rows if r['schedule']==sorted(s['thinned_schedule']))
            success=full['recoverable'] and thin['recoverable'] and set(thin['schedule'])<set(full['schedule'])
            c={'obligation_type':'initial_velocity_recoverability','state_dimension':2,
               'state_stage_count':n+1,'schedules':rows,'minimal_sufficient_schedules':minimal,
               'full_context':full,'thinned_context':thin,'observation_thinning_confirmed':success,
               'intermediate_state_removed':False}
            checks={'full_context_recovers':full['recoverable'],'thinner_context_recovers':success,
                'no_single_observation_recovers':all(not r['recoverable'] for r in rows if len(r['schedule'])==1),
                'every_pair_recovers':all(r['recoverable'] for r in rows if len(r['schedule'])==2)}
        elif wid=='v53_same_slices_different_edges':
            a=path_truth(s,'transitions_variant_a');b=path_truth(s,'transitions_variant_b')
            c={'obligation_type':'path_feature_recoverability_comparison','variant_a':a,'variant_b':b,
               'same_input_fibers':a['fibers']==b['fibers'],
               'same_surviving_slices':a['surviving_slices']==b['surviving_slices'],
               'different_viable_bridges':a['viable_bridges']!=b['viable_bridges']}
            checks={'nonempty_both':a['lift_size']>0 and b['lift_size']>0,
                'same_surviving_slices':a['surviving_slices']==b['surviving_slices'],
                'different_lifts':a['lifts']!=b['lifts'],
                'different_features':a['feature_image_lift']!=b['feature_image_lift'],
                'a_recovers_b_does_not':a['recoverable'] and not b['recoverable']}
        else:
            c={'obligation_type':'path_feature_recoverability',**path_truth(s)}
            if wid=='v53_collapse':
                checks={'pointwise_nonempty':c['pt_size']>0,'lift_empty':c['lift_size']==0,'not_recoverable':not c['recoverable']}
            elif wid=='v53_gap_collapse':
                checks={'pointwise_nonempty':c['pt_size']>0,'lift_empty':c['lift_size']==0,'live_cone_obstructions_absent':len(c['live_cone_obstructions'])==0}
            elif wid=='v53_unique_lift':
                checks={'multiple_pointwise_candidates':c['pt_size']>1,'unique_lift':c['lift_size']==1,'recovers':c['recoverable']}
            elif wid=='v53_feature_ambiguous_recoverable':
                checks={'ambiguous_paths':c['lift_size']>1,'feature_recovers':c['recoverable']}
            elif wid=='v53_missing_cell':
                checks={'nonempty_lift':c['lift_size']>0,'strict_feature_narrowing':set(c['feature_image_lift'])<set(c['feature_image_pt']),'not_recoverable':not c['recoverable']}
            else:
                raise ContractError('unsupported v53 identifier')
    else:
        letter=wid.split('_')[2]
        if letter=='A':
            variants={};n=len(next(iter(s['lifts'].values())))
            # Expected class set is validated in the INPUT contract, never in c.
            for cls in sorted(s['variants']):
                compatible=all(s['lifts'][m][k]==s['lifts'][z][k]
                    for m in s['lifts'] for z in s['lifts'] for k in range(n)
                    if information(s['displayed_paths'][m],k,cls)==information(s['displayed_paths'][z],k,cls))
                per_time=[]
                for k in range(n):
                    cells=cells_of({m:information(y,k,cls) for m,y in s['displayed_paths'].items()})
                    per_time.append({'time':k,**choice_truth(cells,{m:{p[k]} for m,p in s['lifts'].items()},'state_component')})
                variants[cls]={'full_path_selector_exists':compatible,'selector_count':int(compatible),
                    'per_time':per_time,'selector_tables':[x['table'] for x in per_time] if compatible else None,
                    'selected_paths':dict(sorted(s['lifts'].items())) if compatible else None}
            c={'obligation_type':'all_time_path_selector_on_given_unique_lifts','variants':variants,
               'offline_section':section_truth(s['displayed_paths'])}
            checks={'offline_sections_exist':c['offline_section']['exists'],
                'memoryless_fails':not variants['memoryless']['full_path_selector_exists'],
                'lookback_1_succeeds':variants['lookback_1']['full_path_selector_exists']}
        elif letter=='B':
            allowed={m:set(map(tuple,es)) for m,es in s['bridge_edges'].items()}
            choice=choice_truth(s['information_cell'],allowed,'abstract_edge_choice')
            left=sorted(x for x in s['left_support'] if all(any(a==x for a,b in es) for es in allowed.values()))
            right=sorted(x for x in s['right_support'] if all(any(b==x for a,b in es) for es in allowed.values()))
            c={'obligation_type':'abstract_member_dependent_edge_choice','choice':choice,
               'common_left_support':left,'common_right_support':right,
               'same_member_left_supports':all({a for a,b in es}==set(left) for es in allowed.values()),
               'full_path_selector_status':'not_checked','fixed_transition_bridge_realization_claimed':False}
            checks={'nonempty_common_coordinate_supports':bool(left) and bool(right),
                'common_edge_choice_fails':not choice['exists']}
        elif letter=='C':
            reach={b for a,b in s['transitions']['T0'] if a==s['shared_prefix']}
            allowed={m:{x for x in reach if [x,f['terminal']] in s['transitions']['T1']}
                for m,f in s['futures'].items()}
            choice=choice_truth({'shared_prefix':sorted(s['futures'])},allowed,'one_prefix_continuation_choice')
            liftable=all(bool(a) for a in allowed.values())
            c={'obligation_type':'prefix_nonexistence_certificate_only','locally_reachable_choices':sorted(reach),
               'continuation_choice':choice,'each_future_liftable':liftable,
               'full_path_selector_exists':None if choice['exists'] else False,
               'full_path_selector_status':'not_checked' if choice['exists'] else 'ruled_out_by_prefix_conflict',
               'general_controller_synthesis_claimed':False}
            checks={'local_choices_exist':bool(reach),'each_full_future_liftable':liftable,'prefix_conflict':not choice['exists']}
        elif letter=='D':
            worlds={}
            for name,w in sorted(s['worlds'].items()):
                allowed={m:{d['required_action']} for m,d in w.items()};policies={}
                for cls in sorted(s['memory_classes']):
                    cells=cells_of({m:information(d['tilt_history'],len(d['tilt_history'])-1,cls) for m,d in w.items()})
                    policies[cls]=choice_truth(cells,allowed,'terminal_common_action_policy')
                aug={m:[d['tilt_history'],d['mode']] for m,d in w.items()}
                policies['retained_mode_augmented']=choice_truth(cells_of(aug),allowed,'terminal_common_action_policy')
                worlds[name]={'policies':policies,
                    'original_display_section':section_truth({m:d['tilt_history'] for m,d in w.items()}),
                    'augmented_display_section':section_truth(aug)}
            c={'obligation_type':'terminal_action_policy_not_path_section','worlds':worlds,
               'retained_mode_is_additional_information':True,'closed_loop_guarantee_claimed':False}
            t=worlds['traceable']['policies'];z=worlds['silent']['policies']
            checks={'traceable_memoryless_fails':not t['memoryless']['exists'],
                'traceable_lookback_1_succeeds':t['lookback_1']['exists'],
                'silent_full_history_policy_fails':not z['offline']['exists'],
                'silent_retained_policy_succeeds':z['retained_mode_augmented']['exists'],
                'silent_section_exists':worlds['silent']['original_display_section']['exists']}
        elif letter in ('E','F'):
            members=s['hidden_members'];rho=s['quotient_map'];display=s['display_images']
            cells={z:sorted(m for m in members if rho[m]==z) for z in sorted(set(rho.values()))}
            exact=all(rho[m]!=rho[z] for i,m in enumerate(members) for z in members[i+1:])
            sound=all(s['target_verdict'][m]==s['target_verdict'][z] for m in members for z in members if rho[m]==rho[z])
            commutes=all(display[m]==display[z] for m in members for z in members if rho[m]==rho[z])
            qp={z:display[ms[0]] for z,ms in cells.items()} if commutes else None
            allowed={m:{s['required_actions'][m]} for m in members}
            pre=choice_truth(cells_of({m:m for m in members}),allowed,'member_identifying_common_action_policy')
            post=choice_truth(cells_of(rho),allowed,'quotient_common_action_policy')
            original=choice_truth(cells_of(display),allowed,'original_display_common_action_policy')
            c={'obligation_type':'separate_sections_and_action_policies','exact':exact,
               'target_sound':sound,'square_commutes':commutes,'quotient_cells':cells,'quotient_display':qp,
               'original_display_section':section_truth(display),
               'quotient_display_section':section_truth(qp) if commutes else None,
               'pre_member_policy':pre,'post_quotient_policy':post,'original_display_policy':original,
               'pre_information':'member_identity','post_information':'quotient_map',
               'common_action_policy_preserved':pre['exists'] and post['exists'],
               'cpre_claim_status':'not_certified'}
            checks={'nonexact':not exact,'target_sound':sound,'commuting_square':commutes,
                'original_section_exists':c['original_display_section']['exists'],
                'quotient_section_exists':commutes and c['quotient_display_section']['exists'],
                'pre_policy_exists':pre['exists'],
                'post_policy_lost' if letter=='E' else 'post_policy_retained':
                    not post['exists'] if letter=='E' else post['exists']}
        else:
            raise ContractError('unsupported v54 identifier')
    c['claim_checks']=checks;c['registered_claim_holds']=all(checks.values())
    return {'id':wid,'schema_version':SCHEMA_VERSION,'suite_version':SUITE_VERSION,
            'source_volume':spec['source_volume'],'kind':spec['kind'],'role_label':ROLES[wid],
            'spec_sha256':hashlib.sha256(canonical_bytes(spec)).hexdigest(),'computed':c}


def check(spec, record):
    """Check one in-memory record. This is NOT a complete-suite CLI verdict.

    Used by freeze_candidate and by primary selftests, including valid mutations
    whose registered claim is false. A consistent false claim is reported, not
    changed to true; freeze_candidate separately requires all registered claims.
    """
    expected=derive_expected_record(spec)
    compare_complete(record,expected)
    return {'id':spec['id'],'status':'PASS_INDEPENDENT_FINITE_EVIDENCE',
            'claim_check_count':len(expected['computed']['claim_checks']),
            'registered_claim_holds':expected['computed']['registered_claim_holds'],
            'comparison':'complete_record_keys_types_values'}


# Coverage is generated from expectations, not from fields surviving in an actual output.
FIXED_SCOPE_KEYS=frozenset({'obligation_type','cpre_claim_status','pre_information',
    'post_information','full_path_selector_status','general_controller_synthesis_claimed',
    'fixed_transition_bridge_realization_claimed','retained_mode_is_additional_information',
    'closed_loop_guarantee_claimed','intermediate_state_removed','state_dimension'})


def coverage_for(expected):
    entries=[]
    def visit(value, path, inside_computed=False, field=None):
        category=('CONTRACT_VALIDATION' if not inside_computed or field in FIXED_SCOPE_KEYS
                  or type(value) in (dict,list) else 'INDEPENDENT_DERIVATION')
        # Toy C status is derived from an independently computed conflict, with
        # its allowed success boundary also restricted by a fixed contract.
        if field=='full_path_selector_status' and expected['id']=='v54_toy_C_nonblocking':
            category='INDEPENDENT_DERIVATION_WITH_CONTRACT_BOUNDARY'
        entries.append({'path':path,'json_type':type(value).__name__,'validation':category})
        if type(value) is dict:
            for k in sorted(value):
                escaped=k.replace('~','~0').replace('/','~1')
                visit(value[k],path+'/'+escaped,inside_computed or k=='computed',k)
        elif type(value) is list:
            for i,x in enumerate(value):visit(x,path+'/'+str(i),inside_computed,field)
    visit(expected,'')
    return {'id':expected['id'],'expected_record_paths':entries,
            'all_actual_record_paths_compared':True,'unclassified_expected_paths':0}


def _inventory(root, expected, label, optional=frozenset()):
    root=Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ContractError(label+': directory missing or symbolic link')
    files=set()
    for p in root.rglob('*'):
        if p.is_symlink():raise ContractError(label+': symbolic links unsupported')
        if p.is_file():
            if not p.resolve().is_relative_to(root.resolve()):
                raise ContractError(label+': path escapes root')
            files.add(p.relative_to(root).as_posix())
    if not expected<=files or not files<=expected|set(optional):
        raise ContractError(label+': file set mismatch; missing='+repr(sorted(expected-files))+
                            ' extra='+repr(sorted(files-expected-set(optional))))
    return files


def validate_complete_suite(specs_root, results_root):
    expected_specs={('v53' if w.startswith('v53_') else 'v54')+'/'+w+'.json' for w in REQUIRED_IDS}
    expected_results={('v53' if w.startswith('v53_') else 'v54')+'/'+w+'.out.json' for w in REQUIRED_IDS}
    _inventory(specs_root,expected_specs,'specs')
    specs=load_suite(specs_root)  # shared INPUT validation only, no primary calculation
    _inventory(results_root,expected_results,'results',
        frozenset({'run_summary.json','table_v53.csv','table_v54.csv','table_v54_choices.csv'}))
    docs={}
    # Load and validate every envelope before deriving or reporting any PASS.
    for spec in specs:
        wid=spec['id'];lane='v53' if wid.startswith('v53_') else 'v54'
        p=Path(results_root)/lane/(wid+'.out.json');doc=load_json(p)
        if type(doc) is not dict or set(doc)!= {'result','verification'}:
            raise ContractError(wid+': generated document must contain result and verification only')
        result=doc['result']
        if type(result) is not dict or result.get('id')!=wid:
            raise ContractError(wid+': result filename/lane/ID mismatch')
        docs[wid]=doc
    return specs,docs


def verify_suite(specs_root,results_root):
    specs,docs=validate_complete_suite(specs_root,results_root)
    rows=[];coverage=[]
    for spec in specs:
        wid=spec['id'];expected=derive_expected_record(spec);doc=docs[wid]
        compare_complete(doc['result'],expected,'$/result')
        compare_complete(doc['verification'],{
            'strict_golden':'pass','finite_claims':'pass',
            'scope':'fixed_finite_fixture_not_general_proof'},'$/verification')
        # The CLI checks documents emitted by the fixed successful gate. It does
        # not independently rerun that gate or authenticate its historical execution.
        if not expected['computed']['registered_claim_holds']:
            raise IndependentMismatch(wid+': successful generated document has a false registered claim')
        rows.append({'id':wid,'status':'PASS_INDEPENDENT_FINITE_EVIDENCE',
                     'claim_check_count':len(expected['computed']['claim_checks']),
                     'registered_claim_holds':True,'comparison':'complete_record_keys_types_values'})
        coverage.append(coverage_for(expected))
    return {'suite_version':SUITE_VERSION,'status':'PASS_INDEPENDENT_FINITE_EVIDENCE',
            'witness_count':len(rows),'scope':'complete fixed suite; independent calculations with shared input validation; not external review',
            'results':rows}, {
                'schema':'rephase.independent-coverage.v1','suite_version':SUITE_VERSION,
                'records':coverage,
                'generated_document_wrapper':'CONTRACT_VALIDATION; checked label, not authenticated primary-gate replay',
                'csv_and_run_summary':'PRIMARY_GOLDEN_REGRESSION_AND_REGENERATION; not numerical expectations for this checker',
                'no_primary_compute_or_golden_import':True}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specs',type=Path,required=True)
    parser.add_argument('--results',type=Path,required=True)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--coverage-out',type=Path)
    args=parser.parse_args(argv)
    try:
        # Never overwrite an input with a report, including on failure.
        destinations=[p.resolve() for p in (args.out,args.coverage_out) if p is not None]
        if len(destinations)!=len(set(destinations)):
            raise ContractError('report destinations must be distinct')
        for dest in destinations:
            if any(dest==root.resolve() or dest.is_relative_to(root.resolve())
                   for root in (args.specs,args.results)):
                raise ContractError('report destination overlaps protected input')
        result,coverage=verify_suite(args.specs,args.results)
        for path,data in ((args.out,result),(args.coverage_out,coverage)):
            if path is not None:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(canonical_bytes(data))
    except IndependentMismatch as exc:
        print(json.dumps({'status':'FAIL_INDEPENDENT_MISMATCH','error':str(exc)},ensure_ascii=False))
        return 3
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'FAIL_INPUT_CONTRACT','error':str(exc)},ensure_ascii=False))
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
