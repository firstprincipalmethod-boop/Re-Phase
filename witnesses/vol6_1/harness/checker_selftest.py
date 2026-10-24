#!/usr/bin/env python3
"""MIT. Adverse-input tests OF the auxiliary checker, separate from selftest.py.

Named tests exercise public CLI inventory/JSON errors, direct check() evidence
mutations without a pinned-hash shortcut, and freeze_candidate's shared-check
call path. These are test cases, not new mathematical witness models.
"""
from __future__ import annotations
from pathlib import Path
import argparse,copy,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from contract import load_suite,load_json,canonical_bytes,SUITE_VERSION
from independent_check import check,derive_expected_record,compare_complete,IndependentMismatch

A='v54_toy_A_memoryless_fail';B='v54_toy_B_bridge_conflict'
C='v54_toy_C_nonblocking';D='v54_toy_D_retention_memory'
E='v54_toy_E_target_sound_not_selector';F='v54_toy_F_safe_nonexact'
G='v53_gap_collapse';V='v53_constant_velocity'


def run():
    specs={s['id']:s for s in load_suite(HERE/'specs')}
    records={w:load_json(HERE/'generated'/('v53' if w.startswith('v53_') else 'v54')/(w+'.out.json'))['result'] for w in specs}
    cases=[]
    def ok(value,message):
        if not value:raise ValueError(message)
    def case(name,fn,category):
        try:
            details=fn() or {}
            cases.append({'test':name,'category':category,'status':'PASS','details':details})
        except Exception as exc:
            cases.append({'test':name,'category':category,'status':'FAIL','error':str(exc)})
    def mutation(name,wid,change,where=None):
        def test():
            r=copy.deepcopy(records[wid]);change(r)
            try:check(specs[wid],r)
            except IndependentMismatch as exc:
                msg=str(exc)
                if where is not None:ok(where in msg,'rejected at unexpected field: '+msg)
                return {'rejection':'FAIL_INDEPENDENT_MISMATCH','reason':msg}
            raise ValueError('corrupted record accepted or rejected with wrong error class')
        case(name,test,'DIRECT_CHECK_NO_FIXED_HASH_SHORTCUT')
    for wid in sorted(specs):
        case('valid record '+wid,lambda wid=wid:check(specs[wid],records[wid]),'POSITIVE_CONTROL')
    for cls in ['memoryless','lookback_1','causal','offline']:
        mutation('A remove '+cls,A,lambda r,cls=cls:r['computed']['variants'].pop(cls),'variants')
        mutation('A corrupt count '+cls,A,lambda r,cls=cls:r['computed']['variants'][cls].__setitem__('selector_count',7),'selector_count')
        mutation('A corrupt existence '+cls,A,lambda r,cls=cls:r['computed']['variants'][cls].__setitem__('full_path_selector_exists',not r['computed']['variants'][cls]['full_path_selector_exists']),'full_path_selector_exists')
        mutation('A corrupt per-time '+cls,A,lambda r,cls=cls:r['computed']['variants'][cls]['per_time'][0].__setitem__('count',91),'per_time')
        mutation('A corrupt tables '+cls,A,lambda r,cls=cls:r['computed']['variants'][cls].__setitem__('selector_tables',{}),'selector_tables')
        mutation('A corrupt selected paths '+cls,A,lambda r,cls=cls:r['computed']['variants'][cls].__setitem__('selected_paths',{}),'selected_paths')
    mutation('A remove causal and offline',A,lambda r:[r['computed']['variants'].pop(x) for x in ['causal','offline']],'variants')
    mutation('A add variant',A,lambda r:r['computed']['variants'].__setitem__('extra',{}),'variants')
    mutation('A extra computed key',A,lambda r:r['computed'].__setitem__('extra',None),'computed')
    for wid in [E,F]:
        mutation(wid+' preserved flip',wid,lambda r:r['computed'].__setitem__('common_action_policy_preserved',not r['computed']['common_action_policy_preserved']),'common_action_policy_preserved')
        mutation(wid+' CPre promoted',wid,lambda r:r['computed'].__setitem__('cpre_claim_status','certified'),'cpre_claim_status')
        mutation(wid+' CPre removed',wid,lambda r:r['computed'].pop('cpre_claim_status'),'computed')
        mutation(wid+' pre information wrong',wid,lambda r:r['computed'].__setitem__('pre_information','original_display'),'pre_information')
        mutation(wid+' post information wrong',wid,lambda r:r['computed'].__setitem__('post_information','member_identity'),'post_information')
        mutation(wid+' exact flip control',wid,lambda r:r['computed'].__setitem__('exact',not r['computed']['exact']),'exact')
        mutation(wid+' section count',wid,lambda r:r['computed']['quotient_display_section'].__setitem__('count',0),'quotient_display_section')
        mutation(wid+' derived claim integer',wid,lambda r:r['computed']['claim_checks'].__setitem__('target_sound',1),'claim_checks')
    for name,fn,path in [
        ('extra outer null',lambda r:r.__setitem__('extra',None),'$'),
        ('missing outer',lambda r:r.pop('kind'),'$'),
        ('wrong ID',lambda r:r.__setitem__('id',A),'id'),
        ('wrong digest',lambda r:r.__setitem__('spec_sha256','0'*64),'spec_sha256'),
        ('schema float',lambda r:r.__setitem__('schema_version',2.0),'schema_version'),
        ('computed null',lambda r:r.__setitem__('computed',None),'computed'),
        ('bool to int',lambda r:r['computed'].__setitem__('recoverable',0),'recoverable'),
        ('integer to bool',lambda r:r['computed'].__setitem__('pt_size',True),'pt_size'),
        ('integer to float',lambda r:r['computed'].__setitem__('pt_size',1.0),'pt_size'),
        ('missing nested',lambda r:r['computed']['tau_pre'].pop('k'),'tau_pre'),
        ('extra nested null',lambda r:r['computed']['tau_pre'].__setitem__('extra',None),'tau_pre'),
        ('empty set modified',lambda r:r['computed']['live_cone_obstructions'].append(0),'live_cone_obstructions'),
        ('registered claim flip',lambda r:r['computed'].__setitem__('registered_claim_holds',False),'registered_claim_holds'),
    ]:mutation(name,G,fn,path)
    for wid in specs:
        mutation(wid+' extra computed',wid,lambda r:r['computed'].__setitem__('hidden_extra',None),'computed')
    mutation('B full-path claim promotion',B,lambda r:r['computed'].__setitem__('full_path_selector_status','certified'),'full_path_selector_status')
    mutation('B fixed-transition promotion',B,lambda r:r['computed'].__setitem__('fixed_transition_bridge_realization_claimed',True),'fixed_transition_bridge_realization_claimed')
    mutation('C controller promotion',C,lambda r:r['computed'].__setitem__('general_controller_synthesis_claimed',True),'general_controller_synthesis_claimed')
    mutation('C null versus false',C,lambda r:r['computed'].__setitem__('full_path_selector_exists',None),'full_path_selector_exists')
    mutation('D missing world',D,lambda r:r['computed']['worlds'].pop('silent'),'worlds')
    mutation('D closed-loop promotion',D,lambda r:r['computed'].__setitem__('closed_loop_guarantee_claimed',True),'closed_loop_guarantee_claimed')
    mutation('velocity remove state stage',V,lambda r:r['computed'].__setitem__('intermediate_state_removed',True),'intermediate_state_removed')
    mutation('velocity delete schedule',V,lambda r:r['computed']['schedules'].pop(),'schedules')
    mutation('velocity wrong stage count',V,lambda r:r['computed'].__setitem__('state_stage_count',2),'state_stage_count')
    mutation('same slices bridge flag', 'v53_same_slices_different_edges',lambda r:r['computed'].__setitem__('different_viable_bridges',False),'different_viable_bridges')

    python=[sys.executable,'-I','-B']+(['-O'] if not __debug__ else [])
    with tempfile.TemporaryDirectory(prefix='rephase_checker_tests_') as temp:
        root=Path(temp)
        def cli(name,change,expected_status='FAIL_INPUT_CONTRACT',expected_rc=2):
            def test():
                td=root/name;sp=td/'specs';rp=td/'results';out=td/'receipt.json'
                shutil.copytree(HERE/'specs',sp);shutil.copytree(HERE/'generated',rp)
                change(sp,rp)
                out.write_bytes(b'old receipt sentinel\n')
                args=python+[str(HERE/'independent_check.py'),'--specs',str(sp),'--results',str(rp),'--out',str(out)]
                run=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=120)
                ok(run.returncode==expected_rc,'wrong exit: '+str(run.returncode)+' '+run.stdout+' '+run.stderr)
                result=json.loads(run.stdout);ok(result['status']==expected_status,'wrong status')
                if expected_rc:
                    ok(out.read_bytes()==b'old receipt sentinel\n','failure overwrote prior report')
                    ok('witness_count' not in result,'failure claims successful witness count')
                return {'exit_code':run.returncode,'reported_status':result['status'],
                        'prior_report_preserved_on_failure':expected_rc!=0}
            case('CLI '+name,test,'FULL_SUITE_CLI')
        def sf(sp,wid):return sp/('v53' if wid.startswith('v53_') else 'v54')/(wid+'.json')
        def rf(rp,wid):return rp/('v53' if wid.startswith('v53_') else 'v54')/(wid+'.out.json')
        def edit_json(p,fn):
            o=load_json(p);fn(o);p.write_bytes(canonical_bytes(o))
        cli('valid full suite',lambda s,r:None,'PASS_INDEPENDENT_FINITE_EVIDENCE',0)
        cli('nonexistent specs',lambda s,r:shutil.rmtree(s))
        cli('nonexistent results',lambda s,r:shutil.rmtree(r))
        cli('empty specs',lambda s,r:[p.unlink() for p in s.rglob('*.json')])
        cli('empty results',lambda s,r:[p.unlink() for p in r.rglob('*') if p.is_file()])
        cli('one spec only',lambda s,r:[p.unlink() for p in s.rglob('*.json') if p.name!=G+'.json'])
        cli('one spec missing',lambda s,r:sf(s,G).unlink())
        cli('one result missing',lambda s,r:rf(r,G).unlink())
        cli('duplicate ID',lambda s,r:sf(s,'v53_collapse').write_bytes(sf(s,G).read_bytes()))
        cli('extra ID',lambda s,r:(s/'v53/extra.json').write_bytes(sf(s,G).read_bytes()))
        cli('wrong lane',lambda s,r:sf(s,G).rename(s/'v54'/(G+'.json')))
        cli('wrong filename',lambda s,r:sf(s,G).rename(s/'v53/wrong.json'))
        cli('extra result',lambda s,r:(r/'v53/extra.out.json').write_bytes(rf(r,G).read_bytes()))
        cli('result wrong lane',lambda s,r:rf(r,G).rename(r/'v54'/(G+'.out.json')))
        cli('result wrong ID',lambda s,r:edit_json(rf(r,G),lambda o:o['result'].__setitem__('id',A)))
        cli('unknown result sidecar',lambda s,r:(r/'unexpected.json').write_bytes(b'{}\n'))
        cli('duplicate JSON key',lambda s,r:rf(r,G).write_bytes(b'{"result":{},"result":{}}\n'))
        cli('nonfinite JSON',lambda s,r:rf(r,G).write_bytes(b'{"result":NaN,"verification":{}}\n'))
        cli('extra wrapper',lambda s,r:edit_json(rf(r,G),lambda o:o.__setitem__('extra',None)))
        cli('altered verification',lambda s,r:edit_json(rf(r,G),lambda o:o['verification'].__setitem__('finite_claims','certified')),'FAIL_INDEPENDENT_MISMATCH',3)
        cli('A missing variants',lambda s,r:edit_json(rf(r,A),lambda o:[o['result']['computed']['variants'].pop(k) for k in ['causal','offline']]),'FAIL_INDEPENDENT_MISMATCH',3)
        cli('E preserved flip',lambda s,r:edit_json(rf(r,E),lambda o:o['result']['computed'].__setitem__('common_action_policy_preserved',True)),'FAIL_INDEPENDENT_MISMATCH',3)
        cli('E CPre promotion',lambda s,r:edit_json(rf(r,E),lambda o:o['result']['computed'].__setitem__('cpre_claim_status','certified')),'FAIL_INDEPENDENT_MISMATCH',3)

        def freeze_corruption():
            dest=root/'rejected-freeze'
            # No edits to production code: substitute a corrupt compute return
            # only inside this isolated Python process. The shared check must reject it.
            script="""import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import freeze_candidate as f
original=f.compute
def corrupt(s):
 r=original(s)
 if s['id']=='v54_toy_A_memoryless_fail':r['computed']['variants'].pop('causal')
 return r
f.compute=corrupt
out=sys.argv[2]
sys.argv=['freeze_candidate.py','--out',out]
f.main()
"""
            p=subprocess.run(python+['-c',script,str(HERE),str(dest)],capture_output=True,text=True,encoding='utf-8',timeout=120)
            ok(p.returncode!=0,'corrupt freeze accepted')
            ok('IndependentMismatch' in p.stderr and 'variants' in p.stderr,'freeze rejected for unrelated reason')
            ok(not dest.exists(),'freeze wrote candidates before checker failure')
            return {'rejection':'shared independent check; no output created'}
        case('freeze call path rejects missing A class',freeze_corruption,'CALLER_INTEGRATION')

    failures=[r for r in cases if r['status']=='FAIL']
    return {'suite_version':SUITE_VERSION,'mode':'normal' if __debug__ else 'optimized',
            'status':'PASS_CHECKER_SELFTEST' if not failures else 'FAIL_CHECKER_SELFTEST',
            'tests':len(cases),'passed':len(cases)-len(failures),'failed':len(failures),
            'scope':'named auxiliary-checker adversarial cases; not distinct mathematical models',
            'results':cases}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();result=run()
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(canonical_bytes(result))
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
    for r in result['results']:
        if r['status']=='FAIL':print(json.dumps(r))
    return int(bool(result['failed']))


if __name__=='__main__':raise SystemExit(main())
