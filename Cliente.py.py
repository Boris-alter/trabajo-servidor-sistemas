import socket
import os

HOST = '127.0.0.1' 
PORT = 65432

def mostrar_menu():
    print("\n" + "="*30)
    print("      MENÚ DEL CLIENTE")
    print("="*30)
    print("1. Listar archivos en el servidor (Seleccionar Carpeta)")
    print("2. Subir un archivo al servidor (a carpeta entrada)")
    print("3. Descargar/Leer un archivo del servidor")
    print("4. Copiar archivo a procesados (remoto)")
    print("5. Ver logs de operaciones")
    print("6. Salir")
    return input("Elige una opción (1-6): ")

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
        print("✅ Conectado al servidor exitosamente.")
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        return

    try:
        while True:
            opcion = mostrar_menu()

            if opcion == '1':
                # SUBMENÚ PARA ELEGIR QUÉ CARPETA LISTAR
                print("\n--- ¿Qué carpeta deseas enlistar? ---")
                print("1. entrada")
                print("2. procesados")
                print("3. logs")
                opc_carpeta = input("Selecciona una carpeta (1-3): ")
                
                carpeta = ""
                if opc_carpeta == '1': carpeta = "entrada"
                elif opc_carpeta == '2': carpeta = "procesados"
                elif opc_carpeta == '3': carpeta = "logs"
                else:
                    print("⚠️ Opción de carpeta no válida.")
                    continue
                
                # Enviamos el comando con el formato modificado: LISTAR|carpeta
                mensaje = f"LISTAR|{carpeta}"
                cliente.sendall(mensaje.encode('utf-8'))
                respuesta = cliente.recv(4096).decode('utf-8')
                print(f"\n--- Archivos en la carpeta remota '{carpeta}' ---")
                print(respuesta)

            elif opcion == '2':
                archivo_local = input("Introduce el nombre del archivo local a subir (ej. mi_archivo_local.txt): ")
                if os.path.exists(archivo_local):
                    with open(archivo_local, 'r') as f:
                        contenido = f.read()
                    mensaje = f"SUBIR|{archivo_local}|{contenido}"
                    cliente.sendall(mensaje.encode('utf-8'))
                    respuesta = cliente.recv(4096).decode('utf-8')
                    print(f"\nRespuesta del servidor: {respuesta}")
                else:
                    print("❌ Error: El archivo local no existe.")

            elif opcion == '3':
                # Al leer, también te pregunta de qué carpeta proviene, aprovechando que ya las listaste
                print("\n--- ¿De qué carpeta deseas leer el archivo? ---")
                print("1. entrada")
                print("2. procesados")
                print("3. logs")
                opc_carpeta = input("Selecciona la carpeta (1-3): ")
                
                carpeta = ""
                if opc_carpeta == '1': carpeta = "entrada"
                elif opc_carpeta == '2': carpeta = "procesados"
                elif opc_carpeta == '3': carpeta = "logs"
                else:
                    print("⚠️ Opción no válida.")
                    continue
                
                archivo_remoto = input(f"Introduce el nombre del archivo exacto en '{carpeta}': ")
                mensaje = f"LEER|{carpeta}|{archivo_remoto}"
                cliente.sendall(mensaje.encode('utf-8'))
                respuesta = cliente.recv(4096).decode('utf-8')
                
                if respuesta.startswith("ERROR"):
                    print(f"\n{respuesta}")
                else:
                    nombre_descarga = f"descargado_{carpeta}_{archivo_remoto}"
                    with open(nombre_descarga, 'w') as f:
                        f.write(respuesta)
                    print(f"\n✅ Archivo leído con éxito desde '{carpeta}'")
                    print(f"💾 Guardado localmente como: {nombre_descarga}")
                    print(f"--- Contenido del Archivo ---\n{respuesta}")

            elif opcion == '4':
                archivo_remoto = input("Introduce el nombre del archivo a copiar a procesados: ")
                mensaje = f"COPIAR|{archivo_remoto}"
                cliente.sendall(mensaje.encode('utf-8'))
                respuesta = cliente.recv(4096).decode('utf-8')
                print(f"\nRespuesta del servidor: {respuesta}")

            elif opcion == '5':
                cliente.sendall("LOGS|".encode('utf-8'))
                respuesta = cliente.recv(4096).decode('utf-8')
                print("\n--- Logs del Servidor ---")
                print(respuesta)

            elif opcion == '6':
                print("Desconectando del servidor... ¡Hasta luego!")
                break
            else:
                print("⚠️ Opción no válida. Intenta de nuevo.")
                
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
    finally:
        cliente.close()

if __name__ == "__main__":
    iniciar_cliente()