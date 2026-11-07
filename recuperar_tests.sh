#!/bin/bash
cd ~/guardian-hunter || { echo "no existe ~/guardian-hunter"; exit 1; }
BUENO=${1:-d45947d}
git cat-file -e "$BUENO^{commit}" 2>/dev/null || { echo "no existe el commit $BUENO"; exit 1; }
RESP=~/respaldo_falsos/tests_rotos
mkdir -p "$RESP" audit_full
LISTA=audit_full/rotos.txt
python3 -m compileall -q guardian_hunter 2>&1 | grep "Error compiling" | sed -E "s/.*Error compiling '([^']+)'.*/\1/" > "$LISTA"
echo "archivos rotos: $(wc -l < "$LISTA")  | commit bueno: $BUENO"
OK=0; NO=0
while read -r f; do
  [ -z "$f" ] && continue
  mkdir -p "$RESP/$(dirname "$f")"; cp "$f" "$RESP/$f"
  if git cat-file -e "$BUENO:$f" 2>/dev/null; then
    git checkout "$BUENO" -- "$f" && OK=$((OK+1))
  else
    echo "SIN version buena en $BUENO: $f"; NO=$((NO+1))
  fi
done < "$LISTA"
echo "restaurados=$OK  sin_version_buena=$NO  (copia de los rotos en $RESP)"
echo "--- archivos que aun no compilan: $(python3 -m compileall -q guardian_hunter 2>&1 | grep -c 'Error compiling')"
echo "--- pytest (suite completa)"
python3 -m pytest -q -p no:cacheprovider 2>&1 | tail -n 4
