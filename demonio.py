import os
import time
import threading
import shutil
from datetime import datetime

# Rutas de las carpetas
BASE_DIR = '.'
ENTRADA_DIR = os.path.join(BASE_DIR, 'entrada')
PROCESADOS_DIR = os.path.join(BASE_DIR, 'procesados')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'registro.log')

# Candados (Locks) para sincronización [cite: 32, 35]
log_lock = threading.Lock()
file_lock = threading.Lock() 

def registrar_evento(mensaje):
    """Escribe en el log compartido de forma sincronizada con un Lock."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[DEMONIO] [{timestamp}] {mensaje}\n"
    print(log_entry.strip())
    
    # Adquirimos el Lock para que nadie más escriba en el log al mismo tiempo
    with log_lock:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)

def procesar_archivo(nombre_archivo):
    """Función que ejecuta el Thread para mover el archivo a procesados."""
    origen = os.path.join(ENTRADA_DIR, nombre_archivo)
    destino = os.path.join(PROCESADOS_DIR, nombre_archivo)
    
    # Usamos file_lock para evitar condiciones de carrera 
    # Si dos hilos se lanzan rápido, aseguramos que solo uno mueva el archivo a la vez.
    with file_lock:
        if os.path.exists(origen):
            try:
                shutil.move(origen, destino)
                registrar_evento(f"Archivo movido exitosamente: {nombre_archivo} -> procesados/")
            except Exception as e:
                registrar_evento(f"Error al mover {nombre_archivo}: {e}")

def iniciar_demonio():
    """Bucle principal que escanea la carpeta cada 10 segundos."""
    registrar_evento("Demonio iniciado. Escaneando la carpeta 'entrada' cada 10 segundos...")
    
    try:
        while True:
            # Listamos los archivos en la carpeta de entrada
            archivos = os.listdir(ENTRADA_DIR)
            
            for archivo in archivos:
                # Si hay archivos, iniciamos un Thread para cada uno 
                hilo_procesamiento = threading.Thread(target=procesar_archivo, args=(archivo,))
                hilo_procesamiento.start()
                
            # Dormimos el programa por 10 segundos 
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nApagando el demonio...")

if __name__ == "__main__":
    iniciar_demonio()