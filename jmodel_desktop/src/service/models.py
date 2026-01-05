import os

def listar_modelos_desde_env():
    ruta_base = os.getenv('ABSOLUTE_PATH_MODELS')
    if not ruta_base:
        print("Error: La variable 'ABSOLUTE_PATH_MODELS' no está configurada.")
        return {}
    if not os.path.isdir(ruta_base):
        print(f"Error: La ruta '{ruta_base}' no es un directorio válido.")
        return {}

    modelos_dict = {
        archivo: os.path.join(ruta_base, archivo)
        for archivo in os.listdir(ruta_base)
        if os.path.isfile(os.path.join(ruta_base, archivo))
    }

    return modelos_dict