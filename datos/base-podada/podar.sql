-- Poda de la base catastral LADM-COL: deja las tablas con datos y las que estas necesitan.
--
-- Se ejecuta con psql sobre una COPIA de la base original, nunca sobre la original:
--
--     psql -d catastro_pruned -f datos/base-podada/podar.sql
--
-- Todo ocurre en una sola transacción: si una comprobación falla, la base queda como estaba.
--
--   1. Comprueba que la base es la esperada y que nada de lo que va a eliminar tiene datos.
--   2. Elimina las 34 columnas que apuntan a tablas vacías (todas están en NULL).
--   3. Elimina 172 tablas: 117 vacías, 47 dominios que ya nadie referencia
--      y 8 tablas de metadatos de ili2db.
--   4. Comprueba que quedan las 45 tablas y las 77 llaves foráneas documentadas.
--
-- El criterio de poda, el resultado y los pasos para crear la copia están en README.md,
-- en esta misma carpeta. El diccionario de datos de lo que queda está en diccionario-de-datos.md.

\set ON_ERROR_STOP on

BEGIN;

-- La base original no se modifica
DO $$
BEGIN
    IF current_database() = 'xtf2' THEN
        RAISE EXCEPTION 'Esta es la base original (%). El script se ejecuta sobre una copia.', current_database();
    END IF;
END $$;

-- ---------------------------------------------------------------------------------------------
-- Qué se elimina y qué se conserva
-- ---------------------------------------------------------------------------------------------

-- Tablas que se eliminan y por qué:
--   vacia            no tiene ninguna fila
--   dominio_sin_uso  lista de valores que solo usaban tablas vacías
--   metadatos        catálogo de ili2db: describe las 217 tablas del modelo completo
CREATE TEMP TABLE poda_tablas (tabla text PRIMARY KEY, motivo text NOT NULL) ON COMMIT DROP;

INSERT INTO poda_tablas (tabla, motivo) VALUES
    ('cc_barrio', 'vacia'), ('cc_centropoblado', 'vacia'), ('cc_corregimiento', 'vacia'),
    ('cc_limitemunicipio', 'vacia'), ('cc_localidadcomuna', 'vacia'), ('cc_manzana', 'vacia'),
    ('cc_metodooperacion', 'vacia'), ('cc_nomenclaturavial', 'vacia'), ('cc_perimetrourbano', 'vacia'),
    ('cc_sectorrural', 'vacia'), ('cc_sectorurbano', 'vacia'), ('cc_vereda', 'vacia'),
    ('col_areavalor', 'vacia'), ('col_baunitfuente', 'vacia'), ('col_clfuente', 'vacia'),
    ('col_masccl', 'vacia'), ('col_mascl', 'vacia'), ('col_menosccl', 'vacia'), ('col_menoscl', 'vacia'),
    ('col_puntoccl', 'vacia'), ('col_puntocl', 'vacia'), ('col_relacionfuente', 'vacia'),
    ('col_relacionfuenteuespacial', 'vacia'), ('col_transformacion', 'vacia'), ('col_uefuente', 'vacia'),
    ('col_ueuegrupo', 'vacia'), ('col_volumenvalor', 'vacia'), ('cr_fuenteespacial', 'vacia'),
    ('cr_lindero', 'vacia'), ('cr_puntocontrol', 'vacia'), ('cr_puntolindero', 'vacia'),
    ('extarchivo', 'vacia'), ('extinteresado', 'vacia'), ('extredserviciosfisica', 'vacia'),
    ('extreferenciaregistralsistemaantiguo', 'vacia'), ('extunidadedificacionfisica', 'vacia'),
    ('fraccion', 'vacia'), ('gc_barrio', 'vacia'), ('gc_calificacionunidadconstruccion', 'vacia'),
    ('gc_comisionesconstruccion', 'vacia'), ('gc_comisionesterreno', 'vacia'),
    ('gc_comisionesunidadconstruccion', 'vacia'), ('gc_construccion', 'vacia'),
    ('gc_copropiedad', 'vacia'), ('gc_datosphcondominio', 'vacia'), ('gc_datostorreph', 'vacia'),
    ('gc_direccion', 'vacia'), ('gc_estadopredio', 'vacia'), ('gc_manzana', 'vacia'),
    ('gc_perimetro', 'vacia'), ('gc_prediocatastro', 'vacia'), ('gc_propietario', 'vacia'),
    ('gc_sectorrural', 'vacia'), ('gc_sectorurbano', 'vacia'), ('gc_terreno', 'vacia'),
    ('gc_unidadconstruccion', 'vacia'), ('gc_vereda', 'vacia'), ('gm_curve2dlistvalue', 'vacia'),
    ('gm_curve3dlistvalue', 'vacia'), ('gm_geometry2dlistvalue', 'vacia'), ('gm_multicurve2d', 'vacia'),
    ('gm_multicurve3d', 'vacia'), ('gm_multisurface2d', 'vacia'), ('gm_multisurface3d', 'vacia'),
    ('gm_surface2dlistvalue', 'vacia'), ('gm_surface3dlistvalue', 'vacia'), ('imagen', 'vacia'),
    ('ini_predioinsumos', 'vacia'), ('lc_interesadocontacto', 'vacia'), ('lc_novedadfmi', 'vacia'),
    ('lc_nu_agrupacionunidadesespaciales', 'vacia'), ('lc_nu_caraslindero', 'vacia'),
    ('lc_nu_espaciojuridicoredservicios', 'vacia'), ('lc_nu_espaciojuridicounidadedificacion', 'vacia'),
    ('lc_nu_nivel', 'vacia'), ('lc_nu_relacionnecesariabaunits', 'vacia'),
    ('lc_nu_relacionnecesariaunidadesespaciales', 'vacia'), ('lc_predio_ini_predioinsumos', 'vacia'),
    ('ric_agrupacioninteresados', 'vacia'), ('ric_caracteristicasunidadconstruccion', 'vacia'),
    ('ric_construccion', 'vacia'), ('ric_datosphcondominio', 'vacia'), ('ric_derecho', 'vacia'),
    ('ric_fuenteadministrativa', 'vacia'), ('ric_fuenteespacial', 'vacia'),
    ('ric_gestorcatastral', 'vacia'), ('ric_interesado', 'vacia'),
    ('ric_nu_agrupacionunidadesespaciales', 'vacia'), ('ric_nu_cadenacaraslimite', 'vacia'),
    ('ric_nu_caraslindero', 'vacia'), ('ric_nu_espaciojuridicoredservicios', 'vacia'),
    ('ric_nu_espaciojuridicounidadedificacion', 'vacia'), ('ric_nu_nivel', 'vacia'),
    ('ric_nu_punto', 'vacia'), ('ric_nu_relacionnecesariabaunits', 'vacia'),
    ('ric_nu_relacionnecesariaunidadesespaciales', 'vacia'), ('ric_operadorcatastral', 'vacia'),
    ('ric_predio', 'vacia'), ('ric_predio_copropiedad', 'vacia'), ('ric_predio_informalidad', 'vacia'),
    ('ric_predio_tramitecatastral', 'vacia'), ('ric_terreno', 'vacia'),
    ('ric_tramitecatastral', 'vacia'), ('ric_unidadconstruccion', 'vacia'), ('snr_anotacion', 'vacia'),
    ('snr_derecho', 'vacia'), ('snr_estructuramatriculamatriz', 'vacia'),
    ('snr_fuentecabidalinderos', 'vacia'), ('snr_fuentederecho', 'vacia'),
    ('snr_predioregistro', 'vacia'), ('snr_publicidad', 'vacia'), ('snr_publicidad_titular', 'vacia'),
    ('snr_restriccion', 'vacia'), ('snr_restriccion_titular', 'vacia'), ('snr_rol_persona', 'vacia'),
    ('snr_titular', 'vacia'), ('snr_titular_derecho', 'vacia');

INSERT INTO poda_tablas (tabla, motivo) VALUES
    ('cc_nomenclaturavial_tipo_via', 'dominio_sin_uso'), ('col_areatipo', 'dominio_sin_uso'),
    ('col_contenidoniveltipo', 'dominio_sin_uso'), ('col_estadoredserviciostipo', 'dominio_sin_uso'),
    ('col_estructuratipo', 'dominio_sin_uso'), ('col_fuenteespacialtipo', 'dominio_sin_uso'),
    ('col_interpolaciontipo', 'dominio_sin_uso'), ('col_iso19125_tipo', 'dominio_sin_uso'),
    ('col_metodoproducciontipo', 'dominio_sin_uso'), ('col_puntotipo', 'dominio_sin_uso'),
    ('col_redserviciostipo', 'dominio_sin_uso'), ('col_registrotipo', 'dominio_sin_uso'),
    ('col_unidadedificaciontipo', 'dominio_sin_uso'), ('col_volumentipo', 'dominio_sin_uso'),
    ('cr_fotoidentificaciontipo', 'dominio_sin_uso'), ('cr_puntocontroltipo', 'dominio_sin_uso'),
    ('extreferenciaregistralsistemaantiguo_tipo_referencia', 'dominio_sin_uso'),
    ('gc_condicionprediotipo', 'dominio_sin_uso'), ('gc_sistemaprocedenciadatostipo', 'dominio_sin_uso'),
    ('gc_unidadconstrucciontipo', 'dominio_sin_uso'), ('ini_emparejamientotipo', 'dominio_sin_uso'),
    ('lc_novedadfmi_tipo_novedadfmi', 'dominio_sin_uso'), ('ric_catastrotipo', 'dominio_sin_uso'),
    ('ric_condicionprediotipo', 'dominio_sin_uso'), ('ric_construcciontipo', 'dominio_sin_uso'),
    ('ric_derechotipo', 'dominio_sin_uso'), ('ric_destinacioneconomicatipo', 'dominio_sin_uso'),
    ('ric_dominioconstrucciontipo', 'dominio_sin_uso'), ('ric_estadociviltipo', 'dominio_sin_uso'),
    ('ric_estadotipo', 'dominio_sin_uso'), ('ric_grupoetnicotipo', 'dominio_sin_uso'),
    ('ric_interesadodocumentotipo', 'dominio_sin_uso'), ('ric_interesadotipo', 'dominio_sin_uso'),
    ('ric_mutaciontipo', 'dominio_sin_uso'), ('ric_sexotipo', 'dominio_sin_uso'),
    ('ric_unidadconstrucciontipo', 'dominio_sin_uso'), ('ric_usouconstipo', 'dominio_sin_uso'),
    ('ric_zonatipo', 'dominio_sin_uso'), ('snr_calidadderechotipo', 'dominio_sin_uso'),
    ('snr_clasepredioregistrotipo', 'dominio_sin_uso'), ('snr_documentotitulartipo', 'dominio_sin_uso'),
    ('snr_estadofmitipo', 'dominio_sin_uso'), ('snr_fuentetipo', 'dominio_sin_uso'),
    ('snr_personatitulartipo', 'dominio_sin_uso'), ('snr_publicidadtipo', 'dominio_sin_uso'),
    ('snr_restricciontipo', 'dominio_sin_uso'), ('snr_rolpersonatipo', 'dominio_sin_uso');

-- Para conservar los metadatos de ili2db basta con quitar este INSERT y pasar sus ocho
-- tablas a poda_conservadas.
INSERT INTO poda_tablas (tabla, motivo) VALUES
    ('t_ili2db_attrname', 'metadatos'), ('t_ili2db_classname', 'metadatos'),
    ('t_ili2db_column_prop', 'metadatos'), ('t_ili2db_inheritance', 'metadatos'),
    ('t_ili2db_model', 'metadatos'), ('t_ili2db_settings', 'metadatos'),
    ('t_ili2db_table_prop', 'metadatos'), ('t_ili2db_trafo', 'metadatos');

-- Columnas de las tablas que se conservan cuya llave foránea apunta a una tabla vacía
CREATE TEMP TABLE poda_columnas (tabla text, columna text, PRIMARY KEY (tabla, columna)) ON COMMIT DROP;

INSERT INTO poda_columnas (tabla, columna) VALUES
    ('col_miembros', 'interesado_ric_interesado'),
    ('col_miembros', 'interesado_ric_agrupacioninteresados'),
    ('col_miembros', 'agrupacion_ric_agrupacioninteresados'),
    ('col_rrrfuente', 'fuente_administrativa_ric_fuenteadministrativa'),
    ('col_rrrfuente', 'rrr_ric_derecho'), ('col_uebaunit', 'ue_ric_unidadconstruccion'),
    ('col_uebaunit', 'ue_ric_terreno'), ('col_uebaunit', 'ue_ric_construccion'),
    ('col_uebaunit', 'ue_ric_nu_espaciojuridicounidadedificacion'),
    ('col_uebaunit', 'ue_lc_nu_espaciojuridicounidadedificacion'),
    ('col_uebaunit', 'ue_ric_nu_espaciojuridicoredservicios'),
    ('col_uebaunit', 'ue_lc_nu_espaciojuridicoredservicios'), ('col_uebaunit', 'baunit_ric_predio'),
    ('col_unidadfuente', 'fuente_administrativa_ric_fuenteadministrativa'),
    ('col_unidadfuente', 'unidad_ric_predio'), ('cr_construccion', 'nivel_lc_nu_nivel'),
    ('cr_construccion', 'nivel_ric_nu_nivel'), ('cr_terreno', 'nivel_lc_nu_nivel'),
    ('cr_terreno', 'nivel_ric_nu_nivel'), ('cr_unidadconstruccion', 'nivel_lc_nu_nivel'),
    ('cr_unidadconstruccion', 'nivel_ric_nu_nivel'),
    ('extdireccion', 'extunidadedificcnfsica_ext_direccion_id'),
    ('extdireccion', 'extinteresado_ext_direccion_id'),
    ('extdireccion', 'ric_construccion_ext_direccion_id'),
    ('extdireccion', 'ric_n_spcjrdcrdsrvcios_ext_direccion_id'),
    ('extdireccion', 'ric_n_spcjrcndddfccion_ext_direccion_id'),
    ('extdireccion', 'ric_predio_direccion'), ('extdireccion', 'ric_terreno_ext_direccion_id'),
    ('extdireccion', 'ric_unidadconstruccion_ext_direccion_id'),
    ('extdireccion', 'lc_nu_spcjrdcrdsrvcios_ext_direccion_id'),
    ('extdireccion', 'lc_n_spcjrdcndddfccion_ext_direccion_id'),
    ('lc_derecho', 'interesado_ric_interesado'), ('lc_derecho', 'interesado_ric_agrupacioninteresados'),
    ('lc_derecho', 'unidad_ric_predio');

-- Tablas que deben quedar: 20 de datos, 23 dominios y 2 de la carga
CREATE TEMP TABLE poda_conservadas (tabla text PRIMARY KEY) ON COMMIT DROP;

INSERT INTO poda_conservadas (tabla) VALUES
    ('col_miembros'), ('col_rrrfuente'), ('col_uebaunit'), ('col_unidadfuente'),
    ('cr_agrupacioninteresados'), ('cr_caracteristicasunidadconstruccion'), ('cr_construccion'),
    ('cr_datosphcondominio'), ('cr_interesado'), ('cr_predio_copropiedad'), ('cr_terreno'),
    ('cr_unidadconstruccion'), ('extdireccion'), ('lc_contactovisita'),
    ('lc_datosadicionaleslevantamientocatastral'), ('lc_derecho'), ('lc_estructuranovedadnumeropredial'),
    ('lc_fuenteadministrativa'), ('lc_predio'), ('lc_predio_informalidad');

INSERT INTO poda_conservadas (tabla) VALUES
    ('ci_forma_presentacion_codigo'), ('col_dimensiontipo'), ('col_estadodisponibilidadtipo'),
    ('col_fuenteadministrativatipo'), ('col_grupointeresadotipo'), ('col_relacionsuperficietipo'),
    ('col_unidadadministrativabasicatipo'), ('cr_construccionplantatipo'), ('cr_documentotipo'),
    ('cr_grupoetnicotipo'), ('cr_interesadotipo'), ('cr_sexotipo'), ('cr_unidadconstrucciontipo'),
    ('cr_usouconstipo'), ('extdireccion_clase_via_principal'), ('extdireccion_sector_ciudad'),
    ('extdireccion_sector_predio'), ('extdireccion_tipo_direccion'), ('lc_condicionprediotipo'),
    ('lc_derechotipo'), ('lc_destinacioneconomicatipo'),
    ('lc_estructuranovedadnumeropredial_tipo_novedad'), ('lc_resultadovisitatipo');

INSERT INTO poda_conservadas (tabla) VALUES
    ('t_ili2db_basket'), ('t_ili2db_dataset');

-- ---------------------------------------------------------------------------------------------
-- 1. Comprobaciones previas
-- ---------------------------------------------------------------------------------------------
DO $$
DECLARE
    r record;
    hay boolean;
    nombres text;
BEGIN
    SELECT string_agg(t.tablename, ', ' ORDER BY t.tablename) INTO nombres
    FROM pg_tables t
    WHERE t.schemaname = 'xtf'
      AND t.tablename NOT IN (SELECT tabla FROM poda_tablas UNION ALL SELECT tabla FROM poda_conservadas);
    IF nombres IS NOT NULL THEN
        RAISE EXCEPTION 'El esquema xtf tiene tablas que este script no conoce: %', nombres;
    END IF;

    SELECT string_agg(p.tabla, ', ' ORDER BY p.tabla) INTO nombres
    FROM (SELECT tabla FROM poda_tablas UNION ALL SELECT tabla FROM poda_conservadas) p
    WHERE NOT EXISTS (SELECT 1 FROM pg_tables t WHERE t.schemaname = 'xtf' AND t.tablename = p.tabla);
    IF nombres IS NOT NULL THEN
        RAISE EXCEPTION 'Faltan en el esquema xtf tablas que este script espera: %', nombres;
    END IF;

    FOR r IN SELECT tabla FROM poda_tablas WHERE motivo = 'vacia' ORDER BY tabla LOOP
        EXECUTE format('SELECT EXISTS (SELECT 1 FROM xtf.%I)', r.tabla) INTO hay;
        IF hay THEN
            RAISE EXCEPTION 'La tabla xtf.% tiene filas, pero el script la da por vacía.', r.tabla;
        END IF;
    END LOOP;

    FOR r IN SELECT tabla, columna FROM poda_columnas ORDER BY tabla, columna LOOP
        EXECUTE format('SELECT EXISTS (SELECT 1 FROM xtf.%I WHERE %I IS NOT NULL)', r.tabla, r.columna) INTO hay;
        IF hay THEN
            RAISE EXCEPTION 'La columna xtf.%.% tiene valores, pero el script la da por vacía.', r.tabla, r.columna;
        END IF;
    END LOOP;
END $$;

-- ---------------------------------------------------------------------------------------------
-- 2. Columnas que apuntan a tablas vacías
--    Al eliminar la columna se van con ella su llave foránea y su índice.
-- ---------------------------------------------------------------------------------------------
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT tabla, string_agg(format('DROP COLUMN %I', columna), ', ' ORDER BY columna) AS acciones
        FROM poda_columnas
        GROUP BY tabla
        ORDER BY tabla
    LOOP
        EXECUTE format('ALTER TABLE xtf.%I %s', r.tabla, r.acciones);
    END LOOP;
END $$;

-- ---------------------------------------------------------------------------------------------
-- 3. Tablas
--    Sin CASCADE a propósito: si alguna tabla que se conserva dependiera todavía de una que
--    se elimina, PostgreSQL se niega y la transacción se deshace.
-- ---------------------------------------------------------------------------------------------
DO $$
DECLARE
    m text;
    lista text;
BEGIN
    FOREACH m IN ARRAY ARRAY['vacia', 'dominio_sin_uso', 'metadatos'] LOOP
        SELECT string_agg(format('xtf.%I', tabla), ', ' ORDER BY tabla) INTO lista
        FROM poda_tablas
        WHERE motivo = m;
        IF lista IS NOT NULL THEN
            EXECUTE 'DROP TABLE ' || lista;
        END IF;
    END LOOP;
END $$;

-- ---------------------------------------------------------------------------------------------
-- 4. Comprobaciones finales
-- ---------------------------------------------------------------------------------------------
DO $$
DECLARE
    r record;
    hay boolean;
    n_tablas integer;
    n_fks integer;
BEGIN
    SELECT count(*) INTO n_tablas FROM pg_tables WHERE schemaname = 'xtf';
    IF n_tablas <> (SELECT count(*) FROM poda_conservadas) THEN
        RAISE EXCEPTION 'Quedaron % tablas en el esquema xtf y se esperaban %.',
            n_tablas, (SELECT count(*) FROM poda_conservadas);
    END IF;

    SELECT count(*) INTO n_fks
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE n.nspname = 'xtf' AND c.contype = 'f';
    IF n_fks <> 77 THEN
        RAISE EXCEPTION 'Quedaron % llaves foráneas en el esquema xtf y se esperaban 77.', n_fks;
    END IF;

    FOR r IN SELECT tabla FROM poda_conservadas ORDER BY tabla LOOP
        EXECUTE format('SELECT EXISTS (SELECT 1 FROM xtf.%I)', r.tabla) INTO hay;
        IF NOT hay THEN
            RAISE WARNING 'La tabla xtf.% se conservó, pero está vacía.', r.tabla;
        END IF;
    END LOOP;

    RAISE NOTICE 'Poda terminada: quedan % tablas y % llaves foráneas en el esquema xtf.', n_tablas, n_fks;
END $$;

COMMIT;

-- Recupera el espacio de las columnas eliminadas y actualiza las estadísticas
VACUUM (FULL, ANALYZE);
