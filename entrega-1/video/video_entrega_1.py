"""Video de sustentación de la primera entrega (máximo 6 minutos).

Desde la raíz del repositorio:

    VOZ_SERVICIO=silencio uv run manim -ql entrega-1/video/video_entrega_1.py VideoCompleto
    uv run manim -qh --fps 30 entrega-1/video/video_entrega_1.py VideoCompleto

La primera orden hace un borrador mudo; la segunda, el video con la voz de prototipo
(Gemini TTS, configurada en .env). El flujo completo está en herramientas_video/README.md.

Cada `narrar()` es un paso del guion y una diapositiva. El guion que lee cada
integrante (guion.md) se genera a partir de este archivo.
"""

import sys
from pathlib import Path

# El repositorio no es un paquete instalable: se agrega su raíz para importar herramientas_video.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from herramientas_video.escena import *  # noqa: E402

AQUI = Path(__file__).parent


class EntregaBase(EscenaNarrada):
    TITULO = "Primera entrega"
    LIMITE_MINUTOS = 6

    def portada(self):
        self.firma()
        titulo = Text("Nombre del proyecto", font_size=56)
        subtitulo = Text("Primera entrega", font_size=34, color=C_AMARILLO)
        VGroup(titulo, subtitulo).arrange(DOWN, buff=0.5)
        self.narrar(
            (
                "Pendiente: una frase que presente el proyecto y la organización.",
                lambda d: self.paso(
                    d, Write(titulo), FadeIn(subtitulo, shift=UP * 0.2), tope=1.6
                ),
            ),
            quien=DANIEL,
        )
        self.limpiar()

    def acto_problematica(self):
        self.seccion("1. Problemática y entendimiento del negocio")
        puntos = lista(
            "Organización: pendiente",
            "Problemática u oportunidad: pendiente",
            "Objetivos y KPIs: pendiente",
        )
        self.narrar(
            (
                "Pendiente: quién es la organización y qué información del negocio "
                "muestra que el problema importa.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=DANIEL,
        )
        self.narrar(
            (
                "Pendiente: la problemática u oportunidad que se aborda con ciencia de datos.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.narrar(
            (
                "Pendiente: los objetivos del proyecto y los KPIs con los que se evaluará.",
                lambda d: self.paso(
                    d,
                    FadeIn(puntos[2], shift=RIGHT * 0.2),
                    nota="Los KPIs son métricas de negocio, no del modelo.",
                ),
            ),
        )
        self.limpiar()

    def acto_ideacion(self):
        self.seccion("2. Ideación: el producto de datos")
        puntos = lista(
            "Usuarios, procesos actuales y dolores: pendiente",
            "Requerimientos y componentes: pendiente",
            "Mockup: pendiente",
        )
        self.narrar(
            (
                "Pendiente: quiénes usarán el producto de datos, qué hacen hoy y qué les duele.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=NICOLAS,
        )
        self.narrar(
            (
                "Pendiente: los requerimientos del producto y sus componentes analíticos "
                "y tecnológicos.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.narrar(
            (
                # El mockup se muestra con figura(AQUI / "imagenes" / "mockup.png").
                "Pendiente: un recorrido corto por el mockup.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def acto_etica(self):
        self.seccion("3. Aspectos éticos y legales")
        puntos = lista(
            "Privacidad y confidencialidad: pendiente",
            "Transparencia y regulación: pendiente",
        )
        self.narrar(
            (
                "Pendiente: las implicaciones éticas y de privacidad del uso de estos datos.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: los aspectos regulatorios y cómo se atienden.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            quien=NICOLAS,
        )
        self.limpiar()

    def acto_enfoque(self):
        self.seccion("4. Enfoque analítico")
        puntos = lista(
            "Hipótesis o preguntas de negocio: pendiente",
            "Técnicas de análisis y de machine learning: pendiente",
            "Métricas de calidad del modelo: pendiente",
        )
        self.narrar(
            (
                "Pendiente: las hipótesis o preguntas de negocio que guían la experimentación.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=JOUBERT,
        )
        self.narrar(
            (
                "Pendiente: las técnicas con las que se responderán esas preguntas.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: las métricas con las que se evaluará el modelo.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def acto_datos(self):
        self.seccion("5. Recolección de datos")
        puntos = lista(
            "Fuentes de datos, estructura e importancia: pendiente",
            "Diccionario de datos: pendiente",
        )
        self.narrar(
            (
                "Pendiente: las fuentes de datos, cómo están estructuradas y cuáles "
                "son las más importantes.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: las entidades y atributos más relevantes del diccionario de datos.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            quien=JOUBERT,
        )
        self.limpiar()

    def acto_entendimiento(self):
        # Es la actividad que más pesa (35 %): merece la mayor parte del tiempo.
        self.seccion("6. Entendimiento de los datos")
        puntos = lista(
            "Calidad de los datos: pendiente",
            "Análisis univariado: pendiente",
            "Análisis multivariado: pendiente",
        )
        self.narrar(
            (
                "Pendiente: qué tan completos y consistentes son los datos, y si "
                "alcanzan para la solución planteada.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=GABRIEL,
        )
        self.narrar(
            (
                # Las gráficas del notebook se muestran con figura(AQUI / "imagenes" / "...png").
                "Pendiente: el hallazgo más importante del análisis univariado.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.narrar(
            (
                "Pendiente: el hallazgo más importante del análisis multivariado.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def cierre(self):
        self.seccion("7. Conclusiones iniciales")
        puntos = lista(
            "Conclusiones e insights: pendiente",
            "Próximas acciones: pendiente",
        )
        self.narrar(
            (
                "Pendiente: las primeras conclusiones e insights.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: las acciones que siguen para la entrega final.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            quien=GABRIEL,
            pausa=1.5,
        )
        self.limpiar()


# Escenas pequeñas, para probar por partes.


class Portada(EntregaBase):
    def construct(self):
        self.portada()


class Problematica(EntregaBase):
    def construct(self):
        self.acto_problematica()


class Ideacion(EntregaBase):
    def construct(self):
        self.acto_ideacion()


class Etica(EntregaBase):
    def construct(self):
        self.acto_etica()


class Enfoque(EntregaBase):
    def construct(self):
        self.acto_enfoque()


class Datos(EntregaBase):
    def construct(self):
        self.acto_datos()


class Entendimiento(EntregaBase):
    def construct(self):
        self.acto_entendimiento()


class Cierre(EntregaBase):
    def construct(self):
        self.cierre()


class VideoCompleto(EntregaBase):
    def construct(self):
        self.portada()
        self.acto_problematica()
        self.acto_ideacion()
        self.acto_etica()
        self.acto_enfoque()
        self.acto_datos()
        self.acto_entendimiento()
        self.cierre()
