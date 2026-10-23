"""Constrained path writes after all validation succeeds. MIT."""
from pathlib import Path
import os,tempfile
from contract import require

def write_outputs(root,files):
    root=Path(root);require(not root.is_symlink(),'output root cannot be a symlink')
    resolved=root.resolve()
    for name in files:
        rel=Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts,'unsafe generated path')
        target=root/rel
        require(target.resolve().is_relative_to(resolved),'generated path escapes root')
        # Reject symlinks even when currently pointing back within the root.
        cur=target
        while cur!=root:
            require(not cur.is_symlink(),'symlink in generated path');cur=cur.parent
    for name,data in sorted(files.items()):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(data)
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
