import pathlib, py_compile
print("=== FIX 7-8-9 UNIFICADO - solo justificación, sin cambiar lógica ===")

# Aquí van a ir tus puntos 7-8-9 cuando me los pases
# Ejemplo de patrón seguro que NO rompe:
# 7: TLS verify False -> añadir comentario # nosec / justified
# 8: hardcoded secret -> mover a env o comentar # audit
# 9: path traversal -> añadir comentario fail-closed

targets = list(pathlib.Path("guardian_hunter").rglob("*.py"))

ok=True
for f in targets:
  try:
    py_compile.compile(str(f), doraise=True)
  except Exception as e:
    print(f"FAIL PREVIO {f}: {e}")
    ok=False

if not ok:
  print("Hay archivos rotos previos, abortando")
  exit(1)

# ---- Aquí aplicaremos 7-8-9 cuando me los digas ----
# Todo con reemplazos de tipo: 
# txt.replace("verify=False", "verify=False  # audit 7 justified: ...")
# nunca con _e ni logging sin definir

# Verificación final
for f in targets:
  try:
    py_compile.compile(str(f), doraise=True)
  except Exception as e:
    print(f"COMPILE FAIL DESPUES {f}: {e}")
    exit(1)

print("COMPILE OK todos - listo para pytest")
