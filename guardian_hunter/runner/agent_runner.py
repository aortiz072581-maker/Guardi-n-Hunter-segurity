"""Controlled runner for the detached Guardian Agent workspace."""
from __future__ import annotations
import os, stat, sys, subprocess
from pathlib import Path

TIMEOUT_SECONDS = 300
ALLOWED_EXECUTABLES = frozenset({"python", "python3"})
FORBIDDEN_ARGUMENT_TOKENS = (";", "&&", "||", "|", "`", "$(", "\n", "\r", "\x00")
BLOCKED_ENV_PREFIXES = ("GITHUB_", "GH_", "AWS_", "AZURE_", "GOOGLE_", "OPENAI_", "ANTHROPIC_")
SAFE_PATH = "/usr/bin:/bin:/usr/local/bin"

def _fail(m): raise RuntimeError(m)
def _check_empty_command(c):
    if not c: _fail("COMMAND_REQUIRED")
def _check_executable(e):
    if not e: _fail("COMMAND_REQUIRED")
    if "/" in e or "\\" in e or e.startswith("."): _fail(f"EXECUTABLE_NOT_ALLOWED:{e}")
    if e not in ALLOWED_EXECUTABLES: _fail(f"EXECUTABLE_NOT_ALLOWED:{e}")
def _check_forbidden_tokens(cmd):
    for tok in FORBIDDEN_ARGUMENT_TOKENS:
        for x in cmd:
            if tok in x: _fail(f"UNSAFE_COMMAND_ARGUMENT:FORBIDDEN_TOKEN:{tok}")
def _check_code_execution_switches(cmd):
    if len(cmd)>=2:
        sec=cmd[1]
        if sec in ("-c","-m","-i","-S","-E") or sec.startswith("-c") or sec.startswith("-m"):
            _fail(f"UNSAFE_COMMAND_ARGUMENT:CODE_EXECUTION_SWITCH:{sec}")
def _check_workspace_git_metadata(ws: Path):
    for p in [ws/".git", Path.cwd()/".git", Path.cwd().parent/".git", Path.cwd().parent/"guardian-agent"/".git"]:
        if p.exists(): _fail("WORKSPACE_GIT_FORBIDDEN")
    try:
        for p in Path.cwd().parent.rglob(".git"):
            if p.exists(): _fail("WORKSPACE_GIT_FORBIDDEN")
    except OSError: pass

def _validate_candidate_path(candidate: Path, workspace_root: Path):
    s=str(candidate)
    if "\x00" in s: _fail("PATH_TRAVERSAL_FORBIDDEN")
    if candidate.is_absolute(): _fail(f"UNSAFE_COMMAND_ARGUMENT:ABSOLUTE:{candidate}")
    if ".." in candidate.parts: _fail(f"UNSAFE_COMMAND_ARGUMENT:TRAVERSAL:{candidate}")
    if s.startswith("/tmp") or s.startswith("/etc"): _fail(f"UNSAFE_COMMAND_ARGUMENT:BLOCKED:{candidate}")
    if s=="-": _fail(f"UNSAFE_COMMAND_ARGUMENT:STDIN:{candidate}")
    if candidate.suffix!=".py": _fail(f"UNSAFE_COMMAND_ARGUMENT:BAD_EXT:{candidate}")
    cur=workspace_root
    for part in candidate.parts:
        if not part or part==".": continue
        cur=cur/part
        try: st=os.lstat(cur)
        except FileNotFoundError: continue
        if stat.S_ISLNK(st.st_mode): _fail(f"SCRIPT_SYMLINK_FORBIDDEN:SYMLINK_COMPONENT:{candidate}")

def _safe_open_candidate(full_path: Path):
    try: pre=os.lstat(full_path)
    except FileNotFoundError: _fail(f"SCRIPT_NOT_REGULAR_FILE:MISSING:{full_path}")
    if stat.S_ISDIR(pre.st_mode): _fail(f"SCRIPT_NOT_REGULAR_FILE:IS_DIRECTORY:{full_path}")
    if not stat.S_ISREG(pre.st_mode):
        if stat.S_ISLNK(pre.st_mode): _fail(f"SCRIPT_SYMLINK_FORBIDDEN:SYMLINK_CANDIDATE:{full_path}")
        _fail(f"SCRIPT_NOT_REGULAR_FILE:NOT_REGULAR:{full_path}")
    try: fd=os.open(full_path, os.O_RDONLY|os.O_NOFOLLOW)
    except FileNotFoundError: _fail(f"SCRIPT_NOT_REGULAR_FILE:MISSING:{full_path}")
    except OSError:
        _fail(f"SCRIPT_SYMLINK_FORBIDDEN:OPEN_FAILED:{full_path}")
    try:
        fstat=os.fstat(fd)
        if not stat.S_ISREG(fstat.st_mode): _fail(f"SCRIPT_NOT_REGULAR_FILE:NOT_REGULAR_AFTER_OPEN:{full_path}")
        if fstat.st_ino!=pre.st_ino or fstat.st_dev!=pre.st_dev: _fail(f"CANDIDATE_SWAP_DETECTED:{full_path}")
        with os.fdopen(fd,'rb') as f: return f.read()
    finally:
        try: os.close(fd)
        except OSError: pass

def sanitized_environment(workspace: Path):
    clean={}
    for k,v in os.environ.items():
        if k=="SSH_AUTH_SOCK": continue
        if k=="PATH": continue
        if any(k.startswith(p) for p in BLOCKED_ENV_PREFIXES): continue
        clean[k]=v
    clean["HOME"]=str(workspace.resolve())
    clean["PATH"]=SAFE_PATH
    clean["GUARDIAN_WORKSPACE"]=str(workspace.resolve())
    return clean

def run_candidate(command, *, broker=None, workspace=None, env=None):
    _check_empty_command(command)
    _check_executable(command[0])
    _check_forbidden_tokens(command)
    _check_code_execution_switches(command)
    ws=Path(workspace) if workspace else Path.cwd()
    real_ws=ws
    cand_path=None
    full=None
    if len(command)>=2 and command[1]!="--version":
        cand_path=Path(command[1])
        full=ws/cand_path
        if not full.exists():
            for alt in [ws.parent/"guardian-agent", Path.cwd().parent/"guardian-agent", Path.cwd()/"guardian-agent", Path.cwd()]:
                if (alt/cand_path).exists():
                    real_ws=alt; full=alt/cand_path; break
        _validate_candidate_path(cand_path, real_ws)
        _safe_open_candidate(full)
        ws=real_ws
    _check_workspace_git_metadata(ws)
    trusted=str(Path(sys.executable).resolve())
    if len(command)>=2 and command[1]=="--version":
        safe=[trusted,"--version"]
    else:
        # Ejecución segura: python -I -c "exec(...)" candidate.py
        # Sin /proc/self/fd/ y sin pass_fds
        rel = str(cand_path) if cand_path else "candidate.py"
        code = "import sys, pathlib; p=pathlib.Path(sys.argv[1]); exec(compile(p.read_bytes(), str(p), 'exec'))"
        safe=[trusted, "-I", "-c", code, rel]
    kwargs=dict(cwd=ws.resolve(), env=env or sanitized_environment(ws), stdin=subprocess.DEVNULL, timeout=TIMEOUT_SECONDS, check=False, pass_fds=())
    if broker is None:
        r=subprocess.run(safe, **kwargs)
        return r.returncode
    else:
        r=broker(safe, **kwargs)
        return r.returncode if hasattr(r,"returncode") else r

def run_command(c,**kw): return run_candidate(c,**kw)

# --- compat shims for old tests ---
def validate_command(command):
    _check_empty_command(command)
    _check_executable(command[0])
    _check_forbidden_tokens(command)
    _check_code_execution_switches(command)
    if len(command) >= 2 and command[1] not in ("--version",):
        # valida que no sea traversal, etc
        _validate_candidate_path(Path(command[1]), Path.cwd())
    return command
