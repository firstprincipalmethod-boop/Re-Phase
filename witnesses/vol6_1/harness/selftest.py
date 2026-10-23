#!/usr/bin/env python3
"""Positive, malformed-input, role-mutation and pre-write gate tests. MIT."""
from pathlib import Path
import copy,hashlib,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from contract import *
from compute import compute
from golden import compare
from run_all import execute
from independent_check import check


def run():
    specs={s['id']:s for s in load_suite(HERE/'specs')};results=[]
    def case(name,fn):
        try:fn();results.append({'test':name,'status':'PASS'})
        except Exception as e:results.append({'test':name,'status':'FAIL','error':str(e)})
    def ok(x,message='condition failed'):
        if not x:raise ValueError(message)
    def reject(fn):
        try:fn()
        except (ContractError,ValueError,OSError,KeyError):return
        raise ValueError('invalid case was accepted')
    def mutated(wid,fn):
        x=copy.deepcopy(specs[wid]);fn(x);return x
    def invalid(name,wid,fn):case(name,lambda:reject(lambda:validate_spec(mutated(wid,fn))))
    base=compute(specs['v53_collapse'])
    for s in specs.values():case('canonical independent '+s['id'],lambda s=s:check(s,compute(s)))
    for name,fn in [
        ('bool versus int',lambda x:x['computed'].__setitem__('recoverable',0)),
        ('extra null',lambda x:x['computed'].__setitem__('unexpected',None)),
        ('missing key',lambda x:x['computed'].pop('tau_pre')),
        ('wrong outer id',lambda x:x.__setitem__('id','v53_unique_lift')),
        ('wrong source volume',lambda x:x.__setitem__('source_volume','Vol.5.4')),
        ('wrong digest',lambda x:x.__setitem__('spec_sha256','0'*64)),
        ('wrong suite version',lambda x:x.__setitem__('suite_version','old')),
        ('schema int versus float',lambda x:x.__setitem__('schema_version',2.0)),
        ('nested bool versus int',lambda x:x['computed']['claim_checks'].__setitem__('lift_empty',1)),
        ('null versus object',lambda x:x['computed'].__setitem__('tau_pre',None)),
        ('nested extra null',lambda x:x['computed']['tau_pre'].__setitem__('x',None)),
        ('number versus string',lambda x:x['computed'].__setitem__('pt_size','2'))]:
        def test(fn=fn):
            other=copy.deepcopy(base);fn(other);ok(compare(base,other)[0]=='fail')
        case('strict comparator '+name,test)
    case('strict comparator same',lambda:ok(compare(base,copy.deepcopy(base))[0]=='pass'))
    case('strict comparator missing snapshot',lambda:ok(compare(base,None)[0]=='no-golden'))
    def missing_null():
        ok(not typed_equal({'a':None},{}));ok(not typed_equal([False],[0]));ok(not typed_equal(1,1.0))
    case('strict recursive missing/null/type',missing_null)
    for name,raw in [('duplicate JSON key','{"a":1,"a":2}'),('NaN','{"a":NaN}'),('Infinity','{"a":Infinity}')]:
        def bad_json(raw=raw):
            with tempfile.TemporaryDirectory() as td:
                p=Path(td)/'bad.json';p.write_text(raw);reject(lambda:load_json(p))
        case('strict JSON '+name,bad_json)
    a='v54_toy_A_memoryless_fail';b='v54_toy_B_bridge_conflict';c='v54_toy_C_nonblocking';d='v54_toy_D_retention_memory';e='v54_toy_E_target_sound_not_selector';f='v54_toy_F_safe_nonexact';g='v53_gap_collapse';v='v53_constant_velocity'
    invalid('unsafe ID',a,lambda x:x.__setitem__('id','../escape'))
    invalid('unknown ID',a,lambda x:x.__setitem__('id','unknown'))
    invalid('wrong pinned source hash',a,lambda x:x['source'].__setitem__('pdf_sha256','0'*64))
    invalid('wrong source layout',a,lambda x:x['source'].__setitem__('layout','headered'))
    invalid('volume mismatch',a,lambda x:x.__setitem__('source_volume','Vol.5.3'))
    invalid('kind mismatch',a,lambda x:x.__setitem__('kind','pathwise'))
    invalid('extra envelope output',a,lambda x:x.__setitem__('computed',{}))
    invalid('unused stage X99',g,lambda x:x['spec']['state_sets'].__setitem__('X99',['q']))
    invalid('wrong stage X2 to X99',g,lambda x:x['spec']['state_sets'].__setitem__('X99',x['spec']['state_sets'].pop('X2')))
    invalid('unused transition T2',g,lambda x:x['spec']['transitions'].__setitem__('T2',[]))
    invalid('edge outside state domain',g,lambda x:x['spec']['transitions'].__setitem__('T0',[['bad','m']]))
    invalid('duplicate state',g,lambda x:x['spec']['state_sets']['X0'].append('p'))
    invalid('extra feature key',g,lambda x:x['spec']['feature'].__setitem__('unused',True))
    invalid('bool horizon',v,lambda x:x['spec'].__setitem__('horizon',True))
    invalid('bad schedule index',v,lambda x:x['spec'].__setitem__('thinned_schedule',[0,99]))
    invalid('unused velocity field',v,lambda x:x['spec'].__setitem__('transitions',{}))
    invalid('duplicate observation index',v,lambda x:x['spec'].__setitem__('full_schedule',[0,1,2,2]))
    invalid('A stale cells with equal display',a,lambda x:x['spec']['displayed_paths'].__setitem__('path1',list(x['spec']['displayed_paths']['path0'])))
    invalid('A stale t1 cell grouping',a,lambda x:x['spec']['information_cells']['lookback_1_t1'].__setitem__('extra',['path0']))
    invalid('A unknown class',a,lambda x:x['spec']['variants'].append('magic'))
    invalid('A path length mismatch',a,lambda x:x['spec']['lifts']['path0'].append('extra'))
    invalid('B additional overlapping cell',b,lambda x:x['spec']['information_cell'].__setitem__('extra',['u']))
    invalid('B uncovered member',b,lambda x:x['spec'].__setitem__('information_cell',{'only':['u']}))
    invalid('B empty cell',b,lambda x:x['spec']['information_cell'].__setitem__('extra',[]))
    invalid('B unsupported edge',b,lambda x:x['spec']['bridge_edges']['u'].append(['bad','B']))
    invalid('B redundant support mismatch',b,lambda x:x['spec']['left_support'].append('Z'))
    invalid('C wrong declared prefix choice',c,lambda x:x['spec']['futures']['alpha'].__setitem__('required_prefix_choice','n'))
    invalid('C extra transition key',c,lambda x:x['spec']['transitions'].__setitem__('T2',[]))
    invalid('D extra memory class',d,lambda x:x['spec']['memory_classes'].append('unbounded_other'))
    invalid('D missing action',d,lambda x:x['spec']['worlds']['silent']['stable'].pop('required_action'))
    invalid('D unequal history length',d,lambda x:x['spec']['worlds']['silent']['stable']['tilt_history'].append(1))
    for wid in (e,f):
        for field in ('quotient_map','display_images','target_verdict','required_actions'):
            invalid(wid+' extra '+field,wid,lambda x,field=field:x['spec'][field].__setitem__('outside','extra'))
            invalid(wid+' missing '+field,wid,lambda x,field=field:x['spec'][field].pop('x0'))
    def c_success():
        x=mutated(c,lambda x:x['spec']['transitions']['T1'].append(['m','b']))
        z=compute(x)['computed'];check(x,compute(x))
        ok(z['continuation_choice']['exists']);ok(z['continuation_choice']['table'] is not None)
        ok(z['full_path_selector_exists'] is None and z['full_path_selector_status']=='not_checked')
        ok(not z['registered_claim_holds'])
    case('C positive local choice does not certify full path',c_success)
    def e_mutation():
        x=mutated(e,lambda x:x['spec'].__setitem__('required_actions',{'x0':'n','x1':'n'}));r=compute(x);check(x,r)
        ok(r['computed']['post_quotient_policy']['exists']);ok(not r['computed']['registered_claim_holds'])
    case('E changed actions change claims, not role metadata',e_mutation)
    def f_mutation():
        x=mutated(f,lambda x:x['spec']['required_actions'].__setitem__('x1','r'));r=compute(x);check(x,r)
        ok(not r['computed']['post_quotient_policy']['exists'] and not r['computed']['registered_claim_holds'])
    case('F incompatible action changes computed claims',f_mutation)
    def false_thinning():
        x=mutated(v,lambda x:x['spec'].__setitem__('target',[]));r=compute(x);check(x,r)
        ok(not r['computed']['full_context']['recoverable'] and not r['computed']['thinned_context']['recoverable'])
        ok(not r['computed']['observation_thinning_confirmed'])
    case('false equals false is not sufficient thinning',false_thinning)
    def all_times():
        x=mutated(a,lambda x:x['spec']['lifts']['path0'].__setitem__(0,'changed0'))
        ok(compare(compute(x),compute(specs[a]))[0]=='fail')
    case('A off-tested-time components now affect output',all_times)
    def b_multicell():
        x=mutated(b,lambda x:x['spec'].__setitem__('information_cell',{'u':['u'],'v':['v']}));r=compute(x);check(x,r)
        ok(len(r['computed']['choice']['cells'])==2 and r['computed']['choice']['exists']);ok(not r['computed']['registered_claim_holds'])
    case('B all valid information cells are evaluated',b_multicell)
    def b_multiplicity():
        x=mutated(b,lambda x:x['spec']['bridge_edges']['u'].append(['A','D']));r=compute(x);check(x,r)
        ok(r['computed']['same_member_left_supports'])
    case('B supports are sets, not endpoint multiplicities',b_multiplicity)
    def gap_role():
        x=mutated(g,lambda x:x['spec']['transitions'].__setitem__('T0',[['p','m']]))
        z=compute(x)['computed'];ok(z['live_cone_obstructions']==[1] and not z['registered_claim_holds'])
    case('gap role computed from actual cone obstruction',gap_role)
    def ef_sections():
        for wid,n in ((e,0),(f,1)):
            z=compute(specs[wid])['computed'];ok(z['original_display_section']['count']==2 and z['quotient_display_section']['count']==1 and z['pre_member_policy']['count']==1 and z['post_quotient_policy']['count']==n)
    case('E F source section and policy counts',ef_sections)
    def source_counts():
        z={wid:compute(s)['computed'] for wid,s in specs.items()}
        ok((z['v53_unique_lift']['pt_size'],z['v53_unique_lift']['lift_size'])==(8,1))
        ok((z['v53_feature_ambiguous_recoverable']['pt_size'],z['v53_feature_ambiguous_recoverable']['lift_size'])==(27,2))
        ok(z[g]['pt_size']==1 and z[g]['tau_pre']['k']==1 and z[g]['live_cone_obstructions']==[])
        ss=z['v53_same_slices_different_edges'];ok(ss['same_surviving_slices'] and ss['variant_a']['lift_size']==2 and ss['variant_b']['lift_size']==8)
        ok([x['lift_size'] for x in z[v]['schedules']]==[33,3,3,3,1,1,1,1])
        ok(z[v]['minimal_sufficient_schedules']==[[0,1],[0,2],[1,2]])
    case('current source examples exact finite summaries',source_counts)
    def gate_case(kind):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);sp=td/'specs';gd=td/'golden';out=td/'output'
            shutil.copytree(HERE/'specs',sp);shutil.copytree(HERE/'golden',gd)
            if kind=='duplicate':shutil.copyfile(sp/'v53/v53_collapse.json',sp/'v53/duplicate.json')
            elif kind=='missing':(sp/'v53/v53_collapse.json').unlink()
            elif kind=='path_id':
                p=sp/'v53/v53_collapse.json';x=json.loads(p.read_text());x['id']='../escape';p.write_text(json.dumps(x))
            elif kind=='wrong_filename':(sp/'v53/v53_collapse.json').rename(sp/'v53/other.json')
            elif kind=='golden_outer':
                p=gd/'v53/v53_collapse.golden.json';x=json.loads(p.read_text());x['id']='incorrect';p.write_text(json.dumps(x))
            elif kind=='golden_type':
                p=gd/'v53/v53_collapse.golden.json';x=json.loads(p.read_text());x['computed']['recoverable']=0;p.write_text(json.dumps(x))
            elif kind=='extra_golden':(gd/'extra.json').write_text('{}')
            elif kind=='missing_golden':(gd/'v53/v53_collapse.golden.json').unlink()
            elif kind=='valid_mutation':
                p=sp/'v53/v53_collapse.json';x=json.loads(p.read_text());x['spec']['target']=[];p.write_text(json.dumps(x))
            reject(lambda:execute(sp,gd,out,HERE/'suite_manifest.json'))
            ok(not out.exists(),'failed gate wrote output')
            ok(not (td/'escape.out.json').exists(),'path traversal output created')
    for kind in ('duplicate','missing','path_id','wrong_filename','golden_outer','golden_type','extra_golden','missing_golden','valid_mutation'):case('pre-write gate '+kind,lambda kind=kind:gate_case(kind))
    fail=[r for r in results if r['status']!='PASS']
    result={'suite_version':SUITE_VERSION,'mode':'optimized' if not __debug__ else 'normal','tests':len(results),'passed':len(results)-len(fail),'failed':len(fail),'status':'PASS' if not fail else 'FAIL','results':results}
    return result

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=run()
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(canonical_bytes(r))
    print(json.dumps({k:v for k,v in r.items() if k!='results'},indent=2))
    for x in r['results']:
        if x['status']=='FAIL':print(x)
    return 0 if r['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
