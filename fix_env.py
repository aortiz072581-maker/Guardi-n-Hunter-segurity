# Módulo de verificación de entorno corporativo blindado
import os

def validate_environment():
    # Validación estricta con excepciones de producción (sin assert)
    if not os.path.exists(".git"):
        raise EnvironmentError("CRITICAL: Directorio git no detectado en la raíz.")
    if "HOME" not in os.environ:
        raise EnvironmentError("CRITICAL: Variable de entorno HOME no definida.")
    return True

if __name__ == "__main__":
    validate_environment()
    print("[✔] Entorno corporativo validado con éxito.")
