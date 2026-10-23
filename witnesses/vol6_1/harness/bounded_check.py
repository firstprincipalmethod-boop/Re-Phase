#!/usr/bin/env python3
"""Bounded cross-implementation enumeration, MIT. Not an arbitrary-domain proof."""
from pathlib import Path
from itertools import product,combinations
import argparse,json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from compute_v53 import path_summary
from compute_v54 import cell_choices
from independent_check import summary,choice_truth,expect

def powers(xs):
    return [set(c) for k in range(len(xs)+1) for c in combinations(xs,k)]
def partitions(xs):
    if not xs:yield [];return
    x,*rest=xs
    for p in partitions(rest):
        yield [[x]]+p
        for i in range(len(p)):
            yield p[:i]+[[x]+p[i]]+p[i+1:]

def run():
    fibers=powers([0,1]);rels=powers(list(product([0,1],repeat=2)));path_counts={};ncompare=0
    for T in range(4):
        count=0
        fs=product(fibers,repeat=T+1) if T<3 else [[{0,1}]*(T+1)]
        for F in fs:
            for R in product(rels,repeat=T):
                a=path_summary(list(F),list(R),lambda p:p[-1],{0})
                b=summary(F,R,lambda p:p[-1],{0})
                expect(a,b,'bounded full path summary')
                # Endpoint and retrospective conditions, including T=0 distinction.
                expect(a['lift_size']==0,not a['forward_reachable'][-1],'terminal emptiness')
                if T>0:expect(a['retrospective_break'],list(range(T)) if not a['lifts'] else [],'break all-or-nothing')
                count+=1;ncompare+=len(a)
        path_counts[str(T)]=count
    action_counts={};actions=powers(['a','b','c'])
    for n in range(1,4):
        members=['m'+str(k) for k in range(n)];count=0
        for parts in partitions(members):
            cells={'c'+str(k):sorted(ms) for k,ms in enumerate(parts)}
            for row in product(actions,repeat=n):
                allowed=dict(zip(members,row))
                expect(cell_choices(cells,allowed,'bounded_policy'),choice_truth(cells,allowed,'bounded_policy'),'bounded common action')
                count+=1
        action_counts[str(n)]=count
    return {'status':'PASS_BOUNDED_CROSS_IMPLEMENTATION','path_models':sum(path_counts.values()),'path_models_by_horizon':path_counts,'path_summary_fields_compared':ncompare,'one_decision_policy_models':sum(action_counts.values()),'policy_models_by_member_count':action_counts,'scope':{'paths':'two states; horizons 0,1,2: all fibers and adjacent relations; horizon 3: full fibers and all adjacent relations','policies':'one to three members, three actions, all set partitions and allowed-action subsets','proof_over_arbitrary_domains':False,'external_independent_review':False}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=run()
    text=json.dumps(r,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(text.encode('utf-8'))
    print(text)
if __name__=='__main__':main()
