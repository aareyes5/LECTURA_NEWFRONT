from flask import Flask, request, send_from_directory, jsonify
import os
import shutil
import subprocess
from datetime import datetime
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'MP4/Videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rutas de las carpetas
videos_folder = 'MP4/Videos'
audios_folder = 'MP4/Audios'
imagenes_folder = 'MP4/Imagenes'
datos_folder = 'MP4/Datos'

# Asegurarse de que las carpetas existan
os.makedirs(videos_folder, exist_ok=True)
os.makedirs(audios_folder, exist_ok=True)
os.makedirs(imagenes_folder, exist_ok=True)
os.makedirs(datos_folder, exist_ok=True)

# Ruta para servir el HTML de la interfaz
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

# Ruta para servir los archivos estáticos como CSS y JS
@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    return send_from_directory('frontend', path)

# Ruta para manejar la subida de archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files and 'audio' not in request.files:
        return 'No file part', 400

    file_type = 'video' if 'video' in request.files else 'audio'
    file = request.files[file_type]
    if file.filename == '':
        return 'No selected file', 400

    if file:
        question_number = request.form.get('question_number')
        if not question_number:
            return 'Question number is required', 400

        # Definir el nombre y la ruta del archivo
        if file_type == 'video':
            filename = f'Video_{question_number}.mp4'
            folder = videos_folder
        else:
            filename = f'Audio_{question_number}.mp3'
            folder = audios_folder

        file_path = os.path.join(folder, filename)
        file.save(file_path)
        print(f"{file_type.capitalize()} for question {question_number} saved at {file_path}")

        # Verificar si es la última pregunta y si ambos archivos existen
        if int(question_number) == 10:
            video_path = os.path.join(videos_folder, f'Video_10.mp4')
            audio_path = os.path.join(audios_folder, f'Audio_10.mp3')
            lock_file_path = os.path.join(datos_folder, 'processing.lock')

            if os.path.exists(video_path) and os.path.exists(audio_path):
                # Verificar si el archivo de bloqueo existe
                if not os.path.exists(lock_file_path):
                    # Crear el archivo de bloqueo
                    open(lock_file_path, 'w').close()
                    print("Processing started...")

                    try:
                        # Ejecutar el script de procesamiento
                        subprocess.run(["python", "modulo_procesamiento/procesar_videos.py"], check=True)
                        print("Processing completed successfully.")
                    except subprocess.CalledProcessError as e:
                        print(f"Error during processing: {e}")
                    finally:
                        # Eliminar el archivo de bloqueo
                        os.remove(lock_file_path)
                        print("Lock file removed.")
                else:
                    print("Processing is already running or has been completed.")
            else:
                print("Waiting for both video and audio files to be uploaded for question 10.")

        return f'{file_type.capitalize()} uploaded successfully', 200

# Función para borrar contenido de una carpeta
def borrar_contenido_carpeta(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Error al eliminar {file_path}: {e}')

# Ruta para manejar la eliminación del contenido de las carpetas (excepto la de DATOS)
@app.route('/borrar-contenido', methods=['POST'])
def borrar_contenido():
    try:
        borrar_contenido_carpeta(videos_folder)
        borrar_contenido_carpeta(audios_folder)
        borrar_contenido_carpeta(imagenes_folder)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

# Ruta para guardar datos de usuario en un archivo DATOS numerado o con la fecha
@app.route('/guardar-datos', methods=['POST'])
def guardar_datos():
    try:
        # Leer todos los archivos en la carpeta DATOS y filtrar los que siguen el formato Datos_#.txt
        existing_files = [f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f.endswith('.txt')]

        # Extraer el número del archivo más alto existente
        max_number = 0
        for file in existing_files:
            try:
                # Extraer el número del archivo quitando 'Datos_' y '.txt'
                file_number = int(file[6:-4])
                if file_number > max_number:
                    max_number = file_number
            except ValueError:
                continue  # Ignorar archivos que no siguen el formato esperado

        # Crear un nuevo archivo de datos con el número más alto + 1
        new_file_number = max_number + 1
        filename = f'Datos_{new_file_number}.txt'

        data = request.json
        age = data.get('age')
        gender = data.get('gender')

        # Crear el archivo con la información del usuario
        datos_file_path = os.path.join(datos_folder, filename)
        with open(datos_file_path, 'w') as file:
            file.write(f"Género: {gender}\n")
            file.write(f"Edad: {age}\n")

        return jsonify({'success': True, 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
