import socket
import threading
import os
import shutil
from datetime import datetime

HOST = '0.0.0.0' # Escucha en todas las interfaces
PORT = 65432
BASE_DIR = '.'
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'registro.log')

log_lock = threading.Lock()

def registrar_evento(mensaje):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {mensaje}\n"
    print(log_entry.strip())
    with log_lock:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)

def manejar_cliente(conexion, direccion):
    registrar_evento(f"Nuevo cliente conectado desde {direccion}")
    try:
        while True:
            datos = conexion.recv(1024).decode('utf-8')
            if not datos:
                break
            
            partes = datos.split('|')
            comando = partes[0]
            
            if comando == 'LISTAR':
                # El cliente ahora envía: LISTAR|carpeta
                if len(partes) > 1 and partes[1] in ['entrada', 'procesados', 'logs']:
                    carpeta = partes[1]
                    ruta_carpeta = os.path.join(BASE_DIR, carpeta)
                    if os.path.exists(ruta_carpeta):
                        archivos = os.listdir(ruta_carpeta)
                        respuesta = "\n".join(archivos) if archivos else f"La carpeta '{carpeta}' está vacía."
                    else:
                        respuesta = f"ERROR: La carpeta '{carpeta}' no existe en el servidor."
                else:
                    respuesta = "ERROR: Carpeta no válida para listar."
                
                conexion.sendall(respuesta.encode('utf-8'))
                registrar_evento(f"Cliente {direccion} listó la carpeta: {partes[1] if len(partes)>1 else 'desconocida'}")
                
            elif comando == 'LEER':
                # El cliente envía: LEER|carpeta|nombre_archivo
                if len(partes) == 3:
                    carpeta = partes[1]
                    argumento = partes[2]
                    
                    if carpeta in ['entrada', 'procesados', 'logs']:
                        ruta_archivo = os.path.join(BASE_DIR, carpeta, argumento)
                        if os.path.exists(ruta_archivo):
                            with open(ruta_archivo, 'r') as f:
                                contenido = f.read()
                            conexion.sendall(contenido.encode('utf-8'))
                            registrar_evento(f"Cliente {direccion} leyó desde [{carpeta}]: {argumento}")
                        else:
                            conexion.sendall("ERROR: Archivo no encontrado.".encode('utf-8'))
                    else:
                        conexion.sendall("ERROR: Carpeta no válida.".encode('utf-8'))
                else:
                    conexion.sendall("ERROR: Formato de comando LEER incorrecto.".encode('utf-8'))
                    
            elif comando == 'SUBIR':
                if len(partes) == 3:
                    nombre_archivo, contenido = partes[1], partes[2]
                    ruta_archivo = os.path.join(BASE_DIR, 'entrada', nombre_archivo)
                    with open(ruta_archivo, 'w') as f:
                        f.write(contenido)
                    conexion.sendall(f"Archivo {nombre_archivo} subido exitosamente.".encode('utf-8'))
                    registrar_evento(f"Cliente {direccion} subió el archivo: {nombre_archivo}")
                else:
                    conexion.sendall("ERROR: Formato incorrecto.".encode('utf-8'))
                    
            elif comando == 'COPIAR':
                argumento = partes[1] if len(partes) > 1 else ""
                origen = os.path.join(BASE_DIR, 'entrada', argumento)
                destino = os.path.join(BASE_DIR, 'procesados', argumento)
                if os.path.exists(origen):
                    shutil.copy2(origen, destino)
                    conexion.sendall(f"Archivo {argumento} copiado a procesados.".encode('utf-8'))
                    registrar_evento(f"Cliente {direccion} copió el archivo: {argumento} a procesados.")
                else:
                    conexion.sendall("ERROR: Archivo no encontrado en entrada.".encode('utf-8'))

            elif comando == 'LOGS':
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, 'r') as f:
                        contenido = f.read()
                    conexion.sendall(contenido.encode('utf-8'))
                else:
                    conexion.sendall("El archivo de logs aún está vacío.".encode('utf-8'))
                registrar_evento(f"Cliente {direccion} solicitó ver los LOGS.")
                
            else:
                conexion.sendall("ERROR: Comando no reconocido.".encode('utf-8'))
                
    except Exception as e:
        registrar_evento(f"Error con el cliente {direccion}: {e}")
    finally:
        conexion.close()
        registrar_evento(f"Cliente {direccion} desconectado.")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"Servidor escuchando en el puerto {PORT}...")
    registrar_evento("Servidor iniciado.")
    try:
        while True:
            conexion, direccion = servidor.accept()
            hilo_cliente = threading.Thread(target=manejar_cliente, args=(conexion, direccion))
            hilo_cliente.start()
    except KeyboardInterrupt:
        print("\nApagando el servidor...")
        servidor.close()

if __name__ == "__main__":
    iniciar_servidor()