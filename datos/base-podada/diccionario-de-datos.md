# Diccionario de datos de la base podada

Describe las 45 tablas de la base catastral podada: las 20 que tienen los datos del levantamiento, los 23 dominios (listas de valores) que esas tablas usan y las 2 tablas que registran la carga. Qué es la base podada, cómo se obtiene y cómo se relacionan sus tablas está en el [README](README.md) de esta carpeta; de dónde sale el modelo, en el [README de `datos/`](../README.md).

## Cómo leerlo

Cada tabla trae su tipo según el modelo (clase, estructura o asociación), el elemento del modelo del que sale, su número de filas y una tabla con sus columnas:

| Campo | Qué indica |
| --- | --- |
| Tipo | Tipo de dato en PostgreSQL. Las geometrías están en EPSG:9377 y usan tipos con curvas (ver el [README de `datos/`](../README.md#cómo-se-traduce-el-modelo-a-tablas)) |
| Oblig. | Si la columna es obligatoria (`NOT NULL`) |
| Con dato | Porcentaje de filas en que la columna no es nula. Se midió sobre la base original el 13 de octubre de 2026; la poda no cambia ninguna fila. No nulo no quiere decir útil: un texto vacío cuenta como dato |
| Descripción | Empieza con **→ `tabla`** cuando la columna es una llave foránea: guarda el `t_id` de una fila de esa tabla. Las unidades van entre paréntesis |

**De dónde salen las descripciones.** De los comentarios del modelo INTERLIS, que ili2pg guardó como comentarios de las tablas y columnas de la base. Se resumieron cuando eran muy largas. Las que llevan la marca † se redactaron para este diccionario, porque el modelo no trae descripción o la que trae no describe la columna. Para la definición oficial de cada atributo está el diccionario de datos del IGAC, en [`../modelos-ladm-col/documentacion/`](../modelos-ladm-col/documentacion/).

**Columnas comunes.** Se repiten en muchas tablas con el mismo significado, así que se describen una sola vez aquí. En cada tabla se indica cuáles tiene.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `t_id` | bigint | Sí | 100 % | Llave primaria. Es un número propio de la base, sin significado catastral. Todas las llaves foráneas apuntan a esta columna |
| `t_basket` | bigint | Sí | 100 % | **→ `t_ili2db_basket`.** Carga a la que pertenece la fila. La base tiene una sola carga, así que vale lo mismo en todas las filas |
| `t_ili_tid` | uuid | No | 100 % | Identificador del objeto en el archivo de transferencia de origen |
| `t_seq` | bigint | No | 100 % | Orden de la fila entre las que comparten dueño (solo en estructuras) |
| `comienzo_vida_util_version` | timestamp | Sí | 100 % | Comienzo de la validez actual de la instancia de un objeto |
| `fin_vida_util_version` | timestamp | No | 0 % | Finalización de la validez actual de la instancia de un objeto |
| `espacio_de_nombres` | varchar(255) | Sí | 100 % | Identificador único global. Corresponde al atributo *namespace* de la clase en LADM |
| `local_id` | varchar(255) | Sí | 100 % | Identificador único local |

`fin_vida_util_version` está vacía en todas las tablas: la carga solo tiene la versión vigente de cada objeto.

## Tablas de datos

| Tabla | Tipo | Filas | Qué contiene |
| --- | --- | ---: | --- |
| [`lc_predio`](#lc_predio) | Clase | 22 220 | El predio es la unidad territorial legal propia de catastro |
| [`lc_datosadicionaleslevantamientocatastral`](#lc_datosadicionaleslevantamientocatastral) | Clase | 22 220 | Datos adicionales del predio para catastro multipropósito |
| [`lc_contactovisita`](#lc_contactovisita) | Clase | 8 948 | Datos de la persona que atendió la visita de levantamiento |
| [`lc_estructuranovedadnumeropredial`](#lc_estructuranovedadnumeropredial) | Estructura | 15 079 | Permite identificar las modificaciones que puede tener el número predial producto de la dinámica inmobiliaria identificada en el levantamiento catastral |
| [`cr_datosphcondominio`](#cr_datosphcondominio) | Clase | 838 | Datos principales del predio matriz sometido al régimen de propiedad horizontal (PH) o condominio |
| [`cr_predio_copropiedad`](#cr_predio_copropiedad) | Asociación | 14 567 | Relación entre unidades prediales y predios matrices bajo el régimen de propiedad horizontal y condominio |
| [`lc_predio_informalidad`](#lc_predio_informalidad) | Asociación | 181 | Relaciona un predio formal con un predio informal |
| [`extdireccion`](#extdireccion) | Estructura | 22 220 | Referencia a una clase externa para gestionar direcciones |
| [`col_uebaunit`](#col_uebaunit) | Asociación | 65 391 | Une cada predio con sus unidades espaciales: su terreno, sus construcciones y sus unidades de construcción |
| [`cr_terreno`](#cr_terreno) | Clase | 8 920 | Porción de tierra con una extensión geográfica definida |
| [`cr_construccion`](#cr_construccion) | Clase | 13 528 | Es la unión de materiales adheridos al terreno, con carácter de permanente, cualesquiera sean los elementos que la constituyan |
| [`cr_unidadconstruccion`](#cr_unidadconstruccion) | Clase | 42 988 | Es cada conjunto de materiales consolidados dentro de un predio que tiene unas características específicas en cuanto a elementos constitutivos físicos y usos |
| [`cr_caracteristicasunidadconstruccion`](#cr_caracteristicasunidadconstruccion) | Clase | 42 988 | Permite agrupar las unidades de construcción por identificador, uso y tipología |
| [`cr_interesado`](#cr_interesado) | Clase | 16 579 | Es la parte que tiene una relación con el predio por algún tipo de derecho, restricción, publicidad o responsabilidad |
| [`cr_agrupacioninteresados`](#cr_agrupacioninteresados) | Clase | 6 142 | Grupo de interesados que comparten un derecho sobre un predio |
| [`col_miembros`](#col_miembros) | Asociación | 18 482 | Relaciona a los interesados de una agrupación de interesados a través de la proporción de su participación en el grupo |
| [`lc_derecho`](#lc_derecho) | Clase | 22 220 | Registra los derechos que un interesado ejerce sobre un predio |
| [`lc_fuenteadministrativa`](#lc_fuenteadministrativa) | Clase | 22 220 | Almacena las fuentes administrativas (escrituras, sentencias, actos administrativos y otras) que sustentan el derecho respecto de la relación de tenencia entre el interesado y el predio |
| [`col_rrrfuente`](#col_rrrfuente) | Asociación | 22 220 | Une cada derecho con la fuente administrativa que lo sustenta |
| [`col_unidadfuente`](#col_unidadfuente) | Asociación | 22 220 | Une cada predio con su fuente administrativa |

### Predio

El predio y lo que se registra directamente sobre él.

#### `lc_predio`

Clase `LC_Predio` · 22 220 filas · 19 columnas

El predio es la unidad territorial legal propia de catastro. Está formado por el terreno y puede o no tener construcciones asociadas.

- Es la tabla central: casi todas las demás llegan a ella, directamente o a través de una asociación.
- `departamento`, `municipio` y los primeros dígitos de `numero_predial` identifican el municipio de los datos (ver la advertencia del [README](README.md#antes-de-compartirla)).

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `departamento` | varchar(2) | Sí | 100 % | Código del departamento al que pertenece el predio. Lo asigna DIVIPOLA y tiene 2 dígitos |
| `municipio` | varchar(3) | Sí | 100 % | Código del municipio al que pertenece el predio. Lo asigna DIVIPOLA y tiene 3 dígitos |
| `id_operacion` | varchar(30) | Sí | 100 % | Identificador único temporal de cada predio, asignado durante el levantamiento catastral |
| `codigo_orip` | varchar(4) | No | 100 % | Círculo registral |
| `matricula_inmobiliaria` | integer | No | 96,7 % | Matrícula inmobiliaria |
| `numero_predial` | varchar(30) | Sí | 100 % | Código numérico de 30 dígitos que se asigna a cada predio y busca localizarlo inequívocamente en los documentos catastrales, según el modelo del IGAC |
| `codigo_homologado` | varchar(11) | No | 100 % | Código único para identificar los inmuebles en los sistemas de información catastral |
| `avaluo_catastral` | numeric(16,1) | No | 100 % | (COP) Valor del predio, obtenido mediante investigación y análisis estadístico del mercado inmobiliario. Es la suma de los avalúos parciales del terreno y de las unidades de construcción, corresponde a un porcentaje del avalúo comercial y se redondea a miles |
| `tipo` | bigint | Sí | 100 % | **→ `col_unidadadministrativabasicatipo`.** Tipo de predio para efectos catastrales |
| `condicion_predio` | bigint | Sí | 100 % | **→ `lc_condicionprediotipo`.** Caracterización temática de las condiciones del predio, relacionada con aspectos físicos y jurídicos |
| `destinacion_economica` | bigint | Sí | 100 % | **→ `lc_destinacioneconomicatipo`.** Clasificación para fines estadísticos y económicos que se da a cada inmueble en su conjunto (terreno, construcciones o edificaciones) según la actividad predominante que en él se desarrolla |
| `nombre` | varchar(255) | No | 100 % | Nombre de la unidad administrativa básica, en muchos casos toponímico, especialmente en terrenos rústicos |

#### `lc_datosadicionaleslevantamientocatastral`

Clase `LC_DatosAdicionalesLevantamientoCatastral` · 22 220 filas · 8 columnas

Datos adicionales del predio para catastro multipropósito.

- Hay exactamente una fila por predio.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `area_registral_m2` | numeric(25,2) | No | 100 % | (m²) Área consignada en el certificado de tradición y libertad, en la descripción de cabida y linderos o en los títulos registrados |
| `observaciones` | varchar(500) | No | 100 % | Observaciones generales respecto del predio |
| `fecha_visita_predial` | date | No | 100 % | Fecha de la visita en campo al predio |
| `resultado_visita` | bigint | Sí | 100 % | **→ `lc_resultadovisitatipo`.** Situaciones que se presentan y afectan el resultado del levantamiento de la información en campo |
| `lc_predio` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio al que corresponden los datos † |

#### `lc_contactovisita`

Clase `LC_ContactoVisita` · 8 948 filas · 11 columnas

Datos de la persona que atendió la visita de levantamiento. †

- **Contiene datos personales:** nombre, documento, domicilio, celular y correo.
- Las 8 948 filas corresponden a 8 914 registros de datos adicionales: unos pocos tienen más de un contacto.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `nombres_apellidos_quien_atendio` | varchar(150) | Sí | 100 % | Nombres y apellidos de la persona que atendió la visita de actividades catastrales sobre el predio |
| `tipo_documento_quien_atendio` | bigint | No | 100 % | **→ `cr_documentotipo`.** Tipo de documento de la persona que atendió la visita predial |
| `numero_documento_quien_atendio` | varchar(50) | No | 99,6 % | Número de documento de la persona que atendió la visita predial |
| `domicilio_notificaciones` | varchar(255) | No | 84,8 % | Dirección de domicilio para notificaciones |
| `celular` | varchar(20) | No | 100 % | Número de celular de la persona que atendió la visita |
| `correo_electronico` | varchar(100) | No | 100 % | Correo electrónico de la persona que atendió la visita |
| `autoriza_notificaciones` | boolean | No | 100 % | Indica si autoriza las notificaciones administrativas por vía electrónica |
| `lc_datos_adicionales` | bigint | Sí | 100 % | **→ `lc_datosadicionaleslevantamientocatastral`.** Registro de datos adicionales (y, por él, el predio) al que pertenece el contacto † |

#### `lc_estructuranovedadnumeropredial`

Estructura `LC_EstructuraNovedadNumeroPredial` · 15 079 filas · 7 columnas

Permite identificar las modificaciones que puede tener el número predial producto de la dinámica inmobiliaria identificada en el levantamiento catastral.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `t_seq`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `numero_predial` | varchar(30) | Sí | 100 % | Número predial nacional de 30 dígitos al que se refiere la novedad † |
| `tipo_novedad` | bigint | Sí | 100 % | **→ `lc_estructuranovedadnumeropredial_tipo_novedad`.** Tipo de modificación del número predial producto de la dinámica inmobiliaria identificada en el levantamiento |
| `lc_dtsdcnlstmntctstral_novedad_numeros_prediales` | bigint | No | 100 % | **→ `lc_datosadicionaleslevantamientocatastral`.** Registro de datos adicionales al que pertenece la novedad. Relaciona los cambios del predio respecto de la información catastral vigente |

#### `cr_datosphcondominio`

Clase `CR_DatosPHCondominio` · 838 filas · 12 columnas

Datos principales del predio matriz sometido al régimen de propiedad horizontal (PH) o condominio.

- Hay una fila por cada predio matriz que tiene estos datos (838 predios distintos).

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `area_total_terreno` | numeric(16,2) | No | 100 % | (m²) Área total del terreno del PH o condominio matriz |
| `area_total_terreno_privada` | numeric(16,2) | No | 100 % | (m²) Área total privada del terreno del PH o condominio matriz |
| `area_total_terreno_comun` | numeric(16,2) | No | 100 % | (m²) Área total de terreno común del PH o condominio matriz |
| `area_total_construida` | numeric(16,2) | No | 100 % | (m²) Área total construida del PH o condominio matriz |
| `area_total_construida_privada` | numeric(16,2) | No | 100 % | (m²) Área total construida privada del PH o condominio matriz |
| `area_total_construida_comun` | numeric(16,2) | No | 100 % | (m²) Área total construida común del PH o condominio matriz |
| `numero_torres` | integer | No | 100 % | Número de torres en el PH o condominio |
| `total_unidades_privadas` | integer | No | 100 % | Total de unidades privadas en el PH o condominio |
| `lc_predio` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio matriz al que corresponden los datos † |

#### `cr_predio_copropiedad`

Asociación `cr_predio_copropiedad` · 14 567 filas · 5 columnas

Relación entre unidades prediales y predios matrices bajo el régimen de propiedad horizontal y condominio.

- `unidad_predial` tiene un índice único: cada unidad predial pertenece a un solo predio matriz.

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `unidad_predial` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio que es la unidad predial † |
| `matriz` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio matriz al que pertenece la unidad predial † |
| `coeficiente` | numeric(11,10) | No | 100 % | Coeficiente de copropiedad de la unidad predial |

#### `lc_predio_informalidad`

Asociación `lc_predio_informalidad` · 181 filas · 4 columnas

Relaciona un predio formal con un predio informal. †

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `lc_predio_formal` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio formal † |
| `lc_predio_informal` | bigint | Sí | 100 % | **→ `lc_predio`.** Predio informal † |

#### `extdireccion`

Estructura `ExtDireccion` del núcleo LADM-COL · 22 220 filas · 21 columnas

Referencia a una clase externa para gestionar direcciones.

- Hay exactamente una fila por predio. En esta carga solo traen dato el tipo de dirección, si es la principal y `nombre_predio`: los campos de la dirección estructurada y la localización están vacíos.
- Las tres columnas `*_ext_direccion_id` permitirían asociar una dirección a un terreno, una construcción o una unidad de construcción, pero no se usan.

Columnas comunes: `t_id`, `t_basket`, `t_seq`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo_direccion` | bigint | Sí | 100 % | **→ `extdireccion_tipo_direccion`.** Estructurada o no estructurada |
| `es_direccion_principal` | boolean | No | 100 % | Indica si la dirección es la principal |
| `localizacion` | geometry(PointZ, 9377) | No | 0 % | Par de valores georreferenciados (x, y) en el que se encuentra la dirección |
| `codigo_postal` | varchar(255) | No | 0 % | Código postal |
| `clase_via_principal` | bigint | No | 0 % | **→ `extdireccion_clase_via_principal`.** Clase de la vía principal (calle, carrera, avenida y otras) |
| `valor_via_principal` | varchar(100) | No | 0 % | Número que acompaña a la clase de vía principal |
| `letra_via_principal` | varchar(20) | No | 0 % | Letra que acompaña al valor de la vía principal |
| `letra_via_generadora` | varchar(20) | No | 0 % | Letra que acompaña al valor de la vía generadora |
| `sector_ciudad` | bigint | No | 0 % | **→ `extdireccion_sector_ciudad`.** Norte, sur, este u oeste |
| `valor_via_generadora` | varchar(100) | No | 0 % | Número de la vía generadora |
| `numero_predio` | varchar(20) | No | 0 % | Distancia entre la vía generadora y el acceso del predio |
| `sector_predio` | bigint | No | 0 % | **→ `extdireccion_sector_predio`.** Sector donde se localiza el predio: norte, sur, este u oeste |
| `complemento` | varchar(255) | No | 0 % | Complemento de la dirección |
| `nombre_predio` | varchar(255) | No | 100 % | Nombre del predio (por ejemplo, el de los predios del sector rural). Se diligencia cuando el tipo de dirección es `No_Estructurada` |
| `cr_construccion_ext_direccion_id` | bigint | No | 0 % | **→ `cr_construccion`.** Construcción a la que pertenece la dirección † |
| `cr_terreno_ext_direccion_id` | bigint | No | 0 % | **→ `cr_terreno`.** Terreno al que pertenece la dirección † |
| `cr_unidadconstruccion_ext_direccion_id` | bigint | No | 0 % | **→ `cr_unidadconstruccion`.** Unidad de construcción a la que pertenece la dirección † |
| `lc_predio_direccion` | bigint | No | 100 % | **→ `lc_predio`.** Predio al que pertenece la dirección |

### Unidades espaciales

La parte física y geográfica: terrenos, construcciones y unidades de construcción, y la tabla que los une con el predio.

#### `col_uebaunit`

Asociación `col_ueBaunit` del núcleo LADM-COL · 65 391 filas · 6 columnas

Une cada predio con sus unidades espaciales: su terreno, sus construcciones y sus unidades de construcción. †

- Cada fila une un predio con una sola unidad espacial: tiene llena `baunit_lc_predio` y exactamente una de las tres columnas `ue_*` (comprobado en las 65 391 filas).
- Aparecen en esta tabla 19 913 de los 22 220 predios.

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `ue_cr_unidadconstruccion` | bigint | No | 65,7 % | **→ `cr_unidadconstruccion`.** Unidad de construcción del predio † |
| `ue_cr_terreno` | bigint | No | 13,6 % | **→ `cr_terreno`.** Terreno del predio † |
| `ue_cr_construccion` | bigint | No | 20,6 % | **→ `cr_construccion`.** Construcción del predio † |
| `baunit_lc_predio` | bigint | No | 100 % | **→ `lc_predio`.** Predio † |

#### `cr_terreno`

Clase `CR_Terreno` · 8 920 filas · 12 columnas

Porción de tierra con una extensión geográfica definida.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `area_terreno` | numeric(15,1) | Sí | 100 % | (m²) Área total del terreno resultante del levantamiento catastral |
| `geometria` | geometry(MultiSurfaceZ, 9377) | Sí | 100 % | Figura geométrica vectorial poligonal, generada a partir de los linderos del predio |
| `dimension` | bigint | No | 100 % | **→ `col_dimensiontipo`.** Dimensión del objeto |
| `etiqueta` | varchar(255) | No | 100 % | Corresponde al atributo *label* de la clase en LADM |
| `relacion_superficie` | bigint | No | 100 % | **→ `col_relacionsuperficietipo`.** Corresponde al atributo *surfaceRelation* de la clase en LADM |

#### `cr_construccion`

Clase `CR_Construccion` · 13 528 filas · 18 columnas

Es la unión de materiales adheridos al terreno, con carácter de permanente, cualesquiera sean los elementos que la constituyan.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `identificador` | varchar(20) | Sí | 100 % | Identificador de la construcción; puede codificarse con letras del abecedario |
| `total_pisos` | integer | Sí | 100 % | Número total de pisos de la construcción |
| `total_sotanos` | integer | No | 100 % | Número total de sótanos de la construcción |
| `total_mezanines` | integer | No | 100 % | Número total de mezanines de la construcción |
| `total_semisotanos` | integer | No | 100 % | Número total de semisótanos de la construcción |
| `area_total_construccion` | numeric(15,1) | Sí | 100 % | (m²) Área total construida |
| `altura_total_construccion` | numeric(6,2) | No | 100 % | (m) Altura total de la construcción |
| `geometria` | geometry(MultiSurfaceZ, 9377) | Sí | 100 % | Puntos, líneas, polígono y volumen que definen la construcción; la asigna el sistema de captura |
| `dimension` | bigint | No | 100 % | **→ `col_dimensiontipo`.** Dimensión del objeto |
| `etiqueta` | varchar(255) | No | 100 % | Corresponde al atributo *label* de la clase en LADM |
| `relacion_superficie` | bigint | No | 100 % | **→ `col_relacionsuperficietipo`.** Corresponde al atributo *surfaceRelation* de la clase en LADM |

#### `cr_unidadconstruccion`

Clase `CR_UnidadConstruccion` · 42 988 filas · 17 columnas

Es cada conjunto de materiales consolidados dentro de un predio que tiene unas características específicas en cuanto a elementos constitutivos físicos y usos.

- Cada unidad tiene su propio registro de características: la relación con `cr_caracteristicasunidadconstruccion` es de uno a uno en esta carga.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo_planta` | bigint | Sí | 100 % | **→ `cr_construccionplantatipo`.** Tipo de planta donde se ubica la unidad de construcción |
| `planta_ubicacion` | integer | Sí | 100 % | Indica numéricamente la ubicación de la planta |
| `area_construida` | numeric(15,1) | Sí | 100 % | (m²) Área total construida en la unidad de construcción |
| `altura` | integer | No | 100 % | (m) Altura total de la planta |
| `geometria` | geometry(MultiSurfaceZ, 9377) | No | 100 % | Puntos, líneas, polígono y volumen que definen la unidad de construcción; la asigna el sistema de captura |
| `cr_caracteristicasunidadconstruccion` | bigint | Sí | 100 % | **→ `cr_caracteristicasunidadconstruccion`.** Características de la unidad † |
| `cr_construccion` | bigint | No | 100 % | **→ `cr_construccion`.** Construcción a la que pertenece la unidad † |
| `dimension` | bigint | No | 100 % | **→ `col_dimensiontipo`.** Dimensión del objeto |
| `etiqueta` | varchar(255) | No | 100 % | Corresponde al atributo *label* de la clase en LADM |
| `relacion_superficie` | bigint | No | 100 % | **→ `col_relacionsuperficietipo`.** Corresponde al atributo *surfaceRelation* de la clase en LADM |

#### `cr_caracteristicasunidadconstruccion`

Clase `CR_CaracteristicasUnidadConstruccion` · 42 988 filas · 15 columnas

Permite agrupar las unidades de construcción por identificador, uso y tipología.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `identificador` | varchar(20) | Sí | 100 % | Identificador de la unidad de construcción; puede codificarse con letras del abecedario |
| `tipo_unidad_construccion` | bigint | Sí | 100 % | **→ `cr_unidadconstrucciontipo`.** Tipo de unidad según sus elementos constructivos: convencional cuando es de uso residencial, comercial o industrial, y no convencional cuando es un anexo de la construcción |
| `total_plantas` | integer | No | 100 % | Número total de plantas en la unidad de construcción |
| `uso` | bigint | Sí | 100 % | **→ `cr_usouconstipo`.** Destinación de la unidad constructiva con respecto a la actividad económica desarrollada en la edificación del predio |
| `anio_construccion` | integer | No | 100 % | Año de construcción de la unidad de construcción |
| `area_construida` | numeric(15,1) | Sí | 100 % | (m²) Área total construida en la unidad de construcción |
| `area_privada_construida` | numeric(15,1) | No | 57,8 % | (m²) Área total privada de la unidad de construcción, para los predios en régimen de propiedad horizontal |
| `observaciones` | text | No | 100 % | Observaciones generales respecto de la unidad de construcción |

### Interesados y derechos

Quién tiene qué derecho sobre cada predio.

#### `cr_interesado`

Clase `CR_Interesado` · 16 579 filas · 18 columnas

Es la parte que tiene una relación con el predio por algún tipo de derecho, restricción, publicidad o responsabilidad.

- **Contiene datos personales:** documento de identidad, nombres, apellidos, sexo y grupo étnico.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo` | bigint | Sí | 100 % | **→ `cr_interesadotipo`.** Persona natural o persona jurídica |
| `tipo_documento` | bigint | Sí | 100 % | **→ `cr_documentotipo`.** Clase de documento público que permite la identificación del interesado |
| `documento_identidad` | varchar(50) | Sí | 100 % | Número del documento de identificación del interesado |
| `primer_nombre` | varchar(100) | No | 99,5 % | Primer nombre de la persona interesada |
| `segundo_nombre` | varchar(100) | No | 99,4 % | Segundo nombre de la persona interesada |
| `primer_apellido` | varchar(100) | No | 99,5 % | Primer apellido de la persona interesada |
| `segundo_apellido` | varchar(100) | No | 100 % | Segundo apellido de la persona interesada |
| `sexo` | bigint | No | 100 % | **→ `cr_sexotipo`.** Masculino o femenino, según aparezca en el documento de identidad |
| `grupo_etnico` | bigint | No | 100 % | **→ `cr_grupoetnicotipo`.** Grupo étnico al que pertenece el interesado |
| `razon_social` | varchar(255) | No | 99,9 % | Nombre jurídico con el que está inscrita una sociedad o empresa constituida legalmente |
| `nombre` | varchar(255) | No | 100 % | Nombre del interesado |

#### `cr_agrupacioninteresados`

Clase `CR_AgrupacionInteresados` · 6 142 filas · 9 columnas

Grupo de interesados que comparten un derecho sobre un predio. Hereda sus atributos de la clase `COL_AgrupacionInteresados` del núcleo. †

- Todas las agrupaciones tienen miembros en `col_miembros`.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo` | bigint | Sí | 100 % | **→ `col_grupointeresadotipo`.** Tipo de agrupación |
| `nombre` | varchar(255) | No | 0 % | Nombre del interesado |

#### `col_miembros`

Asociación `col_miembros` del núcleo LADM-COL · 18 482 filas · 6 columnas

Relaciona a los interesados de una agrupación de interesados a través de la proporción de su participación en el grupo.

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `interesado_cr_interesado` | bigint | No | 100 % | **→ `cr_interesado`.** Interesado que es miembro de la agrupación † |
| `interesado_cr_agrupacioninteresados` | bigint | No | 0 % | **→ `cr_agrupacioninteresados`.** Agrupación que es miembro de otra agrupación; no se usa en esta carga † |
| `agrupacion_cr_agrupacioninteresados` | bigint | No | 100 % | **→ `cr_agrupacioninteresados`.** Agrupación a la que pertenece el miembro † |
| `participacion` | numeric(11,10) | No | 100 % | Proporción de la participación del interesado en la agrupación de la que hace parte |

#### `lc_derecho`

Clase `LC_Derecho` · 22 220 filas · 14 columnas

Registra los derechos que un interesado ejerce sobre un predio.

- Hay exactamente un derecho por predio.
- El titular es un interesado o una agrupación, nunca los dos: cada fila tiene llena exactamente una de las dos columnas `interesado_*` (comprobado en las 22 220 filas).

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `comienzo_vida_util_version`, `fin_vida_util_version`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo` | bigint | Sí | 100 % | **→ `lc_derechotipo`.** Forma de relación del interesado con el predio según su forma de tenencia: posesión, ocupación o dominio |
| `fraccion_derecho` | numeric(11,10) | Sí | 100 % | Fracción del derecho en relación con la forma de tenencia y el área que ocupa dentro del predio, en tanto por uno (de 0 a 1) |
| `fecha_inicio_tenencia` | date | No | 100 % | Fecha de inicio de la tenencia del interesado con respecto al predio |
| `descripcion` | varchar(255) | No | 100 % | Descripción asociada al derecho, la responsabilidad o la restricción |
| `interesado_cr_interesado` | bigint | No | 72,4 % | **→ `cr_interesado`.** Titular del derecho, cuando es un solo interesado † |
| `interesado_cr_agrupacioninteresados` | bigint | No | 27,6 % | **→ `cr_agrupacioninteresados`.** Titular del derecho, cuando es una agrupación † |
| `unidad_lc_predio` | bigint | No | 100 % | **→ `lc_predio`.** Predio sobre el que recae el derecho † |

### Fuentes administrativas

Los documentos que sustentan los derechos.

#### `lc_fuenteadministrativa`

Clase `LC_FuenteAdministrativa` · 22 220 filas · 12 columnas

Almacena las fuentes administrativas (escrituras, sentencias, actos administrativos y otras) que sustentan el derecho respecto de la relación de tenencia entre el interesado y el predio.

Columnas comunes: `t_id`, `t_basket`, `t_ili_tid`, `espacio_de_nombres`, `local_id`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `tipo` | bigint | Sí | 100 % | **→ `col_fuenteadministrativatipo`.** Tipo de documento (escritura pública, sentencia judicial, acto administrativo, documento privado o sin documento) que acredita la relación entre el interesado y el predio |
| `ente_emisor` | varchar(255) | No | 100 % | Entidad que emite el título de dominio, posesión u ocupación |
| `observacion` | varchar(255) | No | 81,6 % | Observaciones o descripción del documento de la fuente administrativa |
| `numero_fuente` | varchar(150) | No | 100 % | Identificador del documento: por ejemplo, el número de la resolución, de la escritura pública o del radicado de una sentencia |
| `estado_disponibilidad` | bigint | Sí | 100 % | **→ `col_estadodisponibilidadtipo`.** Indica si la fuente está disponible y en qué condiciones |
| `tipo_principal` | bigint | No | 98,1 % | **→ `ci_forma_presentacion_codigo`.** Formato en el que se presenta la fuente |
| `fecha_documento_fuente` | date | No | 100 % | Fecha de expedición del documento de la fuente |

#### `col_rrrfuente`

Asociación `col_rrrFuente` del núcleo LADM-COL · 22 220 filas · 4 columnas

Une cada derecho con la fuente administrativa que lo sustenta. †

- En esta carga la relación es de uno a uno: 22 220 derechos distintos y 22 220 fuentes distintas.

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `fuente_administrativa_lc_fuenteadministrativa` | bigint | No | 100 % | **→ `lc_fuenteadministrativa`.** Fuente administrativa † |
| `rrr_lc_derecho` | bigint | No | 100 % | **→ `lc_derecho`.** Derecho que la fuente sustenta † |

#### `col_unidadfuente`

Asociación `col_unidadFuente` del núcleo LADM-COL · 22 220 filas · 4 columnas

Une cada predio con su fuente administrativa. †

- Hay exactamente una fila por predio.

Columnas comunes: `t_id`, `t_basket`.

| Columna | Tipo | Oblig. | Con dato | Descripción |
| --- | --- | --- | --- | --- |
| `fuente_administrativa_lc_fuenteadministrativa` | bigint | No | 100 % | **→ `lc_fuenteadministrativa`.** Fuente administrativa † |
| `unidad_lc_predio` | bigint | No | 100 % | **→ `lc_predio`.** Predio † |

## Dominios

Un dominio es la lista de valores permitidos de un atributo. Las columnas que lo usan guardan el `t_id` del valor, no su texto, así que para leerlo hay que unir con la tabla del dominio:

```sql
SELECT c.ilicode AS condicion, count(*) AS predios
FROM xtf.lc_predio p
JOIN xtf.lc_condicionprediotipo c ON c.t_id = p.condicion_predio
GROUP BY c.ilicode;
```

Las 23 tablas de dominio tienen las mismas columnas:

| Columna | Tipo | Oblig. | Descripción |
| --- | --- | --- | --- |
| `t_id` | bigint | Sí | Llave primaria; es el valor que guardan las columnas que usan el dominio |
| `thisclass` | varchar(1024) | Sí | Dominio del modelo al que pertenece el valor |
| `baseclass` | varchar(1024) | No | Dominio del que hereda `thisclass`, si hereda de alguno |
| `itfcode` | integer | Sí | Número del valor dentro del dominio |
| `ilicode` | varchar(1024) | Sí | Código del valor en el modelo. Es el identificador estable: conviene usarlo en las consultas y en el análisis. Un punto separa los niveles de una jerarquía (`PH.Matriz`) |
| `seq` | integer | No | Orden del valor, cuando el dominio es ordenado |
| `inactive` | boolean | Sí | Si el valor está inactivo. Ninguno lo está |
| `dispname` | varchar(250) | Sí | Nombre para mostrar |
| `description` | text | No | Definición del valor según el modelo |

Este diccionario lista los códigos, no sus definiciones: la definición de cada valor está en la columna `description` de la propia tabla (salvo en los cuatro dominios de `extdireccion`, en `col_dimensiontipo` y en `lc_estructuranovedadnumeropredial_tipo_novedad`, donde el modelo no la trae) y en el diccionario del IGAC.

| Dominio | Valores | Lo usa | Códigos (`ilicode`) |
| --- | ---: | --- | --- |
| `ci_forma_presentacion_codigo` | 5 | `lc_fuenteadministrativa.tipo_principal` | `Documento`, `Imagen`, `Mapa`, `Otro`, `Video` |
| `col_dimensiontipo` | 3 | `dimension` de `cr_terreno`, `cr_construccion` y `cr_unidadconstruccion` | `Dim2D`, `Dim3D`, `Otro` |
| `col_estadodisponibilidadtipo` | 3 | `lc_fuenteadministrativa.estado_disponibilidad` | `Convertido`, `Desconocido`, `Disponible` |
| `col_fuenteadministrativatipo` | 5 | `lc_fuenteadministrativa.tipo` | `Documento_Privado`, `Documento_Publico.Acto_Administrativo`, `Documento_Publico.Escritura_Publica`, `Documento_Publico.Sentencia_Judicial`, `Sin_Documento`. La tabla tiene 12 filas: estos 5 valores, que son los del levantamiento catastral (`LC_FuenteAdministrativaTipo`), más 2 del núcleo y 5 del modelo RIC que la carga no usa |
| `col_grupointeresadotipo` | 4 | `cr_agrupacioninteresados.tipo` | `Grupo_Civil`, `Grupo_Empresarial`, `Grupo_Etnico`, `Grupo_Mixto` |
| `col_relacionsuperficietipo` | 4 | `relacion_superficie` de `cr_terreno`, `cr_construccion` y `cr_unidadconstruccion` | `En_Rasante`, `En_Subsuelo`, `En_Vuelo`, `Otro` |
| `col_unidadadministrativabasicatipo` | 13 | `lc_predio.tipo` | `Amenazas_Riesgos`, `Ordenamiento_Territorial`, `Parques_Naturales`, `Predio.Privado`, `Predio.Publico.Baldio`, `Predio.Publico.Fiscal_Patrimonial`, `Predio.Publico.Publico`, `Predio.Publico.Uso_Publico`, `Reservas_Naturales`, `Servicios_Publicos`, `Servidumbre`, `Superficies_Agua`, `Transporte`. La tabla tiene 38 filas: estos 13 valores, que son los del levantamiento catastral (`LC_PredioTipo`), más 9 del núcleo y 16 del modelo RIC que la carga no usa |
| `cr_construccionplantatipo` | 5 | `cr_unidadconstruccion.tipo_planta` | `Mezanine`, `Piso`, `Semisotano`, `Sotano`, `Subterraneo` |
| `cr_documentotipo` | 7 | `cr_interesado.tipo_documento`, `lc_contactovisita.tipo_documento_quien_atendio` | `Cedula_Ciudadania`, `Cedula_Extranjeria`, `NIT`, `Pasaporte`, `Registro_Civil`, `Secuencial`, `Tarjeta_Identidad` |
| `cr_grupoetnicotipo` | 6 | `cr_interesado.grupo_etnico` | `Indigena`, `Negro_Afrocolombiano`, `Ninguno`, `Palenquero`, `Raizal`, `Rrom` |
| `cr_interesadotipo` | 2 | `cr_interesado.tipo` | `Persona_Juridica`, `Persona_Natural` |
| `cr_sexotipo` | 3 | `cr_interesado.sexo` | `Femenino`, `Masculino`, `Sin_Determinar` |
| `cr_unidadconstrucciontipo` | 5 | `cr_caracteristicasunidadconstruccion.tipo_unidad_construccion` | `Anexo`, `Comercial`, `Industrial`, `Institucional`, `Residencial` |
| `cr_usouconstipo` | 102 | `cr_caracteristicasunidadconstruccion.uso` | Los códigos tienen la forma `Grupo.Uso`; se listan aparte, [por grupo](#usos-de-la-unidad-de-construcción-cr_usouconstipo) |
| `extdireccion_clase_via_principal` | 10 | `extdireccion.clase_via_principal` (sin datos) | `Autopista`, `Avenida`, `Avenida_Calle`, `Avenida_Carrera`, `Calle`, `Carrera`, `Circular`, `Circunvalar`, `Diagonal`, `Transversal` |
| `extdireccion_sector_ciudad` | 4 | `extdireccion.sector_ciudad` (sin datos) | `Este`, `Norte`, `Oeste`, `Sur` |
| `extdireccion_sector_predio` | 4 | `extdireccion.sector_predio` (sin datos) | `Este`, `Norte`, `Oeste`, `Sur` |
| `extdireccion_tipo_direccion` | 2 | `extdireccion.tipo_direccion` | `Estructurada`, `No_Estructurada` |
| `lc_condicionprediotipo` | 10 | `lc_predio.condicion_predio` | `Bien_Uso_Publico`, `Condominio.Matriz`, `Condominio.Unidad_Predial`, `Informal`, `NPH`, `PH.Matriz`, `PH.Unidad_Predial`, `Parque_Cementerio.Matriz`, `Parque_Cementerio.Unidad_Predial`, `Via` |
| `lc_derechotipo` | 3 | `lc_derecho.tipo` | `Dominio`, `Ocupacion`, `Posesion` |
| `lc_destinacioneconomicatipo` | 27 | `lc_predio.destinacion_economica` | `Acuicola`, `Agricola`, `Agroforestal`, `Agroindustrial`, `Agropecuario`, `Comercial`, `Cultural`, `Educativo`, `Forestal`, `Habitacional`, `Industrial`, `Infraestructura_Asociada_Produccion_Agropecuaria`, `Infraestructura_Hidraulica`, `Infraestructura_Saneamiento_Basico`, `Infraestructura_Seguridad`, `Infraestructura_Transporte`, `Institucional`, `Lote_No_Urbanizable`, `Lote_Urbanizable_No_Urbanizado`, `Lote_Urbanizado_No_Construido`, `Mineria_Hidrocarburos`, `Pecuario`, `Recreacional`, `Religioso`, `Salubridad`, `Servicios_Funerarios`, `Uso_Publico` |
| `lc_estructuranovedadnumeropredial_tipo_novedad` | 5 | `lc_estructuranovedadnumeropredial.tipo_novedad` | `Cambio_Numero_Predial`, `Cancelacion`, `Desenglobe`, `Englobe`, `Predio_Nuevo` |
| `lc_resultadovisitatipo` | 8 | `lc_datosadicionaleslevantamientocatastral.resultado_visita` | `Exitoso`, `Incompleto`, `Menor_Edad`, `No_Hay_Nadie`, `No_Permitieron_Acceso`, `Sin_Visita`, `Situacion_Orden_Publico`, `Zona_Dificil_Acceso` |

Tres dominios quedan en la base sin que ninguna fila los use, porque las columnas que apuntan a ellos están vacías: `extdireccion_clase_via_principal`, `extdireccion_sector_ciudad` y `extdireccion_sector_predio`.

### Usos de la unidad de construcción (`cr_usouconstipo`)

El código completo es `Grupo.Uso`, por ejemplo `Residencial.Vivienda_Hasta_3_Pisos`.

| Grupo | Usos | Códigos |
| --- | ---: | --- |
| `Residencial` | 15 | `Apartamentos_4_y_mas_pisos`, `Apartamentos_4_y_mas_pisos_en_PH`, `Barracas`, `Casa_Elbas`, `Depositos_Lockers`, `Garajes_Cubiertos`, `Garajes_En_PH`, `Salon_Comunal`, `Secadero_Ropa`, `Vivienda_Colonial`, `Vivienda_Colonial_en_PH`, `Vivienda_Hasta_3_Pisos`, `Vivienda_Hasta_3_Pisos_En_PH`, `Vivienda_Recreacional`, `Vivienda_Recreacional_En_PH` |
| `Comercial` | 24 | `Bodegas_Comerciales_Grandes_Almacenes`, `Bodegas_Comerciales_en_PH`, `Centros_Comerciales`, `Centros_Comerciales_en_PH`, `Clubes_Casinos`, `Comercio`, `Comercio_Colonial`, `Comercio_en_PH`, `Hotel_Colonial`, `Hoteles`, `Hoteles_en_PH`, `Oficinas_Consultorios`, `Oficinas_Consultorios_Coloniales`, `Oficinas_Consultorios_en_PH`, `Parque_Diversiones`, `Parqueaderos`, `Parqueaderos_en_PH`, `Pensiones_y_Residencias`, `Plaza_Mercado`, `Restaurante_Colonial`, `Restaurantes`, `Restaurantes_en_PH`, `Teatro_Cinemas`, `Teatro_Cinemas_en_PH` |
| `Industrial` | 5 | `Bodega_Casa_Bomba`, `Bodegas_Casa_Bomba_en_PH`, `Industrias`, `Industrias_en_PH`, `Talleres` |
| `Institucional` | 23 | `Aulas_de_Clases`, `Biblioteca`, `Carceles`, `Casas_de_Culto`, `Clinicas_Hospitales_Centros_Medicos`, `Colegio_y_Universidades`, `Coliseos`, `Entidad_Educativa_Colonial_Colegio_Colonial`, `Estadios`, `Fuertes_y_Castillos`, `Iglesia`, `Iglesia_en_PH`, `Instalaciones_Militares`, `Jardin_Infantil_en_Casa`, `Museos`, `Parque_Cementerio`, `Planetario`, `Plaza_de_Toros`, `Puestos_de_Salud`, `Seminarios_Conventos`, `Teatro`, `Unidad_Deportiva`, `Velodromo_Patinodromo` |
| `Anexo` | 35 | `Albercas_Banaderas`, `Beneficiaderos`, `Camaroneras`, `Canchas`, `Canchas_de_Tenis`, `Carretera`, `Cerramiento`, `Cimientos_Estructura_Muros_y_Placa_Base`, `Cocheras_Marraneras_Porquerizas`, `Construccion_en_Membrana_Arquitectonica`, `Contenedor`, `Corrales`, `Establos_Pesebreras_Caballerizas`, `Estacion_Bombeo`, `Estacion_Sistema_Transporte`, `Galpones_Gallineros`, `Glamping`, `Hangar`, `Kioscos`, `Lagunas_de_Oxidacion`, `Marquesinas_Patios_Cubiertos`, `Muelles`, `Murallas`, `Pergolas`, `Piscinas`, `Pista_Aeropuerto`, `Pozos`, `Ramadas_Cobertizos_Caneyes`, `Secaderos`, `Silos`, `Tanques`, `Toboganes`, `Torre_de_Control`, `Torres_de_Enfriamiento`, `Via_Ferrea` |

## Tablas de la carga

Las crea ili2pg para registrar qué se cargó. Tienen una fila cada una, porque la base tiene una sola carga, y no hacen falta para el análisis.

### `t_ili2db_dataset`

| Columna | Tipo | Oblig. | Descripción |
| --- | --- | --- | --- |
| `t_id` | bigint | Sí | Llave primaria |
| `datasetname` | varchar(200) | No | Nombre del conjunto de datos: el del archivo de transferencia que se cargó |

### `t_ili2db_basket`

| Columna | Tipo | Oblig. | Descripción |
| --- | --- | --- | --- |
| `t_id` | bigint | Sí | Llave primaria; es el valor de la columna `t_basket` de todas las tablas de datos |
| `dataset` | bigint | No | **→ `t_ili2db_dataset`.** Conjunto de datos al que pertenece la carga |
| `topic` | varchar(200) | Sí | Tema del modelo que se cargó (`Levantamiento_Catastral`) |
| `t_ili_tid` | varchar(200) | No | Identificador de la carga en el archivo de transferencia de origen |
| `attachmentkey` | varchar(200) | Sí | Clave con que ili2pg identifica los archivos de la carga |
| `domains` | varchar(1024) | No | Asignación de dominios genéricos de la carga, propia de INTERLIS |
