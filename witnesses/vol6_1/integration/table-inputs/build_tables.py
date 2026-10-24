#!/usr/bin/env python3
"""MIT. Render tables from hash-bound software results; never recompute toy claims."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent

def path_key(path, base):
    return path.relative_to(base).as_posix()

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def esc(x):
    s=str(x)
    for a,b in [('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),('_',r'\_'),('{',r'\{'),('}',r'\}')]:s=s.replace(a,b)
    return s

def table(name,headers,rows,fmt=None):
    fmt=fmt or ('l'+'r'*(len(headers)-1))
    text='\\begin{tabular}{'+fmt+'}\n\\toprule\n'+' & '.join(headers)+' \\\\\n\\midrule\n'
    text+=''.join(' & '.join(str(v) for v in r)+' \\\\\n' for r in rows)
    text+='\\bottomrule\n\\end{tabular}\n'
    (BASE/'generated'/name).write_bytes(text.encode('utf-8'))

def main():
    contract=load(BASE/'SYNC_CONTRACT.json');records={}
    for rel,digest in contract['verification_payload_sha256'].items():
        if sha(BASE/rel)!=digest:raise ValueError('verification digest mismatch: '+rel)
    for p in sorted((BASE/'results').glob('*/*.out.json')):
        rel='witnesses/vol6_1/harness/generated/'+path_key(p,BASE/'results')
        if sha(p)!=contract['software_payload_sha256'][rel]:raise ValueError('result digest mismatch: '+p.name)
        r=load(p)['result']
        if r['suite_version']!=contract['candidate_id']:raise ValueError('candidate mismatch')
        records[r['id']]=r
    if len(records)!=13:raise ValueError('expected 13 result records')
    (BASE/'generated').mkdir(exist_ok=True)
    get=lambda w:records[w]['computed']
    ids=['v53_collapse','v53_gap_collapse','v53_unique_lift','v53_feature_ambiguous_recoverable','v53_missing_cell']
    labels=['Collapse','Live-cone gap','Unique lift','Ambiguous / recovered','Narrowed / not recovered']
    rows=[]
    yn=lambda x:'yes' if x else 'no'
    for wid,label in zip(ids,labels):
        c=get(wid);rows.append([label,c['pt_size'],c['lift_size'],str(c['tau_pre']['k']) if c['tau_pre']['k'] is not None else '--',yn(c['recoverable'])])
    for key,label in [('variant_a','Parallel edges'),('variant_b','Complete edges')]:
        c=get('v53_same_slices_different_edges')[key];rows.append([label,c['pt_size'],c['lift_size'],'--',yn(c['recoverable'])])
    table('v53_summary.tex',['Case',r'$|\mathrm{Pt}|$',r'$|\mathrm{Lift}|$',r'$\tau_{\rm pre}$','Recoverable'],rows,'lrrrl')
    rows=[]
    for c in get('v53_constant_velocity')['schedules']:
        j='$\\varnothing$' if not c['schedule'] else '$\\{'+','.join(map(str,c['schedule']))+'\\}$'
        rows.append([j,c['pt_size'],c['lift_size'],'$\\{'+','.join(map(str,c['feature_image_lift']))+'\\}$',yn(c['recoverable'])])
    table('velocity.tex',['Observed times',r'$|\mathrm{Pt}|$',r'$|\mathrm{Lift}|$',r'$H(\mathrm{Lift})$','Recoverable'],rows,'lrrll')
    rows=[]
    for cls in ['memoryless','lookback_1','causal','offline']:
        c=get('v54_toy_A_memoryless_fail')['variants'][cls];rows.append([esc(cls),yn(c['full_path_selector_exists']),c['selector_count']])
    table('toy_a.tex',['Information class','Full-path selector','Count'],rows,'llr')
    d=get('v54_toy_D_retention_memory')['worlds'];rows=[]
    for cls in ['memoryless','lookback_1','lookback_2','offline','retained_mode_augmented']:
        rows.append([esc(cls),d['traceable']['policies'][cls]['count'],d['silent']['policies'][cls]['count']])
    table('toy_d.tex',['Information','TRACEABLE policies','SILENT policies'],rows,'lrr')
    E=get('v54_toy_E_target_sound_not_selector');F=get('v54_toy_F_safe_nonexact');rows=[]
    for fld,label in [('original_display_section','Original constant-display sections'),('quotient_display_section','Quotient-display sections'),('pre_member_policy','Member-identifying pre-policies'),('post_quotient_policy','Quotient-information post-policies'),('original_display_policy','Original-display-only policies')]:rows.append([label,E[fld]['count'],F[fld]['count']])
    table('toy_ef.tex',['Object','Toy E','Toy F'],rows,'lrr')
    normal=load(BASE/'verification/selftest_normal.json');opt=load(BASE/'verification/selftest_optimized.json');bound=load(BASE/'verification/bounded_normal.json')
    cn=load(BASE/'verification/checker_selftest_normal.json');co=load(BASE/'verification/checker_selftest_optimized.json')
    macros={'SuiteCases':13,'FiniteClaims':sum(len(r['computed']['claim_checks']) for r in records.values()),'SelfTests':normal['tests'],'SelfTestsOptimized':opt['tests'],'CheckerSelfTests':cn['tests'],'CheckerSelfTestsOptimized':co['tests'],'BoundedPaths':bound['path_models'],'BoundedPolicies':bound['one_decision_policy_models'],'BoundedPathFields':bound['path_summary_fields_compared']}
    if normal['failed'] or opt['failed'] or cn['failed'] or co['failed']:raise ValueError('failed selftest cannot populate manuscript')
    text=''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in macros.items())
    text+='\\newcommand{\\SyncDigest}{'+sha(BASE/'SYNC_CONTRACT.json')+'}\n'
    (BASE/'generated/results_macros.tex').write_bytes(text.encode('utf-8'))
    sm=load(BASE/'provenance/source_map.json')
    labels={**dict(zip(ids,labels)),'v53_constant_velocity':'Constant velocity','v53_same_slices_different_edges':'Same slices / different edges'}
    rows=[]
    for wid in sorted(records):
        src=sm[wid];short=labels.get(wid,'Toy '+wid.split('_')[2] if wid.startswith('v54') else wid)
        rows.append([esc(short),esc(src['section']),str(len(records[wid]['computed']['claim_checks'])),r'\texttt{\seqsplit{'+esc(wid)+'}}'])
    table('registry.tex',['Case','Source section','Checks','Stable ID'],rows,'p{3.5cm}p{1.6cm}rp{7.8cm}')
    data={'candidate_id':contract['candidate_id'],'sync_contract_sha256':sha(BASE/'SYNC_CONTRACT.json'),'result_ids':sorted(records),'macros':macros,'tables':{p.name:sha(p) for p in sorted((BASE/'generated').glob('*.tex'))}}
    (BASE/'generated/table_derivation.json').write_bytes((json.dumps(data,sort_keys=True,indent=2)+'\n').encode('utf-8'))
    print('Generated tables from 13 hash-bound result records.')
if __name__=='__main__':main()
