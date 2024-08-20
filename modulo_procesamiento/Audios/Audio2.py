import pyaudio
import wave
import keyboard
import speech_recognition as sr
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import os
from itertools import combinations

sexo = None
edad = None

valores = []
current_dir = os.path.dirname(os.path.abspath(__file__))
ruta_puntaje = os.path.join(current_dir,'..',"..",'modulo_procesamiento','Puntaje','puntaje.txt')


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

# Evaluar el texto y asignar un puntaje
def evaluar_texto(texto):
    # Palabras clave para cada nivel de tristeza
    niveles = {
        0: ["feliz", "alegre", "contento", "bien", "animado"],
        1: ["ocasionalmente", "poco", "circunstancias"],
        2: ["a veces", "de vez en cuando", "ligeramente"],
        3: ["empeorando", "preocupado", "estresado"],
        4: ["triste", "desanimado", "melancólico", "afligido"],
        5: ["muy triste", "miserable", "abatido", "desesperado"],
        6: ["sin esperanza", "desesperación", "angustia", "terrible", "insoportable"]
    }

    palabras = texto.split()  # Dividir el texto en palabras
    max_nivel = 0

    # Análisis de palabras individuales
    for palabra in palabras:
        for nivel, palabras_clave in niveles.items():
            if palabra in palabras_clave:
                if nivel > max_nivel:
                    max_nivel = nivel

    # Análisis de combinaciones de 2 a n palabras en orden de izquierda a derecha
    n = len(palabras)
    for i in range(n):
        for j in range(i + 2, n + 1):  # Comienza en i + 2 para considerar combinaciones de al menos 2 palabras
            frase = ' '.join(palabras[i:j])
            for nivel, palabras_clave in niveles.items():
                for palabra_clave in palabras_clave:
                    if palabra_clave in frase:
                        if nivel > max_nivel:
                            max_nivel = nivel

    return max_nivel

# Cargar el modelo y el scaler

ruta_red = os.path.join(current_dir,'..',"..",'modulo_procesamiento','Red','madrs_model.h5')
model = load_model(ruta_red)
ruta_scaler = os.path.join(current_dir,'scaler.pkl')
scaler = joblib.load(ruta_scaler)

# Función para predecir el puntaje de la Pregunta 2
def predecir_puntaje(edad, sexo, puntaje2):
    # Crear un array con las entradas necesarias
    entrada = np.array([[edad, sexo, puntaje2, 0, 0, 0, 0, 0, 0, 0, 0]])  # Los valores de las preguntas 3-10 se inicializan en 0
    entrada_estandarizada = scaler.transform(entrada)
    predicciones = model.predict(entrada_estandarizada)
    puntaje_predicho = predicciones[0][0]  # La predicción de la Pregunta 2 es el primer valor
    print(f'Puntaje predicho sin redondeo: {puntaje_predicho}')
    
    # Codigo para redondear el puntaje
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

# Evaluar el texto
current_dir = os.path.dirname(os.path.abspath(__file__))
ruta_texto = os.path.join(current_dir,"..","..","modulos_seniales","Audios","AudioPregunta_2.txt")

with open(ruta_texto, 'r') as archivo:
    texto = archivo.read()

puntaje_inicial = evaluar_texto(texto)
print(f'Puntaje evaluado de la Pregunta 2: {puntaje_inicial}')

# Obtener edad y sexo del usuario
valores = leer_valores(ruta_puntaje)
edad = valores[0]
sexo = valores[1]

# Predecir el puntaje usando el modelo entrenado
puntaje_predicho = predecir_puntaje(edad, sexo, puntaje_inicial)
print(f'Puntaje predicho para la Pregunta 2: {puntaje_predicho}')

# Escribir puntaje en archivo
valores.append(puntaje_predicho)
escribir_valores(ruta_puntaje, valores)
