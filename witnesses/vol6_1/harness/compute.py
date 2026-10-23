"""Compute typed fields and finite claim checks; role labels are metadata only. MIT."""
from contract import validate_spec,ROLES,digest,SUITE_VERSION,SCHEMA_VERSION
import compute_v53, compute_v54

def compute(spec):
    validate_spec(spec)
    module=compute_v53 if spec['id'].startswith('v53_') else compute_v54
    c=module.solve(spec['id'],spec['spec'])
    return {'id':spec['id'],'schema_version':SCHEMA_VERSION,'suite_version':SUITE_VERSION,
            'source_volume':spec['source_volume'],'kind':spec['kind'],
            'role_label':ROLES[spec['id']],'spec_sha256':digest(spec),'computed':c}
