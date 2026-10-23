#!/usr/bin/env python3
"""Explicit local candidate freeze, never called by run_all. MIT.

Writes into a NEW staging directory only. Every result must pass the independent
finite checker and the finite claim predicates before golden candidates are emitted.
A candidate freeze is not external acceptance, publication, or a signed trust anchor.
"""
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from contract import load_suite,canonical_bytes,SUITE_VERSION,require
from compute import compute
from independent_check import check

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    require(not a.out.exists(),'refuse to overwrite candidate directory')
    specs=load_suite(HERE/'specs');computed=[];checked=[]
    for s in specs:
        r=compute(s);checked.append(check(s,r))
        require(r['computed']['registered_claim_holds'],s['id']+': finite claim failed')
        computed.append(r)
    a.out.mkdir(parents=True)
    manifest={'suite_version':SUITE_VERSION,'scope':'local_candidate_second_implementation_check; no_external_approval','specs':{},'goldens':{}}
    for r in computed:
        wid=r['id'];lane='v53' if wid.startswith('v53_') else 'v54'
        p=a.out/'golden'/lane/(wid+'.golden.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canonical_bytes(r))
        manifest['specs'][wid]=hashlib.sha256((HERE/'specs'/lane/(wid+'.json')).read_bytes()).hexdigest()
        manifest['goldens'][wid]=hashlib.sha256(p.read_bytes()).hexdigest()
    (a.out/'suite_manifest.json').write_bytes(canonical_bytes(manifest))
    (a.out/'golden_candidate_review.json').write_bytes(canonical_bytes({'suite_version':SUITE_VERSION,'witnesses':checked,'count':len(checked),'external_review':False,'status':'PASS_FINITE_CANDIDATE_COMPARISON'}))
    print(f'Created {len(computed)} independently checked candidate snapshots in {a.out.name}')
if __name__=='__main__':main()
