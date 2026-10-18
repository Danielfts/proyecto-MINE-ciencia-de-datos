"""Convierte la exportación de predios.sql en un archivo parquet con un predio por fila.

Desde la raíz del repositorio:

    psql -XAtq -d catastro_pruned -f datos/predios/predios.sql \\
      | uv run python datos/predios/construir.py datos/predios/predios.parquet \\
          --facturacion "datos/predios/Predial-Comparativo Predial de una vigencia 2025-2026.xlsx"

Lee de la entrada estándar un objeto JSON por línea, le aplica el esquema de abajo, le
une la facturación del impuesto predial y escribe el parquet. Antes de escribir comprueba
que cada objeto trae exactamente los campos del esquema, ni uno más ni uno menos, que hay
un predio por fila, que ningún campo tiene nombre de dato personal, que del Excel de
facturación solo se leyeron sus cuatro columnas y que queda una fila de facturación por
código. El esquema y el significado de cada campo están en README.md, en esta misma carpeta.

El parquet no va al repositorio: el .gitignore excluye los archivos *.parquet.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

PREDIOS_ESPERADOS = 22_220

# Del Excel de facturación solo se leen estas columnas, de la hoja Consulta. Las filas 1 a 6
# son un encabezado que identifica al municipio; los nombres de columna están en la fila 7.
# Las columnas sin sufijo son de la vigencia 2026 y las que terminan en 1, de la 2025.
HOJA_FACTURACION = "Consulta"
FILA_ENCABEZADO_FACTURACION = 6
COLUMNAS_FACTURACION = ["CODIGOCATASTRAL", "IMPPREDIAL", "INDPAGO", "INDPAGO1"]

# Fragmentos que no pueden aparecer en el nombre de ningún campo, en ningún nivel
NOMBRES_PROHIBIDOS = ("documento_identidad", "numero_documento", "tipo_documento", "nombre_",
                      "apellido", "celular", "correo", "domicilio", "razon_social", "etnico")

texto, entero, entero32, real, booleano, fecha = (pa.string(), pa.int64(), pa.int32(),
                                                   pa.float64(), pa.bool_(), pa.date32())

MEDIDAS_GEOMETRIA = [
    ("area_geometrica", real),
    ("perimetro", real),
    ("compacidad", real),
    ("n_vertices", entero32),
    ("n_poligonos", entero32),
    ("geometria_valida", booleano),
]

TERRENO = pa.struct([
    ("id_terreno", entero),
    ("area_terreno", real),
    *MEDIDAS_GEOMETRIA,
])

CONSTRUCCION = pa.struct([
    ("id_construccion", entero),
    ("identificador", texto),
    ("total_pisos", entero32),
    ("total_sotanos", entero32),
    ("total_mezanines", entero32),
    ("total_semisotanos", entero32),
    ("area_total_construccion", real),
    ("altura_total_construccion", real),
    *MEDIDAS_GEOMETRIA,
])

UNIDAD = pa.struct([
    ("id_unidad", entero),
    ("id_construccion", entero),
    ("identificador", texto),
    ("tipo_unidad_construccion", texto),
    ("uso", texto),
    ("tipo_planta", texto),
    ("planta_ubicacion", entero32),
    ("total_plantas", entero32),
    ("anio_construccion", entero32),
    ("area_construida", real),
    ("area_construida_caracteristicas", real),
    ("area_privada_construida", real),
    ("altura", entero32),
    ("observaciones", texto),
    *MEDIDAS_GEOMETRIA,
])

PH_MATRIZ = pa.struct([
    ("area_total_terreno", real),
    ("area_total_terreno_privada", real),
    ("area_total_terreno_comun", real),
    ("area_total_construida", real),
    ("area_total_construida_privada", real),
    ("area_total_construida_comun", real),
    ("numero_torres", entero32),
    ("total_unidades_privadas", entero32),
])

TITULARES = pa.struct([
    ("es_agrupacion", booleano),
    ("tipo_agrupacion", texto),
    ("n_titulares", entero32),
    ("n_persona_natural", entero32),
    ("n_persona_juridica", entero32),
    ("n_femenino", entero32),
    ("n_masculino", entero32),
    ("n_sexo_sin_determinar", entero32),
    ("participacion_max", real),
    ("max_predios_mismo_titular", entero32),
])

CAMPOS_CATASTRO = [
    # Predio
    ("id_predio", entero),
    ("departamento", texto),
    ("municipio", texto),
    ("numero_predial", texto),
    ("zona", texto),
    ("sector", texto),
    ("comuna", texto),
    ("barrio", texto),
    ("manzana_vereda", texto),
    ("numero_terreno", texto),
    ("condicion_propiedad", texto),
    ("edificio", texto),
    ("piso", texto),
    ("unidad", texto),
    ("id_operacion", texto),
    ("codigo_orip", texto),
    ("matricula_inmobiliaria", entero),
    ("codigo_homologado", texto),
    ("avaluo_catastral", real),
    ("tipo", texto),
    ("condicion_predio", texto),
    ("destinacion_economica", texto),
    ("nombre", texto),
    # Levantamiento
    ("area_registral_m2", real),
    ("fecha_visita_predial", fecha),
    ("resultado_visita", texto),
    ("observaciones", texto),
    ("tipo_novedad_numero_predial", texto),
    ("n_contactos_visita", entero32),
    ("autoriza_notificaciones", booleano),
    # Dirección
    ("tipo_direccion", texto),
    ("es_direccion_principal", booleano),
    # Propiedad horizontal, condominio e informalidad
    ("ph_matriz", PH_MATRIZ),
    ("id_predio_matriz", entero),
    ("coeficiente_copropiedad", real),
    ("n_unidades_prediales", entero32),
    ("ids_predios_informales", pa.list_(entero)),
    ("ids_predios_formales", pa.list_(entero)),
    # Unidades espaciales
    ("terreno", TERRENO),
    ("construcciones", pa.list_(CONSTRUCCION)),
    ("unidades", pa.list_(UNIDAD)),
    # Derecho y fuente administrativa
    ("tipo_derecho", texto),
    ("fraccion_derecho", real),
    ("fecha_inicio_tenencia", fecha),
    ("tipo_fuente", texto),
    ("estado_disponibilidad", texto),
    ("tipo_principal", texto),
    ("fecha_documento_fuente", fecha),
    ("ente_emisor", texto),
    ("numero_fuente", texto),
    ("observacion_fuente", texto),
    # Titulares, solo conteos
    ("titulares", TITULARES),
]

# Vienen del Excel de facturación, no de predios.sql; nulos si el predio no se factura
CAMPOS_FACTURACION = [
    ("ipu_facturado_2026", real),
    ("pago_2026", booleano),
    ("pago_2025", booleano),
]

ESQUEMA = pa.schema(CAMPOS_CATASTRO + CAMPOS_FACTURACION, metadata={
    "descripcion": "Predios del levantamiento catastral, uno por fila, sin datos personales, "
                   "con la facturación del impuesto predial. Ver datos/predios/README.md",
})


def ajustar(valor, tipo, ruta):
    """Comprueba que el valor tiene la forma del tipo y convierte las fechas.

    Falla si un objeto trae campos de más o de menos, para que un cambio en predios.sql
    no se pierda en silencio (pyarrow ignora los campos que no están en el esquema).
    """
    if valor is None:
        return None
    if pa.types.is_struct(tipo):
        campos = [tipo.field(i) for i in range(tipo.num_fields)]
        sobran = set(valor) - {c.name for c in campos}
        faltan = {c.name for c in campos} - set(valor)
        if sobran or faltan:
            sys.exit(f"{ruta}: campos que no están en el esquema {sorted(sobran)}, "
                     f"campos que faltan {sorted(faltan)}")
        return {c.name: ajustar(valor[c.name], c.type, f"{ruta}.{c.name}") for c in campos}
    if pa.types.is_list(tipo):
        return [ajustar(v, tipo.value_type, f"{ruta}[]") for v in valor]
    if pa.types.is_date(tipo):
        return date.fromisoformat(valor)
    return valor


def nombres(tipo, prefijo=""):
    """Todos los nombres de campo del esquema, en todos los niveles."""
    if pa.types.is_list(tipo):
        yield from nombres(tipo.value_type, prefijo)
    elif pa.types.is_struct(tipo):
        for i in range(tipo.num_fields):
            campo = tipo.field(i)
            yield prefijo + campo.name
            yield from nombres(campo.type, prefijo + campo.name + ".")


def leer_facturacion(archivo):
    """Lee el Excel de facturación y deja una fila por código catastral.

    Devuelve la tabla indexada por código, con los tres campos de CAMPOS_FACTURACION, y el
    número de códigos que estaban repetidos. Un código repetido junta dos predios de 2025
    en uno de 2026: sus filas tienen que coincidir en las columnas de 2026, y el predio
    cuenta como pagado en 2025 solo si todos los que lo formaron pagaron.
    """
    leido = pd.read_excel(archivo, sheet_name=HOJA_FACTURACION,
                          header=FILA_ENCABEZADO_FACTURACION, usecols=COLUMNAS_FACTURACION,
                          dtype={"CODIGOCATASTRAL": str})
    if sorted(leido.columns) != sorted(COLUMNAS_FACTURACION):
        sys.exit(f"Del Excel de facturación se leyeron otras columnas: {list(leido.columns)}")

    por_codigo = leido.groupby("CODIGOCATASTRAL")
    repetidos = por_codigo.size().gt(1).sum()
    if por_codigo[["IMPPREDIAL", "INDPAGO"]].nunique(dropna=False).gt(1).any(axis=None):
        sys.exit("Hay códigos repetidos en la facturación que difieren en las columnas de 2026")
    if por_codigo["INDPAGO1"].agg(lambda v: 0 < v.isna().sum() < len(v)).any():
        sys.exit("Hay códigos repetidos en la facturación con y sin pago de 2025")

    facturacion = pd.DataFrame({
        "ipu_facturado_2026": por_codigo["IMPPREDIAL"].first(),
        "pago_2026": por_codigo["INDPAGO"].first().astype(bool),
        # min: 0 si alguno no pagó; NaN solo si el predio no existía en 2025
        "pago_2025": por_codigo["INDPAGO1"].min(),
    })
    if not facturacion.index.is_unique:
        sys.exit("Quedó más de una fila de facturación por código")
    return facturacion, repetidos


def a_python(valor, tipo):
    """Convierte un valor de pandas al de Python que espera pyarrow, con NaN como nulo."""
    if pd.isna(valor):
        return None
    return bool(valor) if tipo == booleano else float(valor)


def main():
    opciones = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    opciones.add_argument("salida", type=Path, help="archivo parquet que se escribe")
    opciones.add_argument("--facturacion", type=Path, required=True,
                          help="Excel con la facturación del impuesto predial 2025-2026")
    argumentos = opciones.parse_args()
    salida = argumentos.salida
    if sys.stdin.isatty():
        sys.exit("Falta la entrada: la salida de predios.sql por una tubería (ver --help)")

    prohibidos = [n for n in nombres(pa.struct(ESQUEMA)) if any(p in n for p in NOMBRES_PROHIBIDOS)]
    if prohibidos:
        sys.exit(f"El esquema tiene campos con nombre de dato personal: {prohibidos}")

    raiz = pa.struct(CAMPOS_CATASTRO)
    filas = [ajustar(json.loads(linea), raiz, f"línea {i}")
             for i, linea in enumerate(sys.stdin, start=1) if linea.strip()]

    ids = [f["id_predio"] for f in filas]
    if len(filas) != PREDIOS_ESPERADOS:
        sys.exit(f"Llegaron {len(filas)} predios y se esperaban {PREDIOS_ESPERADOS}")
    if len(set(ids)) != len(ids):
        sys.exit("Hay predios repetidos")
    numeros = {f["numero_predial"] for f in filas}
    if None in numeros or len(numeros) != len(filas):
        sys.exit("Hay predios sin número predial o con el número repetido")

    facturacion, repetidos = leer_facturacion(argumentos.facturacion)
    unidos = facturacion.index.isin(list(numeros))
    facturas = facturacion.to_dict("index")
    for fila in filas:
        factura = facturas.get(fila["numero_predial"])
        for campo, tipo in CAMPOS_FACTURACION:
            fila[campo] = None if factura is None else a_python(factura[campo], tipo)

    tabla = pa.Table.from_pylist(filas, schema=ESQUEMA)
    if tabla.num_rows != PREDIOS_ESPERADOS:
        sys.exit(f"La unión con la facturación dejó {tabla.num_rows} predios")
    total = pc.sum(tabla["ipu_facturado_2026"]).as_py()
    total_excel = facturacion.loc[unidos, "ipu_facturado_2026"].sum()
    if abs(total - total_excel) > 0.5:
        sys.exit(f"El IPU facturado del parquet ({total:,.0f}) no suma lo mismo que el "
                 f"del Excel para los códigos unidos ({total_excel:,.0f})")

    print(f"Facturación: {len(facturacion)} códigos ({repetidos} repetidos, unidos en uno), "
          f"{unidos.sum()} unidos a un predio, {(~unidos).sum()} sin predio (se descartan), "
          f"{tabla.num_rows - unidos.sum()} predios sin facturación")
    print(f"IPU facturado 2026 de los predios unidos: {total:,.0f} COP")

    salida.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tabla, salida, compression="zstd")
    print(f"{salida}: {tabla.num_rows} predios, {tabla.num_columns} columnas, "
          f"{salida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
