#!/bin/bash
cd ~/guardian-hunter || { echo "no existe ~/guardian-hunter"; exit 2; }
OUT=$(mktemp) || { echo "no puedo crear archivo temporal (revisa TMPDIR)"; exit 2; }
trap 'rm -f "$OUT"' EXIT
R=0
chk() {
  local n="$1"; shift
  if "$@" > "$OUT" 2>&1; then
    echo "PASS  $n"
  else
    echo "FAIL  $n"; tail -n 3 "$OUT" | sed 's/^/        /'; R=1
  fi
}
chk "arbol git limpio (sin cambios sin commit)" test -z "$(git status --porcelain)"
chk "compila todo el paquete" python3 -m compileall -q guardian_hunter
chk "tests pasan (suite completa)" python3 -m pytest -q -p no:cacheprovider --cov=guardian_hunter --cov-branch
chk "cobertura >= 85%" python3 -m coverage report --fail-under=85
chk "bandit sin severidad alta" python3 -m bandit -q -r guardian_hunter -x guardian_hunter/tests -lll
chk "dependencias sin CVEs conocidos" python3 -m pip_audit --progress-spinner off
echo
[ $R = 0 ] && echo "RESULTADO: TODO PASA" || echo "RESULTADO: HAY FALLOS (ver arriba)"
exit $R
