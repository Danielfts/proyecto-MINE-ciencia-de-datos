"""Servicios de voz para manim-voiceover: Gemini TTS y un sustituto mudo.

Se configuran con variables de entorno o con el archivo .env de la raíz del
repositorio (ver .env.template):

    VOZ_SERVICIO=gemini            # o "silencio" para ajustar el ritmo sin generar voz
    GEMINI_API_KEY=...             # llave de Vertex AI del proyecto de Google Cloud
    VOZ_MODELO=gemini-3.1-flash-tts-preview
    VOZ_NOMBRE=Zephyr              # voz de la narración que no tiene integrante asignado
    VOZ_IDIOMA=es-419
    VOZ_ESTILO=...                 # instrucción de estilo opcional, antes de cada frase
    VOZ_VERTEX=0                   # solo si la llave es de la API de Gemini y no de Vertex AI

Sin VOZ_SERVICIO se usa "silencio": nadie genera voz, ni gasta cuota, por accidente.
"""

import os
import re
import time
import wave
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import types
from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service

RAIZ = Path(__file__).resolve().parents[1]
# Los clips de voz de todas las entregas comparten una caché, en la raíz del repositorio.
CACHE_VOZ = RAIZ / "media" / "voiceovers"
CACHE_SILENCIO = RAIZ / "media" / "voiceovers_silencio"

MODELO_POR_DEFECTO = "gemini-3.1-flash-tts-preview"
VOZ_POR_DEFECTO = "Zephyr"
IDIOMA_POR_DEFECTO = "es-419"
INTENTOS = 5

# Lo que escribimos en el guion y cómo debe leerlo la voz: parejas (patrón, hablado).
# El guion se escribe como se ve en pantalla y estas reglas lo convierten a como debe
# sonar. Al agregar una regla, comprobar que no cambie el texto de clips ya aprobados.
PRONUNCIACION = [
    # (r"\bKPIs?\b", "ka pe i"),
]

# Letras que ocupa, más o menos, un número de n cifras al decirlo en voz alta.
LETRAS_POR_CIFRAS = {1: 5, 2: 11, 3: 26, 4: 38}
CARACTERES_POR_SEGUNDO = 15
FRECUENCIA = 24000


def a_voz(texto):
    for patron, hablado in PRONUNCIACION:
        texto = re.sub(patron, hablado, texto)
    return texto


def peso_hablado(texto):
    """Longitud aproximada de la frase al pronunciarla; sirve para repartir el tiempo."""
    hablado = re.sub(
        r"\d+",
        lambda m: "x" * LETRAS_POR_CIFRAS.get(len(m.group()), 12 * len(m.group())),
        a_voz(texto),
    )
    return max(len(hablado), 1)


def guardar_wav(ruta, pcm):
    with wave.open(str(ruta), "wb") as salida:
        salida.setnchannels(1)
        salida.setsampwidth(2)
        salida.setframerate(FRECUENCIA)
        salida.writeframes(pcm)


def crear_cliente():
    """Cliente de Gemini con la llave de .env."""
    load_dotenv(find_dotenv(usecwd=True) or RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise RuntimeError("Falta GEMINI_API_KEY (en el entorno o en el archivo .env).")
    # La llave del equipo solo tiene habilitado Vertex AI, no generativelanguage.googleapis.com.
    if os.getenv("VOZ_VERTEX", "1") == "0":
        return genai.Client(api_key=clave)
    return genai.Client(vertexai=True, api_key=clave)


class ServicioSilencio(SpeechService):
    """Audio mudo con la duración estimada de cada frase."""

    def __init__(self, **kwargs):
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = cache_dir or self.cache_dir
        input_data = {
            "input_text": remove_bookmarks(text),
            "service": "silencio",
            "config": {"caracteres_por_segundo": CARACTERES_POR_SEGUNDO},
        }
        en_cache = self.get_cached_result(input_data, cache_dir)
        if en_cache is not None:
            return en_cache

        audio = path or self.get_audio_basename(input_data) + ".wav"
        duracion = peso_hablado(text) / CARACTERES_POR_SEGUNDO + 0.2
        guardar_wav(Path(cache_dir) / audio, b"\x00\x00" * int(FRECUENCIA * duracion))
        return {"input_text": text, "input_data": input_data, "original_audio": audio}


class ServicioGemini(SpeechService):
    """Gemini TTS a través de Vertex AI, autenticado con una llave de API."""

    def __init__(
        self,
        voz=VOZ_POR_DEFECTO,
        modelo=MODELO_POR_DEFECTO,
        idioma=IDIOMA_POR_DEFECTO,
        estilo="",
        **kwargs,
    ):
        initialize_speech_service(self, kwargs)
        self.voz = voz
        self.modelo = modelo
        self.idioma = idioma
        self.estilo = estilo.strip()
        self.cliente = crear_cliente()

    def _configuracion(self, voz):
        return types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                language_code=self.idioma,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voz)
                ),
            ),
        )

    def _sintetizar(self, texto, voz):
        """PCM de 16 bits a 24 kHz. Reintenta ante límites de cuota o respuestas sin audio."""
        contenido = f"{self.estilo} {texto}" if self.estilo else texto
        for intento in range(1, INTENTOS + 1):
            try:
                respuesta = self.cliente.models.generate_content(
                    model=self.modelo, contents=contenido, config=self._configuracion(voz)
                )
                return respuesta.candidates[0].content.parts[0].inline_data.data
            except Exception as error:
                if intento == INTENTOS:
                    raise
                espera = 4 * intento
                logger.warning(
                    f"Gemini TTS falló ({type(error).__name__}); reintento en {espera} s."
                )
                time.sleep(espera)

    def generate_from_text(self, text, cache_dir=None, path=None, voz=None, **kwargs):
        """`voz` cambia la voz de esta frase; así cada integrante suena distinto."""
        cache_dir = cache_dir or self.cache_dir
        voz = voz or self.voz
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "gemini_vertex",
            "config": {
                "voz": voz,
                "modelo": self.modelo,
                "idioma": self.idioma,
                "estilo": self.estilo,
            },
        }
        en_cache = self.get_cached_result(input_data, cache_dir)
        if en_cache is not None:
            return en_cache

        if os.getenv("VOZ_SOLO_CACHE"):
            raise RuntimeError(f"Sin clip en caché para: {input_text[:60]!r}")
        audio = path or self.get_audio_basename(input_data) + ".wav"
        guardar_wav(Path(cache_dir) / audio, self._sintetizar(input_text, voz))
        return {"input_text": text, "input_data": input_data, "original_audio": audio}


def crear_servicio():
    load_dotenv(find_dotenv(usecwd=True) or RAIZ / ".env")
    servicio = os.getenv("VOZ_SERVICIO", "silencio")
    if servicio == "silencio":
        # caché aparte: un borrador mudo puede correr a la vez que un render con voz
        return ServicioSilencio(cache_dir=CACHE_SILENCIO)
    if servicio == "gemini":
        return ServicioGemini(
            voz=os.getenv("VOZ_NOMBRE", VOZ_POR_DEFECTO),
            modelo=os.getenv("VOZ_MODELO", MODELO_POR_DEFECTO),
            idioma=os.getenv("VOZ_IDIOMA", IDIOMA_POR_DEFECTO),
            estilo=os.getenv("VOZ_ESTILO", ""),
            cache_dir=CACHE_VOZ,
        )
    raise ValueError(f"VOZ_SERVICIO desconocido: {servicio!r} (use 'gemini' o 'silencio')")
