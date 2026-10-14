"""Convierte la exportación de predios.sql en un archivo parquet con un predio por fila.

Desde la raíz del repositorio:

    psql -XAtq -d catastro_pruned -f datos/predios/predios.sql \\
      | uv run python datos/predios/construir.py datos/predios/predios.parquet

Lee de la entrada estándar un objeto JSON por línea, le aplica el esquema de abajo y
escribe el parquet. Antes de escribir comprueba que cada objeto trae exactamente los
campos del esquema, ni uno más ni uno menos, que hay un predio por fila y que ningún
campo tiene nombre de dato personal. El esquema y el significado de cada campo están en
README.md, en esta misma carpeta.

El parquet no va al repositorio: el .gitignore excluye los archivos *.parquet.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PREDIOS_ESPERADOS = 22_220

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

ESQUEMA = pa.schema([
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
], metadata={
    "descripcion": "Predios del levantamiento catastral, uno por fila, sin datos personales. "
                   "Ver datos/predios/README.md",
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


def main():
    opciones = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    opciones.add_argument("salida", type=Path, help="archivo parquet que se escribe")
    salida = opciones.parse_args().salida
    if sys.stdin.isatty():
        sys.exit("Falta la entrada: la salida de predios.sql por una tubería (ver --help)")

    prohibidos = [n for n in nombres(pa.struct(ESQUEMA)) if any(p in n for p in NOMBRES_PROHIBIDOS)]
    if prohibidos:
        sys.exit(f"El esquema tiene campos con nombre de dato personal: {prohibidos}")

    raiz = pa.struct(ESQUEMA)
    filas = [ajustar(json.loads(linea), raiz, f"línea {i}")
             for i, linea in enumerate(sys.stdin, start=1) if linea.strip()]

    ids = [f["id_predio"] for f in filas]
    if len(filas) != PREDIOS_ESPERADOS:
        sys.exit(f"Llegaron {len(filas)} predios y se esperaban {PREDIOS_ESPERADOS}")
    if len(set(ids)) != len(ids):
        sys.exit("Hay predios repetidos")

    tabla = pa.Table.from_pylist(filas, schema=ESQUEMA)
    salida.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tabla, salida, compression="zstd")
    print(f"{salida}: {tabla.num_rows} predios, {tabla.num_columns} columnas, "
          f"{salida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
