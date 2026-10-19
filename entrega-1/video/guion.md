# Guion: Primera entrega

Generado a partir de `video_entrega_1.py`. No lo edite a mano: cambie la narración en ese archivo y vuelva a generarlo desde la raíz del repositorio con

    uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py

**Duración: 5:27** de un máximo de 6:00.
Tiempos medidos con las grabaciones de los integrantes.

| Integrante | Tiempo de voz | Participación | Palabras |
| --- | --- | --- | --- |
| Daniel Felipe Triviño Santana | 2:29 | 48% | 357 |
| Nicolas Bedoya Figueroa | 1:05 | 21% | 194 |
| Joubert Daniel Álvarez | 1:34 | 31% | 180 |

> **Bloque de Daniel Felipe Triviño Santana: 1:16 de voz** (0:01 a 1:21)

## Portada

**0:01 · Daniel Felipe Triviño Santana**

Transición predial 2027: un producto de datos para fijar las tarifas del impuesto predial después de una actualización catastral.

## 1. Problemática y entendimiento del negocio

**0:11 · Daniel Felipe Triviño Santana**

Multiaservi Consultores asesora a un municipio colombiano que acaba de actualizar su catastro. Su avalúo mediano se multiplicó por 4,1 y, aunque bajó la tarifa, el impuesto facturado casi se duplicó.

Aun así, se facturó solo la mitad del impuesto pleno: una brecha de 68 mil millones de pesos. Y los límites al aumento vencen en 2027.

El objetivo: comparar escenarios de tarifas para 2027 con dos indicadores opuestos: cuánto se acerca el impuesto al pleno y cuánto sube para los predios de mayor impuesto, sin sacrificar recaudo, progresividad ni legalidad.

## 2. Ideación: el producto de datos

**0:53 · Daniel Felipe Triviño Santana**

Lo usan los consultores de Multiaservi, que hoy arman cada propuesta en hojas de cálculo antes de que pase por la alcaldía y el Concejo. Cada escenario nuevo se rehace a mano y cada tarifa debe explicarse en palabras simples.

Proponemos un motor de escenarios y un modelo que estima la probabilidad de pago de cada predio, servidos por una API y una aplicación web. Al Concejo llega un escenario congelado, no el simulador.

> **Bloque de Nicolas Bedoya Figueroa: 1:05 de voz** (1:22 a 2:31)

**1:22 · Nicolas Bedoya Figueroa**

En el prototipo se fijan tarifas y límites, se ven las alertas y los indicadores, y se lee el resultado en palabras simples.

## 3. Aspectos éticos y legales

**1:31 · Nicolas Bedoya Figueroa**

Los datos catastrales vinculan predios con personas. Por la Ley 1581, el archivo de análisis no tiene nombres ni documentos, y ninguna salida muestra un predio individual. Lo público es la decisión, no los registros: al Concejo llegan agregados explicables, con el recaudo esperado como una estimación. El motor respeta los topes legales al aumento del impuesto, y el modelo de pago solo estima el recaudo agregado: no señala a ningún contribuyente.

## 4. Enfoque analítico

**1:58 · Nicolas Bedoya Figueroa**

Primera pregunta: qué tarifas y límites acercan el impuesto al pleno sin un choque excesivo en la cola. La responde el motor de escenarios: recorre una malla de escenarios, muestra la frontera entre convergencia y choque, y se valida reproduciendo el impuesto de 2026.

Segunda: qué tan bien se anticipa si un predio pagará. Es una clasificación binaria con tres algoritmos: regresión logística, árbol de decisión y gradient boosting, evaluados con ROC-AUC, log-loss y calibración, frente a repetir el pago de 2025. Con esas probabilidades, el recaudo esperado es la suma de cada impuesto por su probabilidad de pago.

> **Bloque de Joubert Daniel Álvarez: 1:34 de voz** (2:33 a 4:09)

## 5. Recolección de datos

**2:33 · Joubert Daniel Álvarez**

Los datos vienen de dos fuentes. La principal es el levantamiento catastral en el modelo LADM-COL: lo cargamos en PostgreSQL y lo podamos de 217 a 45 tablas útiles. La segunda es la facturación del predial: de ella solo tomamos el impuesto de 2026 y si el predio pagó en 2025 y 2026. Todo se une por número predial en un archivo de 22 220 predios, sin datos personales y con su diccionario de datos.

## 6. Entendimiento de los datos

**3:19 · Joubert Daniel Álvarez**

En el notebook de entendimiento analizamos los 22 220 predios. Como los regímenes se valoran distinto, el análisis del avalúo usa 16 705 predios individuales con construcción, el 75 % del total.

El avalúo es muy asimétrico: la mediana es de 236 millones de pesos, y en escala logarítmica queda casi simétrico. Y el catastro anterior estaba desactualizado: el 64 % de los predios cambió su número predial, y el 10 % son nuevos.

En lo multivariado, el avalúo depende casi solo del tamaño: el primer componente principal, que es el tamaño, explica la mitad de la varianza y se correlaciona 0,92 con el avalúo.

> **Bloque de Daniel Felipe Triviño Santana: 1:13 de voz** (4:10 a 5:27)

**4:10 · Daniel Felipe Triviño Santana**

La bitácora de calidad registra 31 problemas. Los más grandes son valores de relleno: una fecha de visita repetida en 9 010 predios y el año 2000 en 3 322. Se marcan como faltantes, y ninguno impide el análisis.

Con la facturación, el impuesto se concentra en la cola: el 10 % de los predios con mayor impuesto factura el 81 % del total.

Y el historial anticipa el pago: pagó en 2026 el 80 % de quienes pagaron en 2025, y casi nadie de quienes no. La incertidumbre está en los predios sin registro de 2025, la curva amarilla.

Así, los datos alcanzan: 19 150 predios facturados, con avalúo, destinación, zona y régimen, para el motor y para el modelo.

## 7. Conclusiones iniciales

**5:04 · Daniel Felipe Triviño Santana**

En síntesis: se factura la mitad del impuesto pleno, el choque se concentra en pocos predios y el historial de pago es una base sólida para el recaudo esperado. Para la entrega final: validar el motor con las tarifas vigentes, comparar los tres modelos y construir la API y la aplicación. Gracias.
