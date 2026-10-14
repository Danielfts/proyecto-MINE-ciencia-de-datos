-- Exporta la base catastral podada como un objeto JSON por predio, sin datos personales.
--
-- Se ejecuta con psql sobre la base podada y su salida va directo a construir.py, que la
-- convierte en el archivo parquet (ver README.md, en esta misma carpeta):
--
--     psql -XAtq -d catastro_pruned -f datos/predios/predios.sql \
--       | uv run python datos/predios/construir.py datos/predios/predios.parquet
--
-- Cada línea de la salida es un predio de lc_predio. Lo que cuelga del predio con relación de
-- uno a uno queda como campos del objeto; lo que es de uno a muchos (construcciones, unidades
-- de construcción, predios informales) queda como listas anidadas.
--
-- Lo que NO sale de la base:
--   - Nada de cr_interesado, col_miembros ni lc_contactovisita, salvo conteos por predio:
--     cuántos titulares, de qué tipo, de qué sexo, cuántos contactos de visita.
--   - Las geometrías: solo medidas calculadas a partir de ellas (área, perímetro, compacidad),
--     sin coordenadas.
--   - Las columnas técnicas de ili2db y las que tienen un solo valor en toda la carga.
--   - Los números de 6 o más dígitos de los textos libres, que se cambian por #: algunos
--     son documentos de identidad de interesados o de quienes atendieron la visita.
--
-- Todo ocurre en una transacción de solo lectura: el script no modifica la base.

\set ON_ERROR_STOP on

BEGIN READ ONLY;
SET LOCAL search_path = xtf, public;
-- ST_IsValid informa por NOTICE dónde falla una geometría, con sus coordenadas
SET LOCAL client_min_messages = warning;

WITH
-- Titulares de cada predio: el interesado del derecho, o los miembros de la agrupación
titular AS (
    SELECT d.unidad_lc_predio AS predio, d.interesado_cr_interesado AS interesado,
           1.0::numeric AS participacion
    FROM lc_derecho d
    WHERE d.interesado_cr_interesado IS NOT NULL
    UNION ALL
    SELECT d.unidad_lc_predio, m.interesado_cr_interesado, m.participacion
    FROM lc_derecho d
    JOIN col_miembros m ON m.agrupacion_cr_agrupacioninteresados = d.interesado_cr_agrupacioninteresados
),
predios_por_interesado AS (
    SELECT interesado, count(DISTINCT predio) AS n
    FROM titular
    GROUP BY interesado
),
titulares AS (
    SELECT t.predio,
           count(*) AS n_titulares,
           count(*) FILTER (WHERE it.ilicode = 'Persona_Natural') AS n_persona_natural,
           count(*) FILTER (WHERE it.ilicode = 'Persona_Juridica') AS n_persona_juridica,
           count(*) FILTER (WHERE sx.ilicode = 'Femenino') AS n_femenino,
           count(*) FILTER (WHERE sx.ilicode = 'Masculino') AS n_masculino,
           count(*) FILTER (WHERE sx.ilicode = 'Sin_Determinar') AS n_sexo_sin_determinar,
           max(t.participacion) AS participacion_max,
           max(ppi.n) AS max_predios_mismo_titular
    FROM titular t
    JOIN cr_interesado i ON i.t_id = t.interesado
    JOIN cr_interesadotipo it ON it.t_id = i.tipo
    LEFT JOIN cr_sexotipo sx ON sx.t_id = i.sexo
    JOIN predios_por_interesado ppi ON ppi.interesado = t.interesado
    GROUP BY t.predio
),
contactos AS (
    SELECT da.lc_predio AS predio, count(*) AS n_contactos_visita,
           bool_or(c.autoriza_notificaciones) AS autoriza_notificaciones
    FROM lc_contactovisita c
    JOIN lc_datosadicionaleslevantamientocatastral da ON da.t_id = c.lc_datos_adicionales
    GROUP BY da.lc_predio
),
-- Medidas de las geometrías. No traen arcos, así que pasarlas a polígonos no cambia su forma
geom_terreno AS (
    SELECT t.t_id, ST_Force2D(ST_CurveToLine(t.geometria)) AS g FROM cr_terreno t
),
geom_construccion AS (
    SELECT c.t_id, ST_Force2D(ST_CurveToLine(c.geometria)) AS g FROM cr_construccion c
),
geom_unidad AS (
    SELECT u.t_id, ST_Force2D(ST_CurveToLine(u.geometria)) AS g FROM cr_unidadconstruccion u
),
terrenos AS (
    SELECT ub.baunit_lc_predio AS predio,
           json_build_object(
               'id_terreno', t.t_id,
               'area_terreno', t.area_terreno,
               'area_geometrica', round(ST_Area(g.g)::numeric, 2),
               'perimetro', round(ST_Perimeter(g.g)::numeric, 2),
               'compacidad', round((4 * pi() * ST_Area(g.g) / nullif(ST_Perimeter(g.g) ^ 2, 0))::numeric, 4),
               'n_vertices', ST_NPoints(g.g),
               'n_poligonos', ST_NumGeometries(g.g),
               'geometria_valida', ST_IsValid(g.g)
           ) AS terreno
    FROM col_uebaunit ub
    JOIN cr_terreno t ON t.t_id = ub.ue_cr_terreno
    JOIN geom_terreno g ON g.t_id = t.t_id
),
construcciones AS (
    SELECT ub.baunit_lc_predio AS predio,
           json_agg(json_build_object(
               'id_construccion', c.t_id,
               'identificador', c.identificador,
               'total_pisos', c.total_pisos,
               'total_sotanos', c.total_sotanos,
               'total_mezanines', c.total_mezanines,
               'total_semisotanos', c.total_semisotanos,
               'area_total_construccion', c.area_total_construccion,
               'altura_total_construccion', c.altura_total_construccion,
               'area_geometrica', round(ST_Area(g.g)::numeric, 2),
               'perimetro', round(ST_Perimeter(g.g)::numeric, 2),
               'compacidad', round((4 * pi() * ST_Area(g.g) / nullif(ST_Perimeter(g.g) ^ 2, 0))::numeric, 4),
               'n_vertices', ST_NPoints(g.g),
               'n_poligonos', ST_NumGeometries(g.g),
               'geometria_valida', ST_IsValid(g.g)
           ) ORDER BY c.t_id) AS construcciones
    FROM col_uebaunit ub
    JOIN cr_construccion c ON c.t_id = ub.ue_cr_construccion
    JOIN geom_construccion g ON g.t_id = c.t_id
    GROUP BY ub.baunit_lc_predio
),
unidades AS (
    SELECT ub.baunit_lc_predio AS predio,
           json_agg(json_build_object(
               'id_unidad', u.t_id,
               -- En propiedad horizontal suele ser una construcción del predio matriz
               'id_construccion', u.cr_construccion,
               'identificador', c.identificador,
               'tipo_unidad_construccion', tu.ilicode,
               'uso', uso.ilicode,
               'tipo_planta', tp.ilicode,
               'planta_ubicacion', u.planta_ubicacion,
               'total_plantas', c.total_plantas,
               'anio_construccion', c.anio_construccion,
               'area_construida', u.area_construida,
               'area_construida_caracteristicas', c.area_construida,
               'area_privada_construida', c.area_privada_construida,
               'altura', u.altura,
               'observaciones', regexp_replace(c.observaciones, '\d(?:\.?\d){5,}', '#', 'g'),
               'area_geometrica', round(ST_Area(g.g)::numeric, 2),
               'perimetro', round(ST_Perimeter(g.g)::numeric, 2),
               'compacidad', round((4 * pi() * ST_Area(g.g) / nullif(ST_Perimeter(g.g) ^ 2, 0))::numeric, 4),
               'n_vertices', ST_NPoints(g.g),
               'n_poligonos', ST_NumGeometries(g.g),
               'geometria_valida', ST_IsValid(g.g)
           ) ORDER BY u.t_id) AS unidades
    FROM col_uebaunit ub
    JOIN cr_unidadconstruccion u ON u.t_id = ub.ue_cr_unidadconstruccion
    JOIN cr_caracteristicasunidadconstruccion c ON c.t_id = u.cr_caracteristicasunidadconstruccion
    JOIN cr_unidadconstrucciontipo tu ON tu.t_id = c.tipo_unidad_construccion
    JOIN cr_usouconstipo uso ON uso.t_id = c.uso
    JOIN cr_construccionplantatipo tp ON tp.t_id = u.tipo_planta
    JOIN geom_unidad g ON g.t_id = u.t_id
    GROUP BY ub.baunit_lc_predio
),
informales AS (
    SELECT lc_predio_formal AS predio, json_agg(lc_predio_informal ORDER BY lc_predio_informal) AS ids
    FROM lc_predio_informalidad
    GROUP BY lc_predio_formal
),
formales AS (
    SELECT lc_predio_informal AS predio, json_agg(lc_predio_formal ORDER BY lc_predio_formal) AS ids
    FROM lc_predio_informalidad
    GROUP BY lc_predio_informal
),
unidades_prediales AS (
    SELECT matriz AS predio, count(*) AS n FROM cr_predio_copropiedad GROUP BY matriz
),
fila AS (
    SELECT
        -- Predio
        p.t_id AS id_predio,
        p.departamento,
        p.municipio,
        p.numero_predial,
        -- Componentes del número predial nacional de 30 dígitos (después de departamento y municipio)
        substr(p.numero_predial, 6, 2) AS zona,
        substr(p.numero_predial, 8, 2) AS sector,
        substr(p.numero_predial, 10, 2) AS comuna,
        substr(p.numero_predial, 12, 2) AS barrio,
        substr(p.numero_predial, 14, 4) AS manzana_vereda,
        substr(p.numero_predial, 18, 4) AS numero_terreno,
        substr(p.numero_predial, 22, 1) AS condicion_propiedad,
        substr(p.numero_predial, 23, 2) AS edificio,
        substr(p.numero_predial, 25, 2) AS piso,
        substr(p.numero_predial, 27, 4) AS unidad,
        p.id_operacion,
        p.codigo_orip,
        p.matricula_inmobiliaria,
        p.codigo_homologado,
        p.avaluo_catastral,
        tipo.ilicode AS tipo,
        cond.ilicode AS condicion_predio,
        dest.ilicode AS destinacion_economica,
        regexp_replace(p.nombre, '\d(?:\.?\d){5,}', '#', 'g') AS nombre,
        -- Levantamiento
        da.area_registral_m2,
        da.fecha_visita_predial,
        rv.ilicode AS resultado_visita,
        regexp_replace(da.observaciones, '\d(?:\.?\d){5,}', '#', 'g') AS observaciones,
        tn.ilicode AS tipo_novedad_numero_predial,
        coalesce(ct.n_contactos_visita, 0) AS n_contactos_visita,
        ct.autoriza_notificaciones,
        -- Dirección (nombre_predio es igual a nombre en todas las filas y no se repite)
        td.ilicode AS tipo_direccion,
        dir.es_direccion_principal,
        -- Propiedad horizontal, condominio e informalidad
        CASE WHEN ph.t_id IS NOT NULL THEN json_build_object(
            'area_total_terreno', ph.area_total_terreno,
            'area_total_terreno_privada', ph.area_total_terreno_privada,
            'area_total_terreno_comun', ph.area_total_terreno_comun,
            'area_total_construida', ph.area_total_construida,
            'area_total_construida_privada', ph.area_total_construida_privada,
            'area_total_construida_comun', ph.area_total_construida_comun,
            'numero_torres', ph.numero_torres,
            'total_unidades_privadas', ph.total_unidades_privadas
        ) END AS ph_matriz,
        cop.matriz AS id_predio_matriz,
        cop.coeficiente AS coeficiente_copropiedad,
        coalesce(up.n, 0) AS n_unidades_prediales,
        coalesce(inf.ids, '[]'::json) AS ids_predios_informales,
        coalesce(fml.ids, '[]'::json) AS ids_predios_formales,
        -- Unidades espaciales
        ter.terreno,
        coalesce(con.construcciones, '[]'::json) AS construcciones,
        coalesce(uni.unidades, '[]'::json) AS unidades,
        -- Derecho y fuente administrativa (descripcion tiene un solo valor y no se exporta)
        tder.ilicode AS tipo_derecho,
        der.fraccion_derecho,
        der.fecha_inicio_tenencia,
        tf.ilicode AS tipo_fuente,
        ed.ilicode AS estado_disponibilidad,
        fp.ilicode AS tipo_principal,
        fa.fecha_documento_fuente,
        fa.ente_emisor,
        regexp_replace(fa.numero_fuente, '\d(?:\.?\d){5,}', '#', 'g') AS numero_fuente,
        regexp_replace(fa.observacion, '\d(?:\.?\d){5,}', '#', 'g') AS observacion_fuente,
        -- Titulares: solo conteos. participacion_max es 1 cuando el titular es uno solo
        json_build_object(
            'es_agrupacion', der.interesado_cr_agrupacioninteresados IS NOT NULL,
            'tipo_agrupacion', ga.ilicode,
            'n_titulares', tit.n_titulares,
            'n_persona_natural', tit.n_persona_natural,
            'n_persona_juridica', tit.n_persona_juridica,
            'n_femenino', tit.n_femenino,
            'n_masculino', tit.n_masculino,
            'n_sexo_sin_determinar', tit.n_sexo_sin_determinar,
            'participacion_max', tit.participacion_max,
            'max_predios_mismo_titular', tit.max_predios_mismo_titular
        ) AS titulares
    FROM lc_predio p
    JOIN col_unidadadministrativabasicatipo tipo ON tipo.t_id = p.tipo
    JOIN lc_condicionprediotipo cond ON cond.t_id = p.condicion_predio
    JOIN lc_destinacioneconomicatipo dest ON dest.t_id = p.destinacion_economica
    JOIN lc_datosadicionaleslevantamientocatastral da ON da.lc_predio = p.t_id
    JOIN lc_resultadovisitatipo rv ON rv.t_id = da.resultado_visita
    LEFT JOIN lc_estructuranovedadnumeropredial nv ON nv.lc_dtsdcnlstmntctstral_novedad_numeros_prediales = da.t_id
    LEFT JOIN lc_estructuranovedadnumeropredial_tipo_novedad tn ON tn.t_id = nv.tipo_novedad
    LEFT JOIN contactos ct ON ct.predio = p.t_id
    JOIN extdireccion dir ON dir.lc_predio_direccion = p.t_id
    JOIN extdireccion_tipo_direccion td ON td.t_id = dir.tipo_direccion
    LEFT JOIN cr_datosphcondominio ph ON ph.lc_predio = p.t_id
    LEFT JOIN cr_predio_copropiedad cop ON cop.unidad_predial = p.t_id
    LEFT JOIN unidades_prediales up ON up.predio = p.t_id
    LEFT JOIN informales inf ON inf.predio = p.t_id
    LEFT JOIN formales fml ON fml.predio = p.t_id
    LEFT JOIN terrenos ter ON ter.predio = p.t_id
    LEFT JOIN construcciones con ON con.predio = p.t_id
    LEFT JOIN unidades uni ON uni.predio = p.t_id
    JOIN lc_derecho der ON der.unidad_lc_predio = p.t_id
    JOIN lc_derechotipo tder ON tder.t_id = der.tipo
    LEFT JOIN cr_agrupacioninteresados ag ON ag.t_id = der.interesado_cr_agrupacioninteresados
    LEFT JOIN col_grupointeresadotipo ga ON ga.t_id = ag.tipo
    JOIN titulares tit ON tit.predio = p.t_id
    JOIN col_unidadfuente uf ON uf.unidad_lc_predio = p.t_id
    JOIN lc_fuenteadministrativa fa ON fa.t_id = uf.fuente_administrativa_lc_fuenteadministrativa
    JOIN col_fuenteadministrativatipo tf ON tf.t_id = fa.tipo
    JOIN col_estadodisponibilidadtipo ed ON ed.t_id = fa.estado_disponibilidad
    LEFT JOIN ci_forma_presentacion_codigo fp ON fp.t_id = fa.tipo_principal
)
SELECT row_to_json(fila) FROM fila ORDER BY id_predio;

COMMIT;
