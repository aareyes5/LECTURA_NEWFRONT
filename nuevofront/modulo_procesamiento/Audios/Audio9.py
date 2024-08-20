import pyaudio
import wave
import keyboard
import speech_recognition as sr
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import os

sexo = None
edad = None
current_dir = os.path.dirname(os.path.abspath(__file__))
ruta_puntaje = os.path.join(current_dir,'..',"..",'modulo_procesamiento','Puntaje','puntaje.txt')
valores = []

def leer_valores(ruta):
    """Lee los valores desde el archivo y los almacena en una lista."""
    valores = []
    if os.path.exists(ruta):
        with open(ruta, 'r') as archivo:
            for linea in archivo:
                try:
                    valor = int(linea.strip())
                    valores.append(valor)
                except ValueError:
                    print(f"No se pudo convertir '{linea.strip()}' a entero.")
    return valores

def escribir_valores(ruta, valores):
    """Escribe los valores en el archivo, uno por línea."""
    with open(ruta, 'w') as archivo:
        for valor in valores:
            archivo.write(f"{valor}\n")
            
"""
# Configuración de PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "audio2.wav"

# Inicializar PyAudio
audio = pyaudio.PyAudio()

# Función para grabar audio
def grabar_audio():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    print("Grabando... Presiona 's' para detener.")
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed('s'):
            print("Grabación detenida.")
            break
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Guardar la grabación en un archivo WAV
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

# Función para convertir audio a texto
def audio_a_texto(file):
    r = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio_data = r.record(source)
        texto = r.recognize_google(audio_data, language='es-ES')
        return texto
"""

# Evaluar el texto y asignar un puntaje
def evaluar_texto(texto):
    # Palabras clave para cada nivel de tristeza
    niveles = {
        0: ["pensamientos positivos", "optimista", "sin pensamientos negativos"],
        1: ["ligeros pensamientos negativos", "ocasionalmente pesimista"],
        2: ["pensamientos negativos a veces", "pesimismo ocasional"],
        3: ["pensamientos pesimistas frecuentes", "preocupado y negativo"],
        4: ["pensamientos muy pesimistas", "totalmente negativo", "angustiado"],
        5: ["extremadamente pesimista", "sin esperanza", "totalmente negativo"],
        6: ["pensamientos suicidas", "desesperanza total", "pensamientos graves y desesperados"]
    }
    palabras = texto.split()  # Dividir el texto en palabras
    max_nivel = 0

    # Análisis de palabras individuales
    for palabra in palabras:
        for nivel, palabras_clave in niveles.items():
            if palabra in palabras_clave:
                if nivel > max_nivel:
                    max_nivel = nivel

    # Análisis de combinaciones de 2 a n palabras
    for n in range(2, len(palabras) + 1):
        for comb in combinations(palabras, n):
            frase = ' '.join(comb)
            for nivel, palabras_clave in niveles.items():
                for palabra_clave in palabras_clave:
                    if palabra_clave in frase:
                        if nivel > max_nivel:
                            max_nivel = nivel

    return max_nivel

# Cargar el modelo y el scaler
current_dir = os.path.dirname(os.path.abspath(__file__))
ruta_red = os.path.join(current_dir,'..','..','modulo_procesamiento','Red','madrs_model.h5')
model = load_model(ruta_red)

ruta_scaler = os.path.join(current_dir,'scaler.pkl')
scaler = joblib.load(ruta_scaler)


# Función para predecir el puntaje de la Pregunta 9
def predecir_puntaje(edad, sexo, puntaje9):
    # Crear un array con las entradas necesarias
    entrada = np.array([[edad, sexo, 0, 0, 0, 0, 0, 0, 0, puntaje9, 0]])  # Los valores de las preguntas 3-10 se inicializan en 0
    entrada_estandarizada = scaler.transform(entrada)
    predicciones = model.predict(entrada_estandarizada)
    puntaje_predicho = predicciones[0][0]  # La predicción de la Pregunta 2 es el primer valor
    print(f'Puntaje predicho sin redondeo: {puntaje_predicho}')
    
    #Codigo para rendondear el puntaje
    if puntaje_predicho < 0:
        puntaje_redondeado = 0
    elif puntaje_predicho > 6:
        puntaje_redondeado = 6
    else:
        decimal = abs(puntaje_predicho) - int(abs(puntaje_predicho))
        if decimal < 0.5:
            puntaje_redondeado = int(puntaje_predicho)
        else:
            puntaje_redondeado = int(puntaje_predicho) + 1
    return puntaje_redondeado

"""
# Capturar audio
print("Presiona 'r' para iniciar la grabación.")
keyboard.wait('r')
grabar_audio()

# Convertir el audio a texto
texto = audio_a_texto(WAVE_OUTPUT_FILENAME)
print(f'Texto del audio: {texto}')
"""

# Evaluar el texto
current_dir = os.path.dirname(os.path.abspath(__file__))
ruta_texto = os.path.join(current_dir,"..","..","modulos_seniales","Audios","AudioPregunta_9.txt")
puntaje_inicial = evaluar_texto(ruta_texto)
print(f'Puntaje evaluado de la Pregunta 9: {puntaje_inicial}')

"""
# Obtener edad y sexo del usuario
edad = int(input("Ingrese la edad: "))
sexo = int(input("Ingrese el sexo (0 para Femenino, 1 para Masculino): "))
"""
#obtener los valores del arreglo puntaje
valores = leer_valores(ruta_puntaje)
edad = valores[0]
sexo = valores[1]

# Predecir el puntaje usando el modelo entrenado
puntaje_predicho = predecir_puntaje(edad, sexo, puntaje_inicial)
print(f'Puntaje predicho para la Pregunta 9: {puntaje_predicho}')

#escribir puntaje en archivo
valores.append(puntaje_predicho)
escribir_valores(ruta_puntaje, valores)

