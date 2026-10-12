"""Transcribe clips de voz ya generados, para revisar cómo quedó la pronunciación.

Desde la raíz del repositorio:

    uv run python -m herramientas_video.revisar_voz "los KPIs" "machine learning"

Por cada fragmento busca en la caché (media/voiceovers) el primer clip cuyo guion
lo contiene y le pide a un modelo Gemini que escriba lo que se oye, sin corregir.
No genera ni modifica clips.

Sirve para atrapar lecturas muy erradas (siglas leídas como otra cosa, palabras en
inglés, palabras que faltan). No distingue matices: no reemplaza escuchar el video.
"""

import json
import sys

from google.genai import types

from .voz import CACHE_VOZ, a_voz, crear_cliente

MODELO = "gemini-3-flash-preview"
PREGUNTA = (
    "Escucha el audio en español y transcribe EXACTAMENTE los sonidos que se "
    "pronuncian, palabra por palabra. No corrijas ni normalices: si una sigla o una "
    "letra suelta se pronuncia con su nombre, escribe el nombre tal como suena (por "
    "ejemplo 'ka pe i', 'ese', 'te'). Devuelve solo la transcripción."
)


def main():
    fragmentos = sys.argv[1:]
    if not fragmentos:
        sys.exit(__doc__)
    cliente = crear_cliente()
    clips = [
        (entrada["input_data"]["input_text"], entrada["original_audio"])
        for entrada in json.loads((CACHE_VOZ / "cache.json").read_text(encoding="utf-8"))
        if entrada["input_data"].get("service") == "gemini_vertex"
    ]
    for fragmento in fragmentos:
        # el guion se guarda como se le envió a la voz, con la pronunciación ya convertida
        buscados = {fragmento.lower(), a_voz(fragmento).lower()}
        clip = next(
            (c for c in clips if any(b in c[0].lower() for b in buscados)), None
        )
        if clip is None:
            print(f"SIN CLIP : {fragmento}")
            continue
        texto, archivo = clip
        respuesta = cliente.models.generate_content(
            model=MODELO,
            contents=[
                types.Part.from_bytes(
                    data=(CACHE_VOZ / archivo).read_bytes(), mime_type="audio/wav"
                ),
                PREGUNTA,
            ],
            config=types.GenerateContentConfig(temperature=0),
        )
        print(f"GUION    : {texto}")
        print(f"SE OYE   : {respuesta.text.strip()}\n")


if __name__ == "__main__":
    main()
