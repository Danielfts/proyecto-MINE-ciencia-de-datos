# Identidad visual

Todo lo que produce el proyecto (reportes, videos, diapositivas, gráficas, producto de datos) usa la identidad visual de la Universidad de los Andes: **amarillo, negro y blanco**, con tipografía sin serifas.

Fuentes:

- [Manual de identidad institucional (2021)](https://www.uniandes.edu.co/sites/default/files/2024-10/manual-imagen-2021.pdf)
- [Identidad institucional](https://www.uniandes.edu.co/es/la-universidad/historia-mision-y-simbolos/identidad-institucional), con los logos y las plantillas para descargar

## Colores

| Color | Valor oficial | Uso en el proyecto |
| --- | --- | --- |
| Amarillo | C0 M0 Y100 K0 · web `#FFFF00` | Acento: franjas, bloques de título, viñetas, subrayado de enlaces, quien habla en el video |
| Negro | C0 M0 Y0 K100 · web `#000000` | Texto sobre blanco o amarillo, franjas, fondo del video |
| Blanco | `#FFFFFF` | Fondo de los documentos, texto sobre negro |
| Gris | sin valor oficial | Texto secundario (pie de página, sección del video) |

- El amarillo nunca lleva texto blanco encima, ni se usa como color de texto sobre blanco: no se lee. Texto negro sobre amarillo, o amarillo sobre negro.
- En los PDF el amarillo se define en CMYK, igual que en el logo; por eso los visores lo muestran como `#FFF200` y no como `#FFFF00`. En el video se usa el valor web.
- El manual menciona una paleta secundaria que solo publica como imagen. En las gráficas, los colores adicionales para distinguir series son elección del equipo, no del manual.

## Tipografía

- El manual recomienda fuentes sin serifas (Circular, Futura, Helvetica, Roboto) y sugiere Arial para presentaciones. El enunciado del proyecto exige Arial 12 en el reporte.
- Se usa Arial en todo. Donde no está instalada (lo usual en Linux) se reemplaza por una equivalente, Liberation Sans. El PDF que se entrega debe compilarse con Arial.
- No se usan fuentes caligráficas, góticas, manuscritas ni decorativas.

## Logo

Archivos, recortados sin modificar del logosímbolo oficial que publica la Universidad (`Logosimbolo-universidaddelosandes_0.eps`):

| Archivo | Versión | Sobre qué fondo |
| --- | --- | --- |
| `logo-uniandes.pdf` | A color (escudo amarillo) | Solo blanco |
| `logo-uniandes-negro.pdf` | Negro | Fondos claros |

Reglas del manual que aplican aquí:

- El logo no se altera: no se deforma, no se inclina, no se le cambian los colores, no se le agregan ni quitan elementos ni efectos.
- La versión a color va únicamente sobre fondo blanco. Sobre fondos oscuros va la versión blanca; la amarilla, solo sobre negro total.
- Sobre una foto o una textura, el logo necesita una franja que garantice que se lea.
- El logo siempre va acompañado del texto legal: "Universidad de los Andes | Vigilada Mineducación. Reconocimiento como Universidad: Decreto 1297 del 30 de mayo de 1964. Reconocimiento personería jurídica: Resolución 28 del 23 de febrero de 1949 Minjusticia."
- No se crean logos nuevos para proyectos, grupos o iniciativas. El proyecto no tiene logo propio.
- Con logos de otras organizaciones (por ejemplo, la organización con la que se trabaja), todos van a la misma altura que el de la Universidad.

El manual está escrito para las comunicaciones institucionales y no dice nada sobre trabajos de estudiantes. Aquí el logo se usa solo en la portada del reporte, que es un trabajo académico del curso, y siguiendo esas reglas. Si los profesores prefieren que no aparezca, se quita la portada con `\portadafalse`.

## Dónde está aplicada

| Pieza | Archivo |
| --- | --- |
| Reportes | [estilo-reporte.tex](estilo-reporte.tex): portada, franja amarilla en cada página, títulos de sección, enlaces, recuadro `destacado` |
| Videos y diapositivas | [herramientas_video/escena.py](../herramientas_video/escena.py): fondo negro, texto blanco, acento amarillo, fuente sin serifas |

Al hacer una pieza nueva (gráficas de los notebooks, dashboard, aplicación), partir de estos mismos colores y de una fuente sin serifas.
