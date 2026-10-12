"""Piezas compartidas por los videos: paleta y escena narrada.

El video de cada entrega hace `from herramientas_video.escena import *`, que trae
también todo manim.
"""

import json
import os
from pathlib import Path

import manimpango
from manim import *
from manim_voiceover import VoiceoverScene

from .creditos import CURSO, DANIEL, GABRIEL, INTEGRANTES, JOUBERT, NICOLAS, VOCES
from .voz import a_voz, crear_servicio, peso_hablado

# Identidad visual de la Universidad de los Andes: negro, amarillo y blanco
# (ver identidad/README.md).
config.background_color = "#000000"
# Sin serifas, como recomienda el manual: Arial, o una equivalente donde no está.
FUENTE = next(
    (f for f in ("Arial", "Liberation Sans", "Helvetica", "DejaVu Sans")
     if f in manimpango.list_fonts()),
    None,
)
if FUENTE:
    Text.set_default(font=FUENTE)

# Si está definida, cada paso narrado se guarda ahí como imagen, con su narración
# (ver guion.py y diapositivas.py).
CARPETA_DIAPOSITIVAS = os.getenv("DIAPOSITIVAS_DIR")

C_TEXTO = "#F2F2F2"
GRIS = "#9A9A9A"
C_AMARILLO = "#FFFF00"  # el amarillo oficial; es el color de acento
# Colores de apoyo, solo para distinguir series o categorías en una gráfica.
C_AZUL = "#5EC4E8"
C_MORADO = "#B39DFF"
C_NARANJA = "#FFB86B"
C_VERDE = "#6EE7B7"
C_ROSA = "#FF8AAE"
C_ROJO = "#FF6B6B"

# La pantalla mide 14,2 x 8 unidades. Nada debe pasar de x = ±6,9 ni bajar de y = −2,9:
# más abajo está la nota.
ANCHO_UTIL = 13.2


def ajustar(mob, ancho=ANCHO_UTIL):
    """Encoge el objeto si es más ancho que `ancho`."""
    if mob.width > ancho:
        mob.scale_to_fit_width(ancho)
    return mob


def lista(*renglones, font_size=30, color=C_TEXTO):
    """Renglones con viñeta, alineados a la izquierda. Cada uno se anima por separado: lista(...)[0]."""
    renglones = VGroup(
        *[Text(f"•  {renglon}", font_size=font_size, color=color) for renglon in renglones]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
    return ajustar(renglones, 12.4)


def figura(ruta, alto=4.6):
    """Imagen (por ejemplo, una gráfica exportada de un notebook) lista para la zona de trabajo."""
    return ImageMobject(str(ruta)).scale_to_fit_height(alto)


class EscenaNarrada(VoiceoverScene):
    """Escena con locución: cada tramo de voz marca la duración de su animación."""

    # Los define el video de cada entrega; salen en el guion y en las diapositivas.
    TITULO = ""
    LIMITE_MINUTOS = None

    def setup(self):
        self.set_speech_service(crear_servicio())
        self.nota_actual = None
        self.seccion_actual = None
        self.titulo_seccion = ""
        self.hablante_actual = None
        self.quien = None
        self.diapositivas = []

    def capturar(self, texto="", inicio=None, duracion=0.0):
        """Guarda el cuadro actual como diapositiva, con su narración como nota."""
        if not CARPETA_DIAPOSITIVAS:
            return
        carpeta = Path(CARPETA_DIAPOSITIVAS)
        carpeta.mkdir(parents=True, exist_ok=True)
        self.renderer.update_frame(self)
        self.diapositivas.append(
            {
                "nota": texto,
                "quien": self.quien if texto else None,
                "seccion": self.titulo_seccion,
                "inicio": round(self.renderer.time if inicio is None else inicio, 3),
                "duracion": round(duracion, 3),
                "fin": round(self.renderer.time, 3),
            }
        )
        imagen = self.renderer.camera.get_image()
        imagen.save(carpeta / f"{len(self.diapositivas):03d}.png")
        recorrido = {
            "titulo": self.TITULO,
            "limite_minutos": self.LIMITE_MINUTOS,
            "pasos": self.diapositivas,
        }
        (carpeta / "notas.json").write_text(
            json.dumps(recorrido, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    # ------------------------------------------------------- voz y textos

    def narrar(self, *tramos, quien=None, pausa=0.2):
        """Una locución partida en tramos (texto, acción).

        Cada acción recibe los segundos que dura su tramo, repartidos según lo
        que tarda en decirse el texto; si termina antes, se espera el resto.
        `quien` es el integrante que la dice; si se omite, sigue el anterior.
        """
        if quien or self.quien:
            self.hablante(quien or self.quien)
        texto = " ".join(t for t, _ in tramos)
        pesos = [peso_hablado(t) for t, _ in tramos]
        comienzo = self.renderer.time
        with self.voiceover(
            text=a_voz(texto), subcaption=texto, voz=VOCES.get(self.quien)
        ) as locucion:
            for (_, accion), peso in zip(tramos, pesos):
                duracion = locucion.duration * peso / sum(pesos)
                inicio = self.renderer.time
                if accion is not None:
                    accion(duracion)
                self.safe_wait(duracion - (self.renderer.time - inicio))
        self.safe_wait(pausa)
        self.capturar(texto, comienzo, locucion.duration)

    def paso(self, duracion, *animaciones, nota=None, tope=1.8, minimo=0.5):
        """Animaciones de un tramo, sin estirarlas más allá de `tope` segundos."""
        if nota is not None:
            self.nota(nota)
            duracion -= 0.4
        self.play(*animaciones, run_time=min(max(duracion, minimo), tope))

    def nota(self, texto, **colores):
        """Texto explicativo inferior: la idea del paso en una frase.

        `colores` resalta palabras: self.nota("El KPI sube", KPI=C_AMARILLO).
        """
        nueva = Text(texto, font_size=28, color=C_TEXTO, t2c=colores)
        ajustar(nueva).to_edge(DOWN, buff=0.45)
        animaciones = [FadeIn(nueva, shift=UP * 0.15)]
        if self.nota_actual is not None:
            animaciones.append(FadeOut(self.nota_actual, shift=UP * 0.15))
        self.play(*animaciones, run_time=0.4)
        self.nota_actual = nueva

    def seccion(self, texto):
        """Título de la sección, arriba a la izquierda. También divide el guion."""
        nueva = Text(texto, font_size=24, color=GRIS).to_corner(UL, buff=0.4)
        animaciones = [FadeIn(nueva)]
        if self.seccion_actual is not None:
            animaciones.append(FadeOut(self.seccion_actual))
        self.play(*animaciones, run_time=0.5)
        self.seccion_actual = nueva
        self.titulo_seccion = texto

    def hablante(self, quien):
        """Nombre de quien habla, arriba a la derecha."""
        if self.hablante_actual is not None and self.quien == quien:
            return
        self.quien = quien
        nueva = Text(quien, font_size=22, color=C_AMARILLO).to_corner(UR, buff=0.4)
        animaciones = [FadeIn(nueva)]
        if self.hablante_actual is not None:
            animaciones.append(FadeOut(self.hablante_actual))
        self.play(*animaciones, run_time=0.3)
        self.hablante_actual = nueva

    def firma(self):
        """Integrantes y curso, en la zona de la nota. Va al empezar la portada y se va con ella."""
        firma = VGroup(
            Text(" · ".join(INTEGRANTES), font_size=22, color=C_TEXTO),
            Text(CURSO, font_size=18, color=GRIS),
        ).arrange(DOWN, buff=0.14)
        ajustar(firma).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(firma), run_time=0.5)

    def limpiar(self):
        """Borra todo al terminar una sección."""
        self.capturar()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.nota_actual = None
        self.seccion_actual = None
        self.hablante_actual = None
