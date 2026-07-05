"""Load + validate witness spec JSON files. Returns only structurally-valid, correctly-placed
specs (D13-clean, D15-placed)."""
import json, glob, os
from schema import validate_spec, bucket


def _path_bucket(path, specs_dir):
    """First subdirectory under specs_dir ('v53'/'v54'), or None if the file sits in specs/ root.
    Deeper nesting (specs/v53/group/x.json) still reports the top bucket 'v53'."""
    rel = os.path.relpath(path, specs_dir)
    parts = rel.split(os.sep)
    return parts[0] if len(parts) > 1 else None


def load_specs(specs_dir):
    specs, problems = [], []
    for path in sorted(glob.glob(os.path.join(specs_dir, "**", "*.json"), recursive=True)):
        try:
            obj = json.load(open(path))
        except Exception as e:
            problems.append((path, [f"JSON parse error: {e}"])); continue
        ok, errs = validate_spec(obj, where=os.path.basename(path))
        if ok:
            # D15 ENFORCEMENT: physical folder must match the source_volume bucket, else a spec
            # dropped in the wrong folder would validate and silently route to the other volume's
            # generated/golden dirs. bucket() is safe here because validate_spec passed.
            want = bucket(obj)
            got = _path_bucket(path, specs_dir)
            if got != want:
                loc = f"specs/{got}/" if got else "specs/ (root)"
                errs = errs + [f"{os.path.relpath(path, specs_dir)}: placed in {loc} but "
                               f"source_volume {obj.get('source_volume')} belongs in "
                               f"specs/{want}/ (D15 placement)"]
                ok = False
        if ok:
            obj["_path"] = path; specs.append(obj)
        else:
            problems.append((path, errs))
    return specs, problems
