#!/usr/bin/env python3
"""MIT. C1 fixed Toy D partition correspondence, using only fixture data.

This is a supplemental finite calculation, not a general equivalence theorem.
No primary/auxiliary harness calculations or golden data are imported.
"""
from pathlib import Path
import argparse, hashlib, json, math
BASE=Path(__file__).resolve().parent.parent

def partition(world, history):
    cells={}
    for member,data in sorted(world.items()):
        observation=tuple(data['tilt_history']) if history else data['tilt_history'][-1]
        cells.setdefault((observation,data['mode']),[]).append(member)
    return sorted(sorted(members) for members in cells.values())

def evidence(world,cells):
    rows=[]
    for members in cells:
        common=set.intersection(*[{world[m]['required_action']} for m in members])
        rows.append({'members':members,'common_actions':sorted(common)})
    return {'cells':rows,'policy_count':math.prod(len(r['common_actions']) for r in rows)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--software-root',type=Path,default=BASE)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args(); p=a.software_root/'witnesses/vol6_1/harness/specs/v54/v54_toy_D_retention_memory.json'
    record=json.loads(p.read_text(encoding='utf-8'))
    if record['id']!='v54_toy_D_retention_memory':raise ValueError('wrong fixture')
    worlds=record['spec']['worlds']
    if set(worlds)!={'traceable','silent'}:raise ValueError('not the registered two worlds')
    rows=[]
    for name,world in sorted(worlds.items()):
        current=partition(world,False);history=partition(world,True)
        ecurrent=evidence(world,current);ehistory=evidence(world,history)
        singleton=all(len(c)==1 for c in current)
        passed=current==history and ecurrent==ehistory and singleton and len(current)==2 and ecurrent['policy_count']==1
        rows.append({'world':name,'current_tilt_plus_mode':ecurrent,'history_plus_mode':ehistory,
            'same_member_partition':current==history,'two_singleton_cells':singleton and len(current)==2,
            'same_allowed_intersections_and_count':ecurrent==ehistory,'status':'PASS' if passed else 'FAIL'})
    result={'status':'PASS_FIXED_TOY_D_INFORMATION_CORRESPONDENCE' if all(r['status']=='PASS' for r in rows) else 'FAIL',
       'candidate_id':record['suite_version'],'spec_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
       'source_doi':'10.5281/zenodo.23499819','source_policy_section':'12',
       'source_policy_map':'current tilt and retained mode','implementation_policy_map':'full tilt history and retained mode',
       'augmented_section_map':'full tilt history and retained mode','worlds':rows,
       'information_value_keys_identical':False,'general_equivalence_claimed':False,
       'primary_or_golden_imported':False,'scope':'two fixed member sets only; not general controller synthesis'}
    text=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(text.encode('utf-8'))
    print(text);return 0 if result['status'].startswith('PASS_') else 1
if __name__=='__main__':raise SystemExit(main())
