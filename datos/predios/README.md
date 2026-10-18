# Predios: la base podada en un solo archivo parquet

`predios.parquet` reúne en un solo archivo casi todo el contenido de la [base podada](../base-podada/README.md): **una fila por predio** (22 220), con lo que cuelga de cada predio en columnas anidadas. No tiene datos personales: lo que la base guarda sobre los interesados y sobre quienes atendieron la visita queda reducido a conteos por predio.

Tiene además tres columnas de una segunda fuente, la [facturación del impuesto predial](#facturación-del-impuesto-predial) de 2025 y 2026: lo facturado en 2026 y si el predio pagó cada año. Todo lo demás, incluido el avalúo, sale de la base catastral.

Sirve para analizar los datos sin un servidor PostgreSQL: se lee con pandas o pyarrow, que están en el entorno del proyecto.

**El archivo no va al repositorio.** Sigue identificando al municipio (códigos, número predial, círculo registral, notarías), así que se comparte con el equipo por un canal privado, como el respaldo de la base y el Excel de facturación. El `.gitignore` excluye los archivos `*.parquet` y `*.xlsx`. Lo que sí está en el repositorio es cómo se construye.

| Archivo | Contenido |
| --- | --- |
| `README.md` | Este documento: cómo se construye y se lee el archivo, y qué se dejó por fuera |
| [diccionario/](diccionario/diccionario-de-datos.pdf) | Diccionario de datos en PDF: un diagrama de qué va anidado dentro de qué, la estructura del número predial nacional, los campos como árbol con su tipo, nulos y definición, y los valores de las categóricas. Al lado, su fuente en LaTeX |
| [predios.sql](predios.sql) | Consulta que arma un objeto JSON por predio. Hace las uniones, traduce los dominios, cuenta los titulares y mide las geometrías |
| [construir.py](construir.py) | Convierte la salida de la consulta en el parquet, con un esquema fijo, le une la facturación del predial y comprueba que no falte ni sobre ningún campo |
| `Predial-Comparativo Predial de una vigencia 2025-2026.xlsx` | Facturación del impuesto predial de 2025 y 2026, entregada por el municipio. No se versiona |
| `predios.parquet` | El archivo resultante (unos 3 MB). No se versiona |

## Cómo se construye

Hace falta la base podada restaurada (ver [Cómo crear la base podada](../base-podada/README.md#cómo-crear-la-base-podada)), el Excel de facturación en esta carpeta, `psql` y el entorno de Python del proyecto. Desde la raíz del repositorio:

```bash
psql -XAtq -d catastro_pruned -f datos/predios/predios.sql \
  | uv run python datos/predios/construir.py datos/predios/predios.parquet \
      --facturacion "datos/predios/Predial-Comparativo Predial de una vigencia 2025-2026.xlsx"
```

Tarda menos de 20 segundos. La consulta corre en una transacción de solo lectura y los datos personales no salen de PostgreSQL: a la tubería solo llegan los conteos. `construir.py` se detiene sin escribir nada si no llegan 22 220 predios distintos, si un objeto trae campos que no están en el esquema o le falta alguno, o si un campo del esquema tiene nombre de dato personal (documento, nombre, apellido, celular, correo, domicilio, razón social o grupo étnico). También si del Excel llega alguna columna distinta de las cuatro que usa, si no queda una fila de facturación por código, si la unión cambia el número de predios o si el impuesto facturado del parquet no suma lo mismo que el del Excel para los códigos unidos. Al terminar imprime cuántos códigos se unieron, cuántos se descartaron, cuántos predios quedaron sin facturación y el total facturado.

## Cómo se lee

```python
import pandas as pd

predios = pd.read_parquet("datos/predios/predios.parquet")

# Una fila por unidad de construcción, con el predio al que pertenece
unidades = predios[["id_predio", "unidades"]].explode("unidades").dropna()
unidades = pd.concat(
    [unidades[["id_predio"]].reset_index(drop=True),
     pd.json_normalize(unidades["unidades"].tolist())],
    axis=1,
)

# Las estructuras (terreno, titulares, ph_matriz) se abren igual
titulares = pd.json_normalize(predios["titulares"].tolist())
```

Las columnas de dominio vienen como texto, con el código `ilicode` del valor (por ejemplo `PH.Unidad_Predial`). Sus valores están en el [diccionario de datos](diccionario/diccionario-de-datos.pdf), sección 5.

## Columnas

Están en el [diccionario de datos](diccionario/diccionario-de-datos.pdf), que muestra el anidamiento del archivo como un diagrama y como un árbol, y explica la estructura del número predial nacional. Las definiciones salen del diccionario de datos del modelo LADM-COL del IGAC, y no se describen las columnas que identifican al municipio o pueden traer datos de personas. La descripción completa de cada atributo de origen está en el [diccionario de la base podada](../base-podada/diccionario-de-datos.md).

El PDF se compila con LuaLaTeX desde `datos/predios/diccionario/`, con `latexmk diccionario-de-datos.tex`, y usa el estilo de los reportes ([identidad/estilo-reporte.tex](../../identidad/estilo-reporte.tex)). Se mantiene a mano: si cambia `predios.sql`, hay que actualizarlo.

## Facturación del impuesto predial

El Excel de facturación compara, predio por predio, el impuesto predial unificado (IPU) de 2025 y 2026. `construir.py` lee de la hoja `Consulta` solo cuatro columnas; las filas 1 a 6 de la hoja son un encabezado que identifica al municipio y no se usan. Las columnas sin sufijo son de 2026 y las que terminan en `1`, de 2025.

| Columna | Tipo | Origen | Contenido |
| --- | --- | --- | --- |
| `ipu_facturado_2026` | `double` | `IMPPREDIAL` | Impuesto facturado para 2026, en pesos |
| `pago_2026` | `bool` | `INDPAGO` | Si el impuesto de 2026 estaba pagado en la fecha de extracción |
| `pago_2025` | `bool` | `INDPAGO1` | Si se pagó el impuesto de 2025; nulo si el predio no existía en 2025 |

**La unión.** `CODIGOCATASTRAL` es el número predial (`numero_predial`). Se parte del catastro, así que el archivo sigue teniendo 22 220 filas:

- **19 332 predios** tienen facturación. En 32 de ellos `IMPPREDIAL` viene vacío (23 informales y 9 unidades de condominio, 28 con avalúo 0): `ipu_facturado_2026` es nulo y `pago_2026` es `false`.
- **2 888 predios** no se facturan, y en ellos las tres columnas son nulas: 1 284 unidades de parque cementerio, 763 matrices de PH, 91 de condominio, 494 NPH, 141 informales, 113 unidades de PH o condominio y 2 vías.
- **48 códigos** de la facturación no están en el catastro y se descartan.
- **2 códigos** aparecen dos veces. Sus filas coinciden en 2026 y difieren en 2025: son dos predios de 2025 que en 2026 son uno. Se deja una fila por código, y `pago_2025` es `true` solo si pagaron todos los predios que se juntaron (en uno pagaron los dos; en el otro, uno solo).

**Precauciones al usarla:**

- **El avalúo del catastro es el que vale.** Hacienda liquidó el impuesto de 2026 con su propio avalúo, que difiere del de la base catastral en cerca del 6 % de los predios. Por eso de la facturación no se toma ningún atributo catastral (avalúo, destino, áreas, zona), y `ipu_facturado_2026` no siempre corresponde a `avaluo_catastral`.
- **`pago_2026` es una foto.** La vigencia 2026 no había cerrado cuando se sacó el archivo, que se generó el 25 de septiembre de 2026 según sus metadatos. Un `false` puede ser un pago que aún no se ha hecho.
- **Falta confirmar con Hacienda qué significa la marca de pago:** si dice que se pagó el impuesto de esa vigencia o que el predio no tiene deuda.

## Qué se dejó por fuera

- **Datos personales.** Ninguna columna de `cr_interesado`, `col_miembros` ni `lc_contactovisita` sale de la base, salvo a través de los conteos de `titulares` y `n_contactos_visita`. Tampoco el grupo étnico, ni siquiera contado: solo 6 de los 16 579 interesados tienen uno distinto de `Ninguno`, y un conteo por predio los señalaría.
- **Coordenadas.** De las geometrías solo quedan las medidas.
- **45 construcciones** que no están unidas a ningún predio en `col_uebaunit`.
- **Columnas sin información:** las técnicas de ili2db (`t_basket`, `t_ili_tid`, `t_seq`, `local_id`, `espacio_de_nombres`), `etiqueta`, las fechas de vigencia (`comienzo_vida_util_version` tiene un solo valor y `fin_vida_util_version` está vacía), `dimension` y `relacion_superficie` (un solo valor), `descripcion` del derecho (un solo valor), los campos vacíos de la dirección y su `nombre_predio`, igual a `nombre` en todas las filas.

## Privacidad

- **Números largos en los textos libres.** `nombre`, `observaciones`, `numero_fuente`, `observacion_fuente` y las observaciones de las unidades traían documentos de identidad de interesados o de quienes atendieron la visita: 13 textos en total. Por eso toda secuencia de 6 o más dígitos (con o sin puntos de miles) se cambia por `#`, también las que no son documentos, como matrículas o códigos. Se comprobó que ningún texto del archivo contiene ya el documento de un interesado ni el celular de un contacto.
- **Los textos libres pueden traer nombres de personas.** No hay forma confiable de detectarlos: muchos apellidos son también palabras comunes o nombres de lugares. Hay que tenerlo en cuenta antes de mostrar esos textos en un entregable.
- **Cuando el titular es uno solo, los conteos describen a esa persona.** En 16 078 predios, `titulares` dice el sexo del dueño y si es persona natural o jurídica. Junto con el número predial, eso es información de una persona identificable. Es otra razón para que el archivo no sea público.

## Qué se comprobó

Sobre el archivo construido el 14 de octubre de 2026, contra la base podada:

- 22 220 filas con `id_predio` distinto, y la suma de `avaluo_catastral` igual a la de `lc_predio`.
- 42 988 unidades de construcción, 13 483 construcciones (las 13 528 menos las 45 sin predio), 8 920 terrenos y 838 registros de PH, como en la base.
- 34 560 titulares en total: los 16 078 interesados que tienen un derecho solos más las 18 482 filas de `col_miembros`.
- 14 567 unidades prediales con su matriz, 181 relaciones de informalidad vistas desde cada lado, 8 948 contactos de visita y 15 079 novedades.
- Facturación, sobre el archivo construido el 18 de octubre de 2026: las columnas del catastro son idénticas a las del 14 de octubre; la suma de `ipu_facturado_2026` es igual a la de `IMPPREDIAL` en el Excel para los códigos unidos; hay 12 266 predios con `pago_2026` en `true` y 7 066 en `false`, y 12 540 con `pago_2025` en `true`, 2 813 en `false` y 3 979 facturados sin vigencia 2025.
- `condicion_propiedad`, sacada del número predial, coincide con `condicion_predio` en todos los predios salvo 4, que tienen 0 en el número predial: 2 informales, 1 unidad predial en PH y 1 vía. Los informales usan el 2 o el 5. `zona` solo toma los valores `00` y `01`.
