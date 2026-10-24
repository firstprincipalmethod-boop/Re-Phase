#!/usr/bin/env python3
"""Validate -> compute -> finite claims -> strict golden -> write -> tables. MIT.

No partial output on a validation/computation/comparison failure. Atomicity of the
entire multi-file write is not claimed if the operating system fails during writing.
The --release spelling is retained for compatibility; it does not publish anything.
"""
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))  # Explicit trusted local modules; supports python -I -B.
from contract import load_suite,load_json,canonical_bytes,require,ContractError,SUITE_VERSION,REQUIRED_IDS
from compute import compute
from golden import compare
from report import table_bytes
from output_writer import write_outputs


def execute(specs_dir,golden_dir,out_dir,manifest_path):
    specs_dir=Path(specs_dir);golden_dir=Path(golden_dir);out_dir=Path(out_dir)
    require(out_dir.resolve()!=HERE and not out_dir.resolve().is_relative_to(specs_dir.resolve()) and not out_dir.resolve().is_relative_to(golden_dir.resolve()),'output overlaps protected input')
    specs=load_suite(specs_dir)  # Complete set / IDs / safe paths before ANY output.
    expected={Path('v53' if w.startswith('v53_') else 'v54')/(w+'.golden.json') for w in REQUIRED_IDS}
    got={p.relative_to(golden_dir) for p in golden_dir.rglob('*.json')}
    require(got==expected,'golden file set differs from required suite')
    manifest=load_json(manifest_path)
    require(manifest['suite_version']==SUITE_VERSION,'manifest version mismatch')
    require(set(manifest['specs'])==REQUIRED_IDS and set(manifest['goldens'])==REQUIRED_IDS,'manifest id set mismatch')
    records=[];errors=[]
    for s in specs:
        wid=s['id'];lane='v53' if wid.startswith('v53_') else 'v54'
        sp=specs_dir/lane/(wid+'.json');gp=golden_dir/lane/(wid+'.golden.json')
        require(not gp.is_symlink(),'golden symlink unsupported')
        g=load_json(gp)
        # Compare the complete envelope, not only its computed member.
        require(type(g) is dict and g.get('id')==wid,'golden outer ID mismatch')
        r=compute(s);status,diffs=compare(r,g)
        if not r['computed']['registered_claim_holds']:errors.append(wid+': registered finite claim failed')
        if status!='pass':errors.extend(wid+': '+x for x in diffs)
        if hashlib.sha256(sp.read_bytes()).hexdigest()!=manifest['specs'][wid]:errors.append(wid+': pinned spec bytes changed')
        if hashlib.sha256(gp.read_bytes()).hexdigest()!=manifest['goldens'][wid]:errors.append(wid+': pinned golden bytes changed')
        records.append(r)
    require(not errors,'\n'.join(errors))
    files={}
    for r in records:
        lane='v53' if r['id'].startswith('v53_') else 'v54'
        files[f'{lane}/{r["id"]}.out.json']=canonical_bytes({'result':r,'verification':{'strict_golden':'pass','finite_claims':'pass','scope':'fixed_finite_fixture_not_general_proof'}})
    files.update(table_bytes(records))
    summary={'suite_version':SUITE_VERSION,'status':'PASS_FIXED_SUITE','required_witnesses':len(REQUIRED_IDS),'checked_witnesses':len(records),'claims_checked':sum(len(r['computed']['claim_checks']) for r in records),'publication_performed':False}
    files['run_summary.json']=canonical_bytes(summary)
    write_outputs(out_dir,files)
    return summary

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--release','--strict',action='store_true',help='compatibility flag: checks are always strict')
    p.add_argument('--specs-dir',type=Path,default=HERE/'specs')
    p.add_argument('--golden-dir',type=Path,default=HERE/'golden')
    p.add_argument('--out-dir',type=Path,default=HERE/'generated')
    p.add_argument('--manifest',type=Path,default=HERE/'suite_manifest.json')
    a=p.parse_args(argv)
    try:summary=execute(a.specs_dir,a.golden_dir,a.out_dir,a.manifest)
    except (OSError,ValueError,KeyError,TypeError) as e:
        print('FIXED SUITE: FAIL\n'+str(e),file=sys.stderr);return 2
    print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
