with open("guardian_enterprise_core.py", "r") as f:
    code = f.read()

# Reemplazar la línea errónea por la sintaxis correcta del f-string
old_line = 'raise HumanApprovalRequiredError(f"BLOQUEO DE GOBIERNO: La acción crítica \'{action\'}\' requiere aprobación humana expresa.")'
new_line = 'raise HumanApprovalRequiredError(f"BLOQUEO DE GOBIERNO: La acción crítica \'{action}\' requiere aprobación humana expresa.")'

# Si hay variaciones en las comillas, reescribamos el método completo de forma limpia:
fixed_code = code.replace(
    'raise HumanApprovalRequiredError(f"BLOQUEO DE GOBIERNO: La acción crítica \'{action\'}\' requiere aprobación humana expresa.")',
    'raise HumanApprovalRequiredError(f"BLOQUEO DE GOBIERNO: La acción crítica \'{action}\' requiere aprobación humana expresa.")'
)

with open("guardian_enterprise_core.py", "w") as f:
    f.write(fixed_code)

print("[✔] Archivo guardian_enterprise_core.py corregido con éxito.")
