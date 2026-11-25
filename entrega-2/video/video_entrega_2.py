"""Video de sustentación de la entrega final (máximo 12 minutos).

Desde la raíz del repositorio:

    VOZ_SERVICIO=silencio uv run manim -ql entrega-2/video/video_entrega_2.py VideoCompleto
    uv run manim -qh --fps 30 entrega-2/video/video_entrega_2.py VideoCompleto

La primera orden hace un borrador mudo; la segunda, el video con la voz de prototipo
(Gemini TTS, configurada en .env). El flujo completo está en herramientas_video/README.md.

Cada `narrar()` es un paso del guion y una diapositiva. El guion que lee cada
integrante (guion.md) se genera a partir de este archivo.

El tiempo se reparte según el peso de cada actividad en la nota de la entrega final:
preparación de datos 20 %, validación 5 %, modelos 20 %, producto 20 %,
retroalimentación de la organización 15 % y conclusiones 15 %.

Las secciones 1 a 7 son las del video de la primera entrega, sin cambios: se toman de
entrega-1/video/video_entrega_1.py, no se copian, y cada una lleva en pantalla y en el
guion la marca de heredada y pendiente de aprobación. Para ajustar una, se copia aquí
su método y se quita la marca (ver `heredado`).
"""

import importlib.util
import sys
from pathlib import Path

# El repositorio no es un paquete instalable: se agrega su raíz para importar herramientas_video.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from herramientas_video.escena import *  # noqa: E402

AQUI = Path(__file__).parent


def cargar_video(ruta, nombre):
    """Importa el video de otra entrega como módulo aparte.

    Sus escenas no entran a este módulo, así que manim no las ofrece como escenas de
    este video. Sus actos siguen usando sus propias imágenes y ayudas (AQUI, caja,
    figura...), porque se resuelven en su módulo.
    """
    especificacion = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules[nombre] = modulo
    especificacion.loader.exec_module(modulo)
    return modulo


primera = cargar_video(AQUI.parent.parent / "entrega-1" / "video" / "video_entrega_1.py",
                       "video_entrega_1")


def heredado(acto):
    """Un acto de la primera entrega, sin cambios, con la marca de heredado en cada paso."""
    def acto_heredado(self):
        self.heredado = True
        try:
            acto(self)
        finally:
            self.heredado = False

    return acto_heredado


class EntregaBase(primera.EntregaBase):
    TITULO = "Entrega final"
    LIMITE_MINUTOS = 12
    # Participan los cuatro, incluido Gabriel, que no estuvo en la primera entrega.
    INTEGRANTES = [DANIEL, NICOLAS, JOUBERT, GABRIEL]

    # Secciones 1 a 7: las de la primera entrega, tal cual, pendientes de aprobación.
    # Hereda de su EntregaBase para que sus actos encuentren sus ayudas (despejar).
    # Su `cierre` es la sección 7; aquí `cierre` es la sección 13.
    acto_problematica = heredado(primera.EntregaBase.acto_problematica)
    acto_ideacion = heredado(primera.EntregaBase.acto_ideacion)
    acto_etica = heredado(primera.EntregaBase.acto_etica)
    acto_enfoque = heredado(primera.EntregaBase.acto_enfoque)
    acto_datos = heredado(primera.EntregaBase.acto_datos)
    acto_entendimiento = heredado(primera.EntregaBase.acto_entendimiento)
    acto_conclusiones_iniciales = heredado(primera.EntregaBase.cierre)

    def portada(self):
        self.firma()
        titulo = Text("Transición predial 2027", font_size=56)
        subtitulo = Text("Entrega final", font_size=34, color=C_AMARILLO)
        VGroup(titulo, subtitulo).arrange(DOWN, buff=0.5)
        self.narrar(
            (
                "Pendiente: una frase que presente el proyecto y lo que trae la entrega final.",
                lambda d: self.paso(
                    d, Write(titulo), FadeIn(subtitulo, shift=UP * 0.2), tope=1.6
                ),
            ),
            quien=DANIEL,
        )
        self.limpiar()

    def acto_preparacion(self):
        self.seccion("8. Preparación de datos")
        puntos = lista(
            "Unidad de análisis y variable objetivo: pendiente",
            "Limpieza y nuevas características: pendiente",
            "Codificación, escalado e imputación: pendiente",
        )
        self.narrar(
            (
                "Pendiente: qué predios entran al modelo y qué se predice.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=NICOLAS,
        )
        self.narrar(
            (
                # El diagrama de bloques se exporta a imagenes/ y se muestra con figura(...).
                "Pendiente: cómo se limpiaron los datos y qué características nuevas se crearon.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.narrar(
            (
                "Pendiente: las transformaciones que se ajustan solo con entrenamiento.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def acto_validacion(self):
        self.seccion("9. Estrategia de validación")
        puntos = lista(
            "Estrategia de experimentación: pendiente",
            "Partición y sus distribuciones: pendiente",
        )
        self.narrar(
            (
                "Pendiente: cómo se entrenan y se eligen los modelos.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: la partición en entrenamiento, validación y prueba, y que "
                "conserva la distribución original.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            quien=NICOLAS,
        )
        self.limpiar()

    def acto_modelos(self):
        self.seccion("10. Construcción y evaluación del modelo")
        puntos = lista(
            "Tres algoritmos y sus hiperparámetros: pendiente",
            "Evaluación frente a la línea base: pendiente",
            "Evaluación cualitativa y mejoras: pendiente",
        )
        self.narrar(
            (
                "Pendiente: los tres algoritmos y los hiperparámetros que se probaron.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=JOUBERT,
        )
        self.narrar(
            (
                "Pendiente: el mejor modelo en prueba, frente a repetir el pago de 2025.",
                lambda d: self.paso(
                    d,
                    FadeIn(puntos[1], shift=RIGHT * 0.2),
                    nota="Las métricas del modelo no son los KPIs del negocio.",
                ),
            ),
        )
        self.narrar(
            (
                "Pendiente: qué aprende el modelo, dónde se equivoca y qué lo mejoraría.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def acto_producto(self):
        self.seccion("11. Producto de datos")
        puntos = lista(
            "Arquitectura: pendiente",
            "Demostración de la aplicación: pendiente",
            "Despliegue: pendiente",
        )
        self.narrar(
            (
                # El diagrama de arquitectura se exporta a imagenes/ y se muestra con figura(...).
                "Pendiente: los componentes del producto y cómo se conectan.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=DANIEL,
        )
        self.narrar(
            (
                # Capturas de la aplicación en imagenes/.
                "Pendiente: un recorrido por un escenario en la aplicación.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.narrar(
            (
                "Pendiente: cómo se despliega el producto.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def acto_retroalimentacion(self):
        self.seccion("12. Retroalimentación de la organización")
        puntos = lista(
            "Interacciones y acuerdos: pendiente",
            "Presentación de resultados y próximos pasos: pendiente",
        )
        self.narrar(
            (
                "Pendiente: las interacciones con Multiaservi y lo que se acordó en cada una.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=GABRIEL,
        )
        self.narrar(
            (
                "Pendiente: qué opinó la organización del producto y qué sigue.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
        )
        self.limpiar()

    def cierre(self):
        self.seccion("13. Conclusiones")
        puntos = lista(
            "Resultados y objetivos: pendiente",
            "Dificultades y condiciones de los datos: pendiente",
            "Impacto en los KPIs: pendiente",
        )
        self.narrar(
            (
                "Pendiente: los resultados más relevantes y si se cumplieron los objetivos.",
                lambda d: self.paso(d, FadeIn(puntos[0], shift=RIGHT * 0.2)),
            ),
            quien=GABRIEL,
        )
        self.narrar(
            (
                "Pendiente: las mayores dificultades y qué datos darían mejores resultados.",
                lambda d: self.paso(d, FadeIn(puntos[1], shift=RIGHT * 0.2)),
            ),
            (
                "Pendiente: cómo cambiarían los KPIs con el producto en uso y si el modelo "
                "basta para resolver el problema.",
                lambda d: self.paso(d, FadeIn(puntos[2], shift=RIGHT * 0.2)),
            ),
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


class ConclusionesIniciales(EntregaBase):
    def construct(self):
        self.acto_conclusiones_iniciales()


class Preparacion(EntregaBase):
    def construct(self):
        self.acto_preparacion()


class Validacion(EntregaBase):
    def construct(self):
        self.acto_validacion()


class Modelos(EntregaBase):
    def construct(self):
        self.acto_modelos()


class Producto(EntregaBase):
    def construct(self):
        self.acto_producto()


class Retroalimentacion(EntregaBase):
    def construct(self):
        self.acto_retroalimentacion()


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
        self.acto_conclusiones_iniciales()
        self.acto_preparacion()
        self.acto_validacion()
        self.acto_modelos()
        self.acto_producto()
        self.acto_retroalimentacion()
        self.cierre()
