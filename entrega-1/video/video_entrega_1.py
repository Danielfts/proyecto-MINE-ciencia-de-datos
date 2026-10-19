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


# El wireframe del producto es el mismo del reporte.
MOCKUP = AQUI.parent / "reporte" / "imagenes" / "mockup.png"
# Regiones numeradas del wireframe, en píxeles (x0, y0, x1, y1) de la imagen de 1280 × 1267.
REGIONES_MOCKUP = {
    1: (25, 103, 383, 955),  # tarifas y límites de crecimiento
    2: (25, 972, 383, 1243),  # alertas de guardrails
    3: (408, 100, 1240, 455),  # indicadores
    4: (408, 470, 1240, 605),  # en palabras simples
    5: (408, 620, 1240, 1142),  # gráficas
}

# Presupuesto de voz por sección, en segundos, según el peso de cada actividad en la
# nota. Suma 335 s: con las transiciones, el video queda por debajo de los 6 minutos.
# guion.md muestra cuánto dura cada sección de verdad.
#   portada 10 · 1. Problemática 40 · 2. Ideación 40 · 3. Ética 30 · 4. Enfoque 45
#   5. Recolección 30 · 6. Entendimiento 110 · 7. Conclusiones 30
# Bloques continuos de voz, grabados por cada integrante (audios/):
#   Daniel: portada, 1 y 2 hasta la arquitectura · Nicolás: el wireframe, 3 y 4
#   Joubert: 5 y la primera mitad de 6 · Daniel: la segunda mitad de 6 y 7

IMAGENES = AQUI / "imagenes"  # gráficas recortadas del notebook de entendimiento


def caja(titulo, detalle=None, font_size=24, borde=GRIS):
    """Rectángulo redondeado con un título y, debajo, un detalle en gris."""
    def renglones(texto, **estilo):
        return VGroup(*[Text(r, **estilo) for r in texto.split("\n")]).arrange(DOWN, buff=0.08)

    textos = VGroup(renglones(titulo, font_size=font_size, color=C_TEXTO))
    if detalle:
        textos.add(renglones(detalle, font_size=font_size * 0.75, color=GRIS))
    textos.arrange(DOWN, buff=0.12)
    marco = RoundedRectangle(
        corner_radius=0.12, width=textos.width + 0.5, height=textos.height + 0.4,
        stroke_color=borde, stroke_width=2,
    ).move_to(textos)
    return VGroup(marco, textos)


def flecha(origen, destino, etiqueta=None):
    """Flecha gris del borde derecho de `origen` al izquierdo de `destino`."""
    trazo = Arrow(
        origen.get_right(), destino.get_left(), buff=0.12, color=GRIS, stroke_width=3,
        max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=8,
    )
    if etiqueta is None:
        return trazo
    return VGroup(trazo, Text(etiqueta, font_size=20, color=GRIS).next_to(trazo, UP, buff=0.1))


def cifra(valor, etiqueta):
    """Una cifra grande en amarillo con su etiqueta debajo."""
    return VGroup(
        Text(valor, font_size=54, color=C_AMARILLO, weight=BOLD),
        Text(etiqueta, font_size=22, color=GRIS, line_spacing=0.8),
    ).arrange(DOWN, buff=0.18)


def ficha(texto):
    """Etiqueta pequeña con borde, para las metas y los guardrails."""
    rotulo = Text(texto, font_size=20, color=C_TEXTO)
    marco = RoundedRectangle(
        corner_radius=0.25, width=rotulo.width + 0.5, height=0.55,
        stroke_color=GRIS, stroke_width=1.5,
    ).move_to(rotulo)
    return VGroup(marco, rotulo)


def igualar(*cajas):
    """Da a todas las cajas el ancho de la más ancha, para alinearlas en una grilla."""
    ancho = max(c[0].width for c in cajas)
    for c in cajas:
        c[0].stretch_to_fit_width(ancho)
    return VGroup(*cajas)


def numero(n, radio=0.2):
    """Círculo amarillo con un número negro, como los del wireframe."""
    return VGroup(
        Circle(radius=radio, fill_color=C_AMARILLO, fill_opacity=1, stroke_width=0),
        Text(str(n), font_size=22, color="#000000", weight=BOLD),
    )


class EntregaBase(EscenaNarrada):
    TITULO = "Primera entrega"
    LIMITE_MINUTOS = 6

    def despejar(self, duracion, *objetos):
        """Retira lo que mostró el paso anterior, con su nota, antes del siguiente."""
        if self.nota_actual is not None:
            objetos += (self.nota_actual,)
            self.nota_actual = None
        self.paso(duracion, FadeOut(Group(*objetos)), tope=0.8)

    def portada(self):
        self.firma()
        titulo = Text("Transición predial 2027", font_size=60, weight=BOLD)
        subtitulo = Text(
            "Un producto de datos para fijar tarifas\ndespués de la actualización catastral",
            font_size=30, color=C_TEXTO, line_spacing=0.9,
        )
        entrega = Text("Primera entrega", font_size=30, color=C_AMARILLO)
        VGroup(titulo, subtitulo, entrega).arrange(DOWN, buff=0.45).shift(UP * 0.5)
        self.narrar(
            (
                "Transición predial 2027: un producto de datos para fijar las tarifas del "
                "impuesto predial después de una actualización catastral.",
                lambda d: self.paso(
                    d, Write(titulo), FadeIn(subtitulo, shift=UP * 0.2),
                    FadeIn(entrega, shift=UP * 0.2), tope=2.0,
                ),
            ),
            quien=DANIEL,
        )
        self.limpiar()

    def acto_problematica(self):
        self.seccion("1. Problemática y entendimiento del negocio")

        # La organización y el choque de los avalúos
        consultora = caja("Multiaservi Consultores", "gestión tributaria · más de 21 años")
        alcaldia = caja("Alcaldía de un municipio colombiano", "catastro recién actualizado")
        VGroup(consultora, alcaldia).arrange(RIGHT, buff=1.8).move_to(UP * 1.9)
        asesora = flecha(consultora, alcaldia, "asesora")
        cifras = VGroup(
            cifra("×4,1", "avalúo mediano\n2025 → 2026"),
            cifra("10,8 → 5,6 ‰", "tarifa mediana"),
            cifra("≈ ×2", "impuesto predial\nfacturado"),
        ).arrange(RIGHT, buff=1.3, aligned_edge=UP).move_to(DOWN * 0.9)
        self.narrar(
            (
                "Multiaservi Consultores asesora a un municipio colombiano que acaba de "
                "actualizar su catastro.",
                lambda d: self.paso(
                    d,
                    LaggedStart(FadeIn(consultora), GrowArrow(asesora[0]),
                                FadeIn(asesora[1]), FadeIn(alcaldia), lag_ratio=0.35),
                    tope=2.4,
                ),
            ),
            (
                "Su avalúo mediano se multiplicó por 4,1",
                lambda d: self.paso(d, FadeIn(cifras[0], shift=UP * 0.2)),
            ),
            (
                "y, aunque bajó la tarifa, el impuesto facturado casi se duplicó.",
                lambda d: self.paso(
                    d,
                    LaggedStart(FadeIn(cifras[1], shift=UP * 0.2),
                                FadeIn(cifras[2], shift=UP * 0.2), lag_ratio=0.5),
                    nota="Los avalúos se cuadruplicaron; el impuesto, casi se duplicó.",
                ),
            ),
            quien=DANIEL,
        )

        # La brecha frente al impuesto pleno y el plazo de los límites
        pleno = Rectangle(width=10, height=0.9, stroke_color=C_TEXTO, stroke_width=2)
        facturado = Rectangle(
            width=5, height=0.9, fill_color=C_AMARILLO, fill_opacity=1, stroke_width=0
        ).align_to(pleno, LEFT)
        barra = VGroup(pleno, facturado).move_to(UP * 1.2)
        rotulo_pleno = Text("Impuesto pleno: avalúo × tarifa", font_size=24, color=C_TEXTO)
        rotulo_pleno.next_to(pleno, UP, buff=0.2).align_to(pleno, LEFT)
        rotulo_facturado = Text("Facturado en 2026 · 50 %", font_size=24, color="#000000",
                                weight=BOLD).move_to(facturado)
        brecha = VGroup(
            Text("Brecha", font_size=24, color=C_AMARILLO, weight=BOLD),
            Text("68 400 millones de pesos", font_size=20, color=C_AMARILLO),
        ).arrange(DOWN, buff=0.08).move_to(pleno.get_right() + LEFT * 2.5)

        eje = Line(LEFT * 4.5, RIGHT * 4.5, color=GRIS, stroke_width=2).move_to(DOWN * 1.5)
        vigencia = Line(eje.get_left(), eje.get_right(), color=C_AMARILLO, stroke_width=8)
        marcas = VGroup(*[
            VGroup(Line(UP * 0.15, DOWN * 0.15, color=GRIS).move_to(eje.point_from_proportion(p)),
                   Text(t, font_size=22, color=C_TEXTO).next_to(
                       eje.point_from_proportion(p), DOWN, buff=0.3))
            for p, t in ((0, "2026"), (0.5, "2027"), (1, "fin de 2027"))
        ])
        rotulo_vigencia = Text("Límites transitorios al aumento del impuesto", font_size=22,
                               color=C_AMARILLO).next_to(eje, UP, buff=0.25)

        def mostrar_brecha(d):
            self.despejar(d * 0.3, consultora, alcaldia, asesora, cifras)
            self.paso(d * 0.7, Create(pleno), FadeIn(rotulo_pleno),
                      GrowFromEdge(facturado, LEFT), FadeIn(rotulo_facturado),
                      FadeIn(brecha), tope=2.0)

        self.narrar(
            (
                "Aun así, se facturó solo la mitad del impuesto pleno: una brecha de 68 mil "
                "millones de pesos.",
                mostrar_brecha,
            ),
            (
                "Y los límites al aumento vencen en 2027.",
                lambda d: self.paso(
                    d, Create(eje), FadeIn(marcas), Create(vigencia), FadeIn(rotulo_vigencia),
                    nota="2027 es la última oportunidad de una transición gradual.",
                ),
            ),
        )

        # El objetivo y los KPIs
        objetivo = Text(
            "Objetivo: apoyar el proyecto de acuerdo de tarifas y límites de 2027\n"
            "con un producto de datos que compare escenarios",
            font_size=26, color=C_TEXTO, line_spacing=0.9, t2c={"Objetivo:": C_AMARILLO},
        )
        ajustar(objetivo).move_to(UP * 2.4)

        def tarjeta(titulo, que_mide, valor, base):
            textos = VGroup(
                Text(titulo, font_size=22, color=C_AMARILLO, weight=BOLD),
                Text(que_mide, font_size=20, color=GRIS, line_spacing=0.8),
                Text(valor, font_size=48, color=C_TEXTO, weight=BOLD),
                Text(base, font_size=20, color=GRIS),
            ).arrange(DOWN, buff=0.15)
            marco = RoundedRectangle(corner_radius=0.15, width=max(4.6, textos.width + 0.5),
                                     height=2.9, stroke_color=GRIS, stroke_width=2).move_to(textos)
            return VGroup(marco, textos)

        convergencia = tarjeta("KPI 1 · Convergencia", "impuesto facturado / impuesto pleno",
                               "50 %", "en 2026")
        choque = tarjeta("KPI 2 · Choque en la cola",
                         "aumento en el 1 % de predios\ncon mayor impuesto", "56 %",
                         "del aumento de 2026")
        VGroup(convergencia, choque).arrange(RIGHT, buff=2.2).move_to(DOWN * 0.15)
        tension = VGroup(
            DoubleArrow(convergencia.get_right(), choque.get_left(), buff=0.2, color=C_AMARILLO,
                        stroke_width=4, max_tip_length_to_length_ratio=0.2),
        )
        tension.add(Text("se oponen", font_size=20, color=C_AMARILLO).next_to(tension[0], UP, 0.1))
        fichas = VGroup(
            ficha("Meta: recaudo"), ficha("Guardrail: progresividad"),
            ficha("Guardrail: legalidad"),
        ).arrange(RIGHT, buff=0.4).move_to(DOWN * 2.25)

        def mostrar_objetivo(d):
            self.despejar(d * 0.3, barra, rotulo_pleno, rotulo_facturado, brecha, eje, vigencia,
                          marcas, rotulo_vigencia)
            self.paso(d * 0.7, FadeIn(objetivo, shift=DOWN * 0.2))

        self.narrar(
            (
                "El objetivo: comparar escenarios de tarifas para 2027",
                mostrar_objetivo,
            ),
            (
                "con dos indicadores opuestos: cuánto se acerca el impuesto al pleno",
                lambda d: self.paso(d, FadeIn(convergencia, shift=UP * 0.2),
                                    GrowFromCenter(tension)),
            ),
            (
                "y cuánto sube para los predios de mayor impuesto,",
                lambda d: self.paso(d, FadeIn(choque, shift=UP * 0.2)),
            ),
            (
                "sin sacrificar recaudo, progresividad ni legalidad.",
                lambda d: self.paso(
                    d, LaggedStart(*[FadeIn(f, shift=UP * 0.15) for f in fichas],
                                   lag_ratio=0.3),
                    nota="Acercarse al pleno aumenta el choque: hay que equilibrarlos.",
                ),
            ),
        )
        self.limpiar()

    def acto_ideacion(self):
        self.seccion("2. Ideación: el producto de datos")

        # Usuarios, proceso actual y dolores
        etapas = VGroup(
            caja("Consultores de\nMultiaservi", "hojas de cálculo", font_size=22,
                 borde=C_AMARILLO),
            caja("Hacienda y\nPlaneación", "revisan", font_size=22),
            caja("Alcalde", "ajusta", font_size=22),
            caja("Concejo\nMunicipal", "debate y aprueba", font_size=22),
        ).arrange(RIGHT, buff=0.9)
        ajustar(etapas).move_to(UP * 1.9)
        pasos = VGroup(*[flecha(a, b) for a, b in zip(etapas[:-1], etapas[1:])])
        usuarios = Text("usuarios", font_size=20, color=C_AMARILLO).next_to(etapas[0], DOWN, 0.15)
        dolores = lista(
            "Cada escenario nuevo se recalcula a mano, en plena negociación",
            "El trabajo no se acumula entre municipios ni entre vigencias",
            "Cada tarifa se justifica en palabras simples ante el Concejo",
            "Lo facturado no es lo que se recauda",
            font_size=26,
        ).move_to(DOWN * 0.95)
        self.narrar(
            (
                "Lo usan los consultores de Multiaservi, que hoy arman cada propuesta en hojas "
                "de cálculo antes de que pase por la alcaldía y el Concejo.",
                lambda d: self.paso(
                    d,
                    LaggedStart(*[
                        AnimationGroup(FadeIn(etapa), *([GrowArrow(pasos[i - 1])] if i else []))
                        for i, etapa in enumerate(etapas)
                    ], FadeIn(usuarios), lag_ratio=0.4),
                    tope=3.0,
                ),
            ),
            (
                "Cada escenario nuevo se rehace a mano y cada tarifa debe explicarse en "
                "palabras simples.",
                lambda d: self.paso(
                    d, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in dolores],
                                   lag_ratio=0.5),
                    nota="Cuatro dolores del proceso actual.", tope=3.0,
                ),
            ),
            quien=DANIEL,
        )

        # Componentes analíticos y tecnológicos
        datos = caja("Datos", "catastro LADM-COL\n+ facturación del predial", font_size=22)
        motor = caja("Motor de escenarios", "tarifas y topes por predio", font_size=22)
        modelo = caja("Modelo de ML", "probabilidad de pago", font_size=22)
        api = caja("API REST", font_size=22)
        app = caja("Aplicación web", "consultora y alcaldía", font_size=22)
        exportacion = caja("Exportación congelada", "insumo para el Concejo", font_size=22)
        nucleo = VGroup(motor, modelo).arrange(DOWN, buff=0.6)
        salidas = VGroup(app, exportacion).arrange(DOWN, buff=0.6)
        arquitectura = VGroup(datos, nucleo, api, salidas).arrange(RIGHT, buff=0.9)
        ajustar(arquitectura).move_to(UP * 0.55)
        enlaces_nucleo = VGroup(flecha(datos, motor), flecha(datos, modelo))
        enlaces_api = VGroup(flecha(motor, api), flecha(modelo, api))
        enlaces_salidas = VGroup(flecha(api, app), flecha(api, exportacion))
        tecnologia = Text("Python · pandas · scikit-learn · FastAPI · Dash", font_size=22,
                          color=GRIS).move_to(DOWN * 2.15)

        def mostrar_nucleo(d):
            self.despejar(d * 0.3, etapas, pasos, usuarios, dolores)
            self.paso(d * 0.7, FadeIn(datos), *[GrowArrow(f) for f in enlaces_nucleo],
                      FadeIn(motor), FadeIn(modelo), tope=2.0)

        self.narrar(
            (
                "Proponemos un motor de escenarios y un modelo que estima la probabilidad de "
                "pago de cada predio,",
                mostrar_nucleo,
            ),
            (
                "servidos por una API y una aplicación web.",
                lambda d: self.paso(
                    d, *[GrowArrow(f) for f in enlaces_api], FadeIn(api),
                    GrowArrow(enlaces_salidas[0]), FadeIn(app), FadeIn(tecnologia),
                ),
            ),
            (
                "Al Concejo llega un escenario congelado, no el simulador.",
                lambda d: self.paso(
                    d, GrowArrow(enlaces_salidas[1]), FadeIn(exportacion),
                    nota="Escenarios en segundos, alertas, trazabilidad y ningún dato personal.",
                ),
            ),
        )

        # Recorrido por el wireframe
        mockup = figura(MOCKUP, alto=5.6).move_to(LEFT * 3.0 + UP * 0.35)
        escala = mockup.height / 1267
        esquina = mockup.get_corner(UL)

        def region(n):
            x0, y0, x1, y1 = REGIONES_MOCKUP[n]
            return Rectangle(
                width=(x1 - x0) * escala, height=(y1 - y0) * escala,
                stroke_color=C_AMARILLO, stroke_width=5,
            ).move_to(esquina + RIGHT * (x0 + x1) / 2 * escala + DOWN * (y0 + y1) / 2 * escala)

        leyenda = VGroup(*[
            VGroup(numero(n), Text(texto, font_size=24, color=C_TEXTO)).arrange(RIGHT, buff=0.25)
            for n, texto in enumerate([
                "Tarifas y límites de crecimiento", "Alertas de guardrails",
                "Indicadores frente a 2026", "Lectura en palabras simples", "Gráficas",
            ], start=1)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(mockup, RIGHT, buff=0.6)
        marco = region(1)

        def mostrar_mockup(d):
            self.despejar(d * 0.3, datos, nucleo, api, salidas, enlaces_nucleo, enlaces_api,
                          enlaces_salidas, tecnologia)
            self.paso(d * 0.7, FadeIn(mockup), Create(marco), FadeIn(leyenda[0]))

        self.narrar(
            (
                "En el prototipo se fijan tarifas y límites,",
                mostrar_mockup,
            ),
            (
                "se ven las alertas",
                lambda d: self.paso(d, Transform(marco, region(2)), FadeIn(leyenda[1])),
            ),
            (
                "y los indicadores,",
                lambda d: self.paso(d, Transform(marco, region(3)), FadeIn(leyenda[2])),
            ),
            (
                "y se lee el resultado en palabras simples.",
                lambda d: self.paso(
                    d, Transform(marco, VGroup(region(4), region(5))),
                    FadeIn(leyenda[3]), FadeIn(leyenda[4]),
                    nota="Wireframe: las cifras entre corchetes son marcadores.",
                ),
            ),
            quien=NICOLAS,
        )
        self.limpiar()

    def acto_etica(self):
        self.seccion("3. Aspectos éticos y legales")
        tarjetas = igualar(
            caja("Privacidad", "Ley 1581 de 2012\nsin nombres ni documentos\nninguna salida individual",
                 borde=C_AMARILLO),
            caja("Transparencia", "Ley 1712 de 2014\nregistros reservados\nla decisión es pública"),
            caja("Legalidad", "Leyes 44 de 1990 y 1995 de 2019\ntopes al aumento del impuesto"),
            caja("Equidad", "el modelo estima recaudo agregado\ny no señala contribuyentes"),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.6, 0.5))
        ajustar(tarjetas).move_to(UP * 0.3)
        self.narrar(
            (
                "Los datos catastrales vinculan predios con personas. Por la Ley 1581, el archivo "
                "de análisis no tiene nombres ni documentos, y ninguna salida muestra un predio "
                "individual.",
                lambda d: self.paso(d, FadeIn(tarjetas[0], shift=UP * 0.2)),
            ),
            (
                "Lo público es la decisión, no los registros: al Concejo llegan agregados "
                "explicables, con el recaudo esperado como una estimación.",
                lambda d: self.paso(d, FadeIn(tarjetas[1], shift=UP * 0.2)),
            ),
            (
                "El motor respeta los topes legales al aumento del impuesto,",
                lambda d: self.paso(d, FadeIn(tarjetas[2], shift=UP * 0.2)),
            ),
            (
                "y el modelo de pago solo estima el recaudo agregado: no señala a ningún "
                "contribuyente.",
                lambda d: self.paso(d, FadeIn(tarjetas[3], shift=UP * 0.2),
                                    nota="Minimización de datos desde el diseño."),
            ),
            quien=NICOLAS,
        )
        self.limpiar()

    def acto_enfoque(self):
        self.seccion("4. Enfoque analítico")

        def columna(rotulo, pregunta, componente, detalle, metricas):
            cabeza = VGroup(
                Text(rotulo, font_size=26, color=C_AMARILLO, weight=BOLD),
                Text(pregunta, font_size=22, color=C_TEXTO, line_spacing=0.85),
            ).arrange(DOWN, buff=0.2)
            bloque = caja(componente, detalle, font_size=24)
            pie = Text(metricas, font_size=20, color=GRIS, line_spacing=0.85)
            return VGroup(cabeza, bloque, pie).arrange(DOWN, buff=0.4)

        escenarios = columna(
            "Pregunta 1 · Escenarios",
            "¿Qué tarifas y límites para 2027 acercan\nel impuesto al pleno sin un choque excesivo?",
            "Motor de escenarios", "malla de escenarios →\nfrontera convergencia–choque",
            "Validación: reproducir el impuesto de 2026",
        )
        pago = columna(
            "Pregunta 2 · Pago",
            "¿Qué tan bien se anticipa\nsi un predio pagará?",
            "Clasificación binaria", "regresión logística · árbol de decisión\ngradient boosting",
            "ROC-AUC · log-loss · calibración\nfrente a repetir el pago de 2025",
        )
        columnas = VGroup(escenarios, pago).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        ajustar(columnas).move_to(UP * 0.55)
        separador = DashedLine(UP * 2.9, DOWN * 1.6, color=GRIS, stroke_width=1.5).move_to(
            (escenarios.get_right() + pago.get_left()) / 2 * RIGHT + UP * 0.65)
        recaudo = Text("Recaudo esperado = suma de cada impuesto × su probabilidad de pago",
                       font_size=24, color=C_AMARILLO)
        ajustar(recaudo).move_to(DOWN * 2.15)
        self.narrar(
            (
                "Primera pregunta: qué tarifas y límites acercan el impuesto al pleno sin un "
                "choque excesivo en la cola.",
                lambda d: self.paso(d, FadeIn(escenarios[0], shift=DOWN * 0.2), Create(separador)),
            ),
            (
                "La responde el motor de escenarios: recorre una malla de escenarios, muestra la "
                "frontera entre convergencia y choque, y se valida reproduciendo el impuesto de "
                "2026.",
                lambda d: self.paso(d, FadeIn(escenarios[1], shift=UP * 0.2),
                                    FadeIn(escenarios[2])),
            ),
            quien=NICOLAS,
        )
        self.narrar(
            (
                "Segunda: qué tan bien se anticipa si un predio pagará. Es una clasificación "
                "binaria con tres algoritmos: regresión logística, árbol de decisión y gradient "
                "boosting,",
                lambda d: self.paso(d, FadeIn(pago[0], shift=DOWN * 0.2),
                                    FadeIn(pago[1], shift=UP * 0.2), tope=2.4),
            ),
            (
                "evaluados con ROC-AUC, log-loss y calibración, frente a repetir el pago de 2025.",
                lambda d: self.paso(d, FadeIn(pago[2])),
            ),
            (
                "Con esas probabilidades, el recaudo esperado es la suma de cada impuesto por su "
                "probabilidad de pago.",
                lambda d: self.paso(d, FadeIn(recaudo, shift=UP * 0.2),
                                    nota="El modelo describe asociaciones de 2026, no reacciones a otra tarifa."),
            ),
        )
        self.limpiar()

    def acto_datos(self):
        self.seccion("5. Recolección de datos")
        catastro = caja("Levantamiento\ncatastral", "INTERLIS · LADM-COL", font_size=22)
        postgres = caja("PostgreSQL", "217 → 45 tablas", font_size=22)
        programa = caja("SQL + Python", "un predio por fila", font_size=22)
        parquet = caja("Archivo de predios", "22 220 predios\nsin datos personales", font_size=22,
                       borde=C_AMARILLO)
        cadena = VGroup(catastro, postgres, programa, parquet).arrange(RIGHT, buff=0.85)
        ajustar(cadena).move_to(UP * 1.2)
        enlaces = VGroup(*[flecha(a, b) for a, b in zip(cadena[:-1], cadena[1:])])
        facturacion = caja("Facturación del predial", "Secretaría de Hacienda · 2025–2026",
                           font_size=22).move_to(DOWN * 1.3 + LEFT * 3.0)
        union = Arrow(facturacion.get_right(), parquet.get_bottom(), buff=0.15, color=GRIS,
                      stroke_width=3, max_tip_length_to_length_ratio=0.12)
        rotulo_union = Text("impuesto 2026 y pago 2025–2026\npor número predial", font_size=20,
                            color=GRIS, line_spacing=0.85).next_to(union.get_center(), DR, buff=0.15)
        self.narrar(
            (
                "Los datos vienen de dos fuentes. La principal es el levantamiento catastral en el "
                "modelo LADM-COL: lo cargamos en PostgreSQL y lo podamos de 217 a 45 tablas útiles.",
                lambda d: self.paso(
                    d, LaggedStart(FadeIn(catastro), GrowArrow(enlaces[0]), FadeIn(postgres),
                                   GrowArrow(enlaces[1]), FadeIn(programa), lag_ratio=0.35),
                    tope=3.0,
                ),
            ),
            (
                "La segunda es la facturación del predial: de ella solo tomamos el impuesto de 2026 "
                "y si el predio pagó en 2025 y 2026.",
                lambda d: self.paso(d, FadeIn(facturacion, shift=UP * 0.2)),
            ),
            (
                "Todo se une por número predial en un archivo de 22 220 predios, sin datos "
                "personales y con su diccionario de datos.",
                lambda d: self.paso(
                    d, GrowArrow(enlaces[2]), FadeIn(parquet), GrowArrow(union), FadeIn(rotulo_union),
                    nota="El catastro es la fuente de todo atributo catastral.",
                ),
            ),
            quien=JOUBERT,
        )
        self.limpiar()

    def acto_entendimiento(self):
        # Es la actividad que más pesa (35 %): merece la mayor parte del tiempo.
        self.seccion("6. Entendimiento de los datos")

        # Unidad de análisis
        unidad = VGroup(
            cifra("22 220", "predios del\nlevantamiento"),
            cifra("16 705", "base del avalúo:\nindividuales con construcción"),
        ).arrange(RIGHT, buff=1.6, aligned_edge=UP).move_to(UP * 0.4)
        paso_unidad = Arrow(unidad[0][0].get_right(), unidad[1][0].get_left(), buff=0.4,
                            color=GRIS, stroke_width=3)
        self.narrar(
            (
                "En el notebook de entendimiento analizamos los 22 220 predios. Como los regímenes "
                "se valoran distinto, el análisis del avalúo usa 16 705 predios individuales con "
                "construcción, el 75 % del total.",
                lambda d: self.paso(d, FadeIn(unidad[0], shift=UP * 0.2), GrowArrow(paso_unidad),
                                    FadeIn(unidad[1], shift=UP * 0.2), tope=2.4),
            ),
            quien=JOUBERT,
        )

        # Univariado
        histograma = figura(IMAGENES / "avaluo-log.png", alto=2.9)
        ajustar(histograma, 12.6).move_to(UP * 1.2)
        novedades = VGroup(
            cifra("236 M", "avalúo mediano\n(pesos)"),
            cifra("64 %", "cambió su\nnúmero predial"),
            cifra("10 %", "predios\nnuevos"),
        ).arrange(RIGHT, buff=1.5, aligned_edge=UP).move_to(DOWN * 1.55)

        def mostrar_histograma(d):
            self.despejar(d * 0.3, unidad, paso_unidad)
            self.paso(d * 0.7, FadeIn(histograma), FadeIn(novedades[0], shift=UP * 0.2),
                      nota="Univariado: histogramas y QQ-plots, en escala original y log10.")

        self.narrar(
            (
                "El avalúo es muy asimétrico: la mediana es de 236 millones de pesos, y en escala "
                "logarítmica queda casi simétrico.",
                mostrar_histograma,
            ),
            (
                "Y el catastro anterior estaba desactualizado: el 64 % de los predios cambió su "
                "número predial, y el 10 % son nuevos.",
                lambda d: self.paso(d, LaggedStart(FadeIn(novedades[1], shift=UP * 0.2),
                                                   FadeIn(novedades[2], shift=UP * 0.2),
                                                   lag_ratio=0.5)),
            ),
        )

        # Multivariado
        pca = figura(IMAGENES / "pca-varianza.png", alto=4.6).move_to(LEFT * 3.3 + UP * 0.35)
        tamano = VGroup(
            cifra("50 %", "de la varianza en el\nprimer componente: el tamaño"),
            cifra("0,92", "correlación del tamaño\ncon el avalúo"),
        ).arrange(DOWN, buff=0.7).next_to(pca, RIGHT, buff=1.0)

        def mostrar_pca(d):
            self.despejar(d * 0.3, histograma, novedades)
            self.paso(d * 0.7, FadeIn(pca), FadeIn(tamano[0], shift=UP * 0.2))

        self.narrar(
            (
                "En lo multivariado, el avalúo depende casi solo del tamaño: el primer componente "
                "principal, que es el tamaño, explica la mitad de la varianza",
                mostrar_pca,
            ),
            (
                "y se correlaciona 0,92 con el avalúo.",
                lambda d: self.paso(d, FadeIn(tamano[1], shift=UP * 0.2),
                                    nota="Multivariado: correlaciones, tablas cruzadas, pruebas, PCA y regresión."),
            ),
        )

        # Calidad
        problemas = cifra("31", "problemas en la\nbitácora de calidad").move_to(LEFT * 4.3 + UP * 0.4)
        principales = lista(
            "Fecha de visita de relleno: 9 010 predios",
            "Año de construcción 2000: 3 322 predios",
            "Avalúo igual a 0: 2 335 predios",
            font_size=26,
        ).next_to(problemas, RIGHT, buff=1.0)

        def mostrar_calidad(d):
            self.despejar(d * 0.3, pca, tamano)
            self.paso(d * 0.7, FadeIn(problemas, shift=UP * 0.2),
                      LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in principales],
                                  lag_ratio=0.4), tope=2.4)

        self.narrar(
            (
                "La bitácora de calidad registra 31 problemas. Los más grandes son valores de "
                "relleno: una fecha de visita repetida en 9 010 predios y el año 2000 en 3 322.",
                mostrar_calidad,
            ),
            (
                "Se marcan como faltantes, y ninguno impide el análisis.",
                lambda d: self.paso(d, Indicate(problemas[0], color=C_AMARILLO),
                                    nota="Completitud, conformidad, consistencia, precisión y relevancia."),
            ),
            quien=DANIEL,
        )

        # Facturación y pago
        cola = cifra("10 % → 81 %", "el 10 % de predios con mayor impuesto\nfactura el 81 % del total")
        cola.move_to(UP * 0.3)

        def mostrar_cola(d):
            self.despejar(d * 0.3, problemas, principales)
            self.paso(d * 0.7, FadeIn(cola, shift=UP * 0.2))

        self.narrar(
            (
                "Con la facturación, el impuesto se concentra en la cola: el 10 % de los predios "
                "con mayor impuesto factura el 81 % del total.",
                mostrar_cola,
            ),
        )

        decil = figura(IMAGENES / "pago-por-decil.png", alto=4.8).move_to(LEFT * 3.2 + UP * 0.3)
        historial = VGroup(
            cifra("80 %", "pagó en 2026 si\npagó en 2025"),
            cifra("0,3 %", "pagó en 2026 si\nno pagó en 2025"),
        ).arrange(DOWN, buff=0.7).next_to(decil, RIGHT, buff=1.0)

        def mostrar_decil(d):
            self.despejar(d * 0.3, cola)
            self.paso(d * 0.7, FadeIn(decil), FadeIn(historial, shift=UP * 0.2))

        self.narrar(
            (
                "Y el historial anticipa el pago: pagó en 2026 el 80 % de quienes pagaron en 2025, "
                "y casi nadie de quienes no.",
                mostrar_decil,
            ),
            (
                "La incertidumbre está en los predios sin registro de 2025, la curva amarilla.",
                lambda d: self.paso(d, Circumscribe(decil, color=C_AMARILLO, buff=0.05),
                                    nota="Chi-cuadrado: V de Cramér = 0,57."),
            ),
        )
        suficiencia = VGroup(
            Text("Los datos alcanzan", font_size=40, color=C_AMARILLO, weight=BOLD),
            Text("19 150 predios facturados con avalúo, destinación, zona y régimen\n"
                 "para el motor de escenarios y para el modelo de pago",
                 font_size=26, color=C_TEXTO, line_spacing=0.9),
        ).arrange(DOWN, buff=0.4)

        def mostrar_suficiencia(d):
            self.despejar(d * 0.3, decil, historial)
            self.paso(d * 0.7, FadeIn(suficiencia, shift=UP * 0.2))

        self.narrar(
            (
                "Así, los datos alcanzan: 19 150 predios facturados, con avalúo, destinación, zona "
                "y régimen, para el motor y para el modelo.",
                mostrar_suficiencia,
            ),
        )
        self.limpiar()

    def cierre(self):
        self.seccion("7. Conclusiones iniciales")
        hallazgos = lista(
            "Se factura la mitad del impuesto pleno",
            "El choque se concentra en pocos predios",
            "El historial de pago sostiene el recaudo esperado",
        ).move_to(UP * 1.1)
        siguientes = VGroup(
            Text("Entrega final", font_size=26, color=C_AMARILLO, weight=BOLD),
            Text("validar el motor · comparar tres modelos · API y aplicación web",
                 font_size=24, color=C_TEXTO),
        ).arrange(DOWN, buff=0.2).move_to(DOWN * 1.5)
        self.narrar(
            (
                "En síntesis: se factura la mitad del impuesto pleno, el choque se concentra en "
                "pocos predios y el historial de pago es una base sólida para el recaudo esperado.",
                lambda d: self.paso(d, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in hallazgos],
                                                   lag_ratio=0.5), tope=3.0),
            ),
            (
                "Para la entrega final: validar el motor con las tarifas vigentes, comparar los "
                "tres modelos y construir la API y la aplicación. Gracias.",
                lambda d: self.paso(d, FadeIn(siguientes, shift=UP * 0.2)),
            ),
            quien=DANIEL,
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
