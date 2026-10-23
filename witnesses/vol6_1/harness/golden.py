"""Strict, recursive type/key/value comparison of complete deterministic records. MIT.

All envelope fields, including id, schema/suite version and spec digest, are compared.
No missing/null coercion, bool/int coercion, ignored keys, or auto-rebaseline operation.
"""
from contract import typed_equal

def differences(a,b,path='$'):
    if type(a) is not type(b):return [path+': type mismatch']
    if type(a) is dict:
        ds=[path+': key set mismatch'] if set(a)!=set(b) else []
        for k in sorted(set(a)&set(b)):ds.extend(differences(a[k],b[k],path+'.'+k))
        return ds
    if type(a) is list:
        ds=[path+': array length mismatch'] if len(a)!=len(b) else []
        for k,(x,y) in enumerate(zip(a,b)):ds.extend(differences(x,y,f'{path}[{k}]'))
        return ds
    return [] if a==b else [path+': value mismatch']

def compare(record,golden):
    if golden is None:return 'no-golden',['missing golden record']
    ds=differences(record,golden)
    return ('pass' if not ds else 'fail'),ds
