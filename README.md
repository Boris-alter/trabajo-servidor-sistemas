# Sistema Multipropósito: Terminal, Hilos y Sincronización

Este proyecto es un sistema cliente-servidor desarrollado en Python para la gestión remota de archivos, Integra conceptos de comandos de terminal Linux, programación con hilos (threads) para concurrencia, y mecanismos de sincronización para evitar condiciones de carrera

## Requisitos Previos y Estructura

Antes de ejecutar el código, asegúrese de tener la siguiente estructura de directorios en su sistema Linux:

- `servidor_archivos/` (Carpeta principal)
  - `entrada/` (Debe contener archivos .txt de prueba)
  - `procesados/`
  - `logs/`

## 🚀 Instrucciones de Ejecución

[cite_start]Para iniciar el sistema de manera correcta, es necesario abrir **tres ventanas de terminal separadas**[cite: 42]:

1. **Terminal 1 (Servidor):**
   Navegue a la carpeta del proyecto y ejecute el servidor. Este quedará escuchando conexiones entrantes.
   `python3 servidor.py`

2. **Terminal 2 (Demonio):**
   Navegue a la misma carpeta y ejecute el demonio de procesamiento. Este escaneará la carpeta `entrada` cada 10 segundos.
   `python3 demonio.py`

3. **Terminal 3 (Cliente):**
   Ejecute el script interactivo del cliente para conectarse al servidor y utilizar el menú de opciones.
   `python3 cliente.py`

*(Nota: Si desea conectar un cliente desde otra computadora en la misma red local, debe cambiar la variable `HOST = '0.0.0.0'` en el servidor y configurar la IP local de la máquina anfitriona en el script del cliente).*

---

## Respuestas del item 2

**1. [cite_start]¿Cómo evitó condiciones de carrera en el servidor?** [cite: 44]
Se evitaron implementando un mecanismo de exclusión mutua mediante **Locks** (cerrojos) de la librería `threading` de Python. Se crearon dos candados lógicos (`log_lock` y `file_lock`). Al utilizar un bloque `with lock:`, se garantiza que cuando un hilo intenta escribir en el archivo `registro.log` o intenta mover un archivo de una carpeta a otra, ningún otro hilo pueda interferir hasta que la tarea termine y el cerrojo se libere

**2. [cite_start]¿Qué ventajas tiene usar threads en lugar de procesos para este caso?** [cite: 45]
Los hilos comparten el mismo espacio de memoria, lo que facilita enormemente compartir recursos globales como los objetos `Lock` sin recurrir a mecanismos complejos de comunicación entre procesos. Además, la creación de hilos consume muchos menos recursos del CPU y de la memoria RAM, lo cual es ideal para un servidor concurrente que pasa gran parte de su tiempo esperando operaciones de Entrada/Salida

**3. [cite_start]Explique el método de sincronización elegido.** [cite: 46]
Se eligió el **Lock (Mutex - Exclusión Mutua)** porque es el mecanismo más directo para proteger el acceso a un recurso único (como el archivo de registro). Al utilizar el contexto `with threading.Lock()`, el hilo en ejecución adquiere el cerrojo antes de la sección crítica y pone en espera a cualquier otro hilo que intente acceder. Una vez que termina la escritura, libera el cerrojo automáticamente, evitando corrupciones de datos e interbloqueos (deadlocks).

---

## Problemas, Inconvenientes y Soluciones

[cite_start]Durante el desarrollo de esta actividad, se presentaron los siguientes retos técnicos:

* **Problema 1: Creación y edición de archivos directamente en la terminal sin entorno gráfico.**
  * *Solución:* aprendi a utilizar el editor de texto interactivo `nano` directamente en la línea de comandos de Linux, utilizando los atajos `Ctrl + O` para guardar los cambios y `Ctrl + X` para cerrar el entorno de manera segura.

* **Problema 2: El cliente no podía leer archivos que ya habían sido procesados.**
  * *Contexto:* Inicialmente, la opción de "Leer archivo" del cliente solo buscaba en la carpeta `entrada`. Sin embargo, debido a que el demonio movía los archivos rápidamente a `procesados`, el cliente lanzaba un error de "Archivo no encontrado".
  * *Solución:* Se tuvo que rediseñar el protocolo de los sockets de comunicación. Se modificaron los comandos del servidor y del cliente para que aceptaran un formato dinámico (`LISTAR|carpeta` y `LEER|carpeta|nombre_archivo`). Esto permitió agregar un submenú en el cliente donde el usuario puede elegir exactamente de qué subdirectorio desea leer o listar.
