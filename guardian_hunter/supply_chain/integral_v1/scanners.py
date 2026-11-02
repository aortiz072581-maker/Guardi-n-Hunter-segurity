"""Read-only scanners. No permission to execute repairs or deployments."""
import json, shutil, subprocess, hashlib
from pathlib import Path

def run_json_tool(executable, args, timeout=120):
    binary=shutil.which(executable)
    if not binary:return {'status':'UNAVAILABLE','tool':executable}
    try:
        result=subprocess.run([binary,*args],capture_output=True,text=True,timeout=timeout,check=False)
        if result.returncode:return {'status':'FAILED','tool':executable,'exit_code':result.returncode,'stderr':result.stderr[-1000:]}
        return {'status':'SCANNED','tool':executable,'result':json.loads(result.stdout)}
    except (OSError,ValueError,subprocess.TimeoutExpired) as e:return {'status':'FAILED','tool':executable,'error':type(e).__name__}

def grype_sbom(path):
    p=Path(path).resolve(strict=True)
    if not p.is_file() or p.is_symlink():raise ValueError('INVALID_SBOM')
    return run_json_tool('grype',['sbom:'+str(p),'-o','json'])

def syft_directory(path):
    p=Path(path).resolve(strict=True)
    if not p.is_dir() or p.is_symlink():raise ValueError('INVALID_DIRECTORY')
    return run_json_tool('syft',['dir:'+str(p),'-o','cyclonedx-json'])

def verify_cosign_blob(blob,signature,key):
    for p in (blob,signature,key):
        if not Path(p).is_file() or Path(p).is_symlink():raise ValueError('MISSING_TRUSTED_INPUT')
    binary=shutil.which('cosign')
    if not binary:return {'status':'UNAVAILABLE'}
    try:
        r=subprocess.run([binary,'verify-blob','--key',str(Path(key).resolve()),'--signature',str(Path(signature).resolve()),str(Path(blob).resolve())],capture_output=True,text=True,timeout=90)
        return {'status':'VERIFIED' if r.returncode==0 else 'DENIED','exit_code':r.returncode}
    except (OSError,subprocess.TimeoutExpired):return {'status':'FAILED'}

def inspect_intoto_statement(path, artifact):
    """Structural digest check only; NOT provenance authenticity verification."""
    doc=json.loads(Path(path).read_text())
    digest=hashlib.sha256(Path(artifact).read_bytes()).hexdigest()
    subjects=doc.get('subject',[])
    matches=any(s.get('digest',{}).get('sha256')==digest for s in subjects if isinstance(s,dict))
    return {'status':'DIGEST_MATCH_UNAUTHENTICATED' if matches else 'DENIED','provenance_verified':False}
