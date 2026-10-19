"""Guion del video, para que cada integrante lea su parte.

Desde la raíz del repositorio:

    uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py

Recorre la escena VideoCompleto sin animar y escribe guion.md junto al video: quién
dice qué, en qué momento, cuánto dura el video y cuánto habla cada integrante.

Los tiempos son estimados (15 caracteres por segundo). Con --grabaciones CARPETA se
miden con la voz grabada por los integrantes (ver voz.py). Con --voz se miden con los
clips de Gemini que ya estén en caché, y falla si falta alguno.

No genera voz ni renderiza el video.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .creditos import INTEGRANTES
from .voz import CARACTERES_POR_SEGUNDO, RAIZ

SIN_ASIGNAR = "Sin asignar"


def recorrer(archivo, escena="VideoCompleto", calidad="-ql", con_voz=False, grabaciones=None):
    """Recorre la escena sin animar. Devuelve (carpeta de capturas, recorrido).

    Deja una imagen por paso narrado y el recorrido de notas.json: título, límite
    de minutos y, por paso, narración, integrante, sección y tiempos.
    """
    archivo = Path(archivo).resolve()
    carpeta = RAIZ / "media" / "diapositivas" / archivo.stem
    shutil.rmtree(carpeta, ignore_errors=True)
    entorno = dict(os.environ, DIAPOSITIVAS_DIR=str(carpeta))
    if grabaciones:
        entorno.update(VOZ_SERVICIO="grabaciones", VOZ_GRABACIONES=str(Path(grabaciones).resolve()))
    elif con_voz:
        entorno.update(VOZ_SERVICIO="gemini", VOZ_SOLO_CACHE="1")
    else:
        entorno["VOZ_SERVICIO"] = "silencio"
    orden = [sys.executable, "-m", "manim", calidad, "-s", "--progress_bar", "none",
             str(archivo), escena]
    resultado = subprocess.run(orden, cwd=RAIZ, env=entorno, capture_output=True, text=True)
    notas = carpeta / "notas.json"
    if resultado.returncode or not notas.exists():
        sys.exit((resultado.stderr or resultado.stdout)[-4000:] or "manim no dejó capturas")
    return carpeta, json.loads(notas.read_text(encoding="utf-8"))


def reloj(segundos):
    segundos = round(segundos)
    return f"{segundos // 60}:{segundos % 60:02d}"


def resumen(pasos):
    """Por integrante: segundos de voz y palabras, en el orden del equipo."""
    cuenta = {nombre: [0.0, 0] for nombre in INTEGRANTES}
    for paso in pasos:
        if paso["nota"]:
            fila = cuenta.setdefault(paso["quien"] or SIN_ASIGNAR, [0.0, 0])
            fila[0] += paso["duracion"]
            fila[1] += len(paso["nota"].split())
    return cuenta


def escribir(recorrido, archivo, orden, con_voz):
    pasos = recorrido["pasos"]
    total = max((paso["fin"] for paso in pasos), default=0.0)
    limite = recorrido["limite_minutos"]
    cuenta = resumen(pasos)
    voz_total = sum(segundos for segundos, _ in cuenta.values()) or 1.0

    lineas = [
        f"# Guion: {recorrido['titulo'] or archivo.stem}",
        "",
        f"Generado a partir de `{archivo.name}`. No lo edite a mano: cambie la narración "
        "en ese archivo y vuelva a generarlo desde la raíz del repositorio con",
        "",
        f"    {orden}",
        "",
    ]
    duracion = f"**Duración: {reloj(total)}**"
    if limite:
        duracion += f" de un máximo de {reloj(limite * 60)}."
        if total > limite * 60:
            duracion += f" **Se pasa del límite por {reloj(total - limite * 60)}.**"
    lineas += [
        duracion,
        con_voz if isinstance(con_voz, str) else
        "Tiempos medidos con la voz del prototipo." if con_voz else
        f"Tiempos estimados a {CARACTERES_POR_SEGUNDO} caracteres por segundo; "
        "cambian cuando cada quien lea su parte.",
        "",
        "| Integrante | Tiempo de voz | Participación | Palabras |",
        "| --- | --- | --- | --- |",
    ]
    for nombre, (segundos, palabras) in cuenta.items():
        lineas.append(
            f"| {nombre} | {reloj(segundos)} | {segundos / voz_total:.0%} | {palabras} |"
        )
    callados = [n for n in INTEGRANTES if cuenta[n][1] == 0]
    if callados:
        lineas += ["", f"**Todavía no tienen parte:** {', '.join(callados)}."]

    # Bloques: pasos seguidos de un mismo integrante, aunque crucen secciones
    # (segundos de voz, inicio, fin), indexados por el primer paso del bloque
    narrados = [paso for paso in pasos if paso["nota"]]
    bloques = {}
    for i, paso in enumerate(narrados):
        if i and paso["quien"] == narrados[i - 1]["quien"]:
            segundos, desde, _ = bloques[primero]
            bloques[primero] = (segundos + paso["duracion"], desde, paso["fin"])
        else:
            primero = i
            bloques[i] = (paso["duracion"], paso["inicio"], paso["fin"])

    seccion, quien = None, None
    for i, paso in enumerate(narrados):
        if i in bloques:
            segundos, desde, hasta = bloques[i]
            lineas += ["", f"> **Bloque de {paso['quien'] or SIN_ASIGNAR}: {reloj(segundos)} de voz** "
                           f"({reloj(desde)} a {reloj(hasta)})"]
        if paso["seccion"] != seccion:
            seccion, quien = paso["seccion"], None
            lineas += ["", f"## {seccion or 'Portada'}"]
        if paso["quien"] != quien:
            quien = paso["quien"]
            lineas += ["", f"**{reloj(paso['inicio'])} · {quien or SIN_ASIGNAR}**"]
        lineas += ["", paso["nota"]]

    destino = archivo.parent / "guion.md"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return destino, total, limite


def main():
    opciones = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    opciones.add_argument("video", help="archivo .py del video, con la escena VideoCompleto")
    opciones.add_argument("--escena", default="VideoCompleto")
    opciones.add_argument("--grabaciones", metavar="CARPETA",
                          help="medir los tiempos con la voz grabada (carpeta con indice.json)")
    opciones.add_argument("--voz", action="store_true",
                          help="medir los tiempos con los clips de Gemini en caché")
    args = opciones.parse_args()

    archivo = Path(args.video).resolve()
    _, recorrido = recorrer(archivo, args.escena, con_voz=args.voz, grabaciones=args.grabaciones)
    orden = f"uv run python -m herramientas_video.guion {archivo.relative_to(RAIZ).as_posix()}"
    medicion = "Tiempos medidos con las grabaciones de los integrantes." if args.grabaciones else args.voz
    destino, total, limite = escribir(recorrido, archivo, orden, medicion)
    print(f"{destino.relative_to(RAIZ)}: {reloj(total)}"
          + (f" de {reloj(limite * 60)}" if limite else ""))


if __name__ == "__main__":
    main()
