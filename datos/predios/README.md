# Predios: la base podada en un solo archivo parquet

`predios.parquet` reúne en un solo archivo casi todo el contenido de la [base podada](../base-podada/README.md): **una fila por predio** (22 220), con lo que cuelga de cada predio en columnas anidadas. No tiene datos personales: lo que la base guarda sobre los interesados y sobre quienes atendieron la visita queda reducido a conteos por predio.

Sirve para analizar los datos sin un servidor PostgreSQL: se lee con pandas o pyarrow, que están en el entorno del proyecto.

**El archivo no va al repositorio.** Sigue identificando al municipio (códigos, número predial, círculo registral, notarías), así que se comparte con el equipo por un canal privado, como el respaldo de la base. El `.gitignore` excluye los archivos `*.parquet`. Lo que sí está en el repositorio es cómo se construye.

| Archivo | Contenido |
| --- | --- |
| `README.md` | Este documento: cómo se construye y se lee el archivo, sus columnas y qué se dejó por fuera |
| [predios.sql](predios.sql) | Consulta que arma un objeto JSON por predio. Hace las uniones, traduce los dominios, cuenta los titulares y mide las geometrías |
| [construir.py](construir.py) | Convierte la salida de la consulta en el parquet, con un esquema fijo, y comprueba que no falte ni sobre ningún campo |
| `predios.parquet` | El archivo resultante (unos 3 MB). No se versiona |

## Cómo se construye

Hace falta la base podada restaurada (ver [Cómo crear la base podada](../base-podada/README.md#cómo-crear-la-base-podada)), `psql` y el entorno de Python del proyecto. Desde la raíz del repositorio:

```bash
psql -XAtq -d catastro_pruned -f datos/predios/predios.sql \
  | uv run python datos/predios/construir.py datos/predios/predios.parquet
```

Tarda unos 15 segundos. La consulta corre en una transacción de solo lectura y los datos personales no salen de PostgreSQL: a la tubería solo llegan los conteos. `construir.py` se detiene sin escribir nada si no llegan 22 220 predios distintos, si un objeto trae campos que no están en el esquema o le falta alguno, o si un campo del esquema tiene nombre de dato personal (documento, nombre, apellido, celular, correo, domicilio, razón social o grupo étnico).

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

Las columnas de dominio vienen como texto, con el código `ilicode` del valor (por ejemplo `PH.Unidad_Predial`). Su lista de valores está en el [diccionario de datos](../base-podada/diccionario-de-datos.md#dominios).

## Columnas

Los `id_*` son los `t_id` de la base: sirven para unir filas entre sí y con la base, y no tienen significado catastral. Las áreas están en m², las alturas en metros y los valores en pesos. La descripción completa de cada atributo de origen está en el [diccionario de datos](../base-podada/diccionario-de-datos.md).

### Predio

De `lc_predio`.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `id_predio` | entero | Llave del predio (`t_id`) |
| `departamento`, `municipio` | texto | Códigos DIVIPOLA |
| `numero_predial` | texto | Número predial nacional de 30 dígitos |
| `zona`, `sector`, `comuna`, `barrio`, `manzana_vereda`, `numero_terreno`, `condicion_propiedad`, `edificio`, `piso`, `unidad` | texto | Las partes del número predial, en ese orden, después de departamento y municipio. `zona` es `00` en lo rural y `01` en lo urbano. `condicion_propiedad` corresponde a `condicion_predio` (9 para PH, 8 para condominio, 0 para NPH, 2 o 5 para informal, etc.) |
| `id_operacion`, `codigo_homologado` | texto | Identificadores del levantamiento y del sistema catastral |
| `codigo_orip`, `matricula_inmobiliaria` | texto, entero | Círculo registral y folio de matrícula |
| `avaluo_catastral` | real | Avalúo catastral |
| `tipo`, `condicion_predio`, `destinacion_economica` | texto | Dominios |
| `nombre` | texto | Nombre del predio, con los números largos ocultos (ver [Privacidad](#privacidad)) |

### Levantamiento y dirección

De `lc_datosadicionaleslevantamientocatastral`, `lc_estructuranovedadnumeropredial`, `lc_contactovisita` y `extdireccion`, todas de uno a uno con el predio salvo los contactos.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `area_registral_m2` | real | Área registral |
| `fecha_visita_predial` | fecha | Fecha de la visita |
| `resultado_visita` | texto | Dominio |
| `observaciones` | texto | Observaciones del levantamiento, con los números largos ocultos |
| `tipo_novedad_numero_predial` | texto | Novedad del número predial; nula si no hay (15 079 predios la tienen) |
| `n_contactos_visita` | entero | Cuántas personas atendieron la visita (0 a 4) |
| `autoriza_notificaciones` | booleano | Si alguna autorizó notificaciones electrónicas; nulo si no hubo contacto |
| `tipo_direccion`, `es_direccion_principal` | texto, booleano | De la dirección. Los demás campos de `extdireccion` están vacíos, y `nombre_predio` es igual a `nombre` en todas las filas |

### Propiedad horizontal, condominio e informalidad

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `ph_matriz` | estructura | Los ocho campos de `cr_datosphcondominio` (áreas totales, privadas y comunes, torres y unidades privadas). Solo en los 838 predios matriz que los tienen |
| `id_predio_matriz` | entero | Si el predio es una unidad predial, el predio matriz al que pertenece |
| `coeficiente_copropiedad` | real | Coeficiente de la unidad predial |
| `n_unidades_prediales` | entero | Si el predio es matriz, cuántas unidades prediales tiene |
| `ids_predios_informales` | lista de enteros | Predios informales relacionados con este predio formal |
| `ids_predios_formales` | lista de enteros | Predios formales relacionados con este predio informal |

### Unidades espaciales

De `cr_terreno`, `cr_construccion`, `cr_unidadconstruccion` y `cr_caracteristicasunidadconstruccion`, unidas al predio por `col_uebaunit`.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `terreno` | estructura | `id_terreno`, `area_terreno` y las medidas de la geometría. Nulo en los predios sin terreno propio (13 300; entre ellos todas las unidades prediales en PH) |
| `construcciones` | lista de estructuras | Una por construcción: `id_construccion`, `identificador`, `total_pisos`, `total_sotanos`, `total_mezanines`, `total_semisotanos`, `area_total_construccion`, `altura_total_construccion` y las medidas de la geometría |
| `unidades` | lista de estructuras | Una por unidad de construcción: `id_unidad`, `id_construccion`, `tipo_planta`, `planta_ubicacion`, `area_construida`, `altura`, las medidas de la geometría y, de sus características, `identificador`, `tipo_unidad_construccion`, `uso`, `total_plantas`, `anio_construccion`, `area_construida_caracteristicas`, `area_privada_construida` y `observaciones` (con los números largos ocultos) |

**Medidas de la geometría**, en los tres casos, calculadas con PostGIS en EPSG:9377: `area_geometrica`, `perimetro`, `compacidad` (4πA/P², 1 para un círculo y cercana a 0 para una figura alargada), `n_vertices`, `n_poligonos` y `geometria_valida` (falsa en 31 construcciones y 19 unidades, por anillos anidados o autointersecciones).

**En propiedad horizontal, la construcción de una unidad está en otro predio.** Las unidades de construcción de una unidad predial apuntan casi siempre a una construcción del predio matriz (19 655 de 19 748 casos). `id_construccion` se conserva para poder unirlas: la construcción está en la lista `construcciones` de la fila del matriz.

### Derecho, fuente y titulares

De `lc_derecho` y `lc_fuenteadministrativa` (uno a uno con el predio), y de los interesados, solo conteos.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `tipo_derecho` | texto | Dominio: dominio, posesión u ocupación |
| `fraccion_derecho` | real | De 0 a 1 |
| `fecha_inicio_tenencia` | fecha | Inicio de la tenencia |
| `tipo_fuente`, `estado_disponibilidad`, `tipo_principal` | texto | Dominios de la fuente administrativa |
| `fecha_documento_fuente` | fecha | Fecha del documento |
| `ente_emisor` | texto | Notaría, juzgado o entidad que emitió el documento |
| `numero_fuente`, `observacion_fuente` | texto | Número y observaciones del documento, con los números largos ocultos |
| `titulares` | estructura | Ver la tabla siguiente |

| Campo de `titulares` | Descripción |
| --- | --- |
| `es_agrupacion` | Si el derecho lo tiene una agrupación de interesados (6 142 predios) y no un interesado solo |
| `tipo_agrupacion` | Dominio `col_grupointeresadotipo`; nulo si no es agrupación |
| `n_titulares` | Cuántos interesados tienen el derecho: 1, o los miembros de la agrupación (2 a 88) |
| `n_persona_natural`, `n_persona_juridica` | Cuántos son de cada tipo |
| `n_femenino`, `n_masculino`, `n_sexo_sin_determinar` | Cuántos son de cada sexo |
| `participacion_max` | La mayor participación de un miembro en la agrupación; 1 si el titular es uno solo |
| `max_predios_mismo_titular` | Cuántos predios tiene, en todo el levantamiento, el titular de este predio que más tiene. Mide concentración de la propiedad sin decir quién es el titular |

## Qué se dejó por fuera

- **Datos personales.** Ninguna columna de `cr_interesado`, `col_miembros` ni `lc_contactovisita` sale de la base, salvo a través de los conteos de arriba. Tampoco el grupo étnico, ni siquiera contado: solo 6 de los 16 579 interesados tienen uno distinto de `Ninguno`, y un conteo por predio los señalaría.
- **Coordenadas.** De las geometrías solo quedan las medidas.
- **45 construcciones** que no están unidas a ningún predio en `col_uebaunit`.
- **Columnas sin información:** las técnicas de ili2db (`t_basket`, `t_ili_tid`, `t_seq`, `local_id`, `espacio_de_nombres`), `etiqueta`, las fechas de vigencia (`comienzo_vida_util_version` tiene un solo valor y `fin_vida_util_version` está vacía), `dimension` y `relacion_superficie` (un solo valor), `descripcion` del derecho (un solo valor) y los campos vacíos de la dirección.

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
- `condicion_propiedad`, sacada del número predial, coincide con `condicion_predio` en todos los predios salvo 4, que tienen 0 en el número predial: 2 informales, 1 unidad predial en PH y 1 vía. Los informales usan el 2 o el 5. `zona` solo toma los valores `00` y `01`.
