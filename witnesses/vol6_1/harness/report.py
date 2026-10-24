"""CSV / manuscript-data export exclusively from newly computed verified records. MIT."""
import csv,io,json

def dumps_csv(rows,fields):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader()
    for row in rows:w.writerow(row)
    return s.getvalue().encode()

def table_bytes(records):
    a=[];b=[];choices=[]
    for r in records:
        c=r['computed'];base={'id':r['id'],'role_label':r['role_label'],'obligation_type':c['obligation_type'],'registered_claim_holds':json.dumps(c['registered_claim_holds'])}
        if r['id'].startswith('v53_'):
            summaries=[('parallel',c['variant_a']),('complete',c['variant_b'])] if 'variant_a' in c else [(json.dumps(x['schedule']),x) for x in c['schedules']] if 'schedules' in c else [('',c)]
            for variant,x in summaries:a.append({**base,'variant':variant,'pt_size':x['pt_size'],'lift_size':x['lift_size'],'feature_image_lift':json.dumps(x['feature_image_lift']),'tau_pre':json.dumps(x['tau_pre']),'recoverable':json.dumps(x['recoverable'])})
        else:
            b.append(base)
            def add(scope,obj):
                choices.append({'id':r['id'],'scope':scope,'obligation_type':obj['obligation_type'],'exists':json.dumps(obj['exists']),'count':obj['count'],'table':json.dumps(obj['table'],sort_keys=True)})
            if 'variants' in c:
                for cls,v in c['variants'].items():
                    choices.append({'id':r['id'],'scope':cls,'obligation_type':c['obligation_type'],'exists':json.dumps(v['full_path_selector_exists']),'count':v['selector_count'],'table':json.dumps(v['selected_paths'],sort_keys=True)})
            elif 'choice' in c:add('all_information_cells',c['choice'])
            elif 'continuation_choice' in c:add('shared_prefix_only',c['continuation_choice'])
            elif 'worlds' in c:
                for name,w in c['worlds'].items():
                    for cls,v in w['policies'].items():add(name+'/'+cls,v)
            else:
                for field in ('pre_member_policy','post_quotient_policy','original_display_policy'):add(field,c[field])
    return {'table_v53.csv':dumps_csv(a,['id','role_label','obligation_type','variant','pt_size','lift_size','feature_image_lift','tau_pre','recoverable','registered_claim_holds']),
            'table_v54.csv':dumps_csv(b,['id','role_label','obligation_type','registered_claim_holds']),
            'table_v54_choices.csv':dumps_csv(choices,['id','scope','obligation_type','exists','count','table'])}
