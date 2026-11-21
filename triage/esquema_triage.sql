-- DespachoX · triage de solicitudes. Tablas nuevas; no toca las de datos/esquema.sql.
CREATE TABLE IF NOT EXISTS zonas (
  id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
  tipo TEXT NOT NULL DEFAULT 'barrio' CHECK(tipo IN ('barrio','vereda','albergue')),
  comuna TEXT, lat REAL NOT NULL, lon REAL NOT NULL, geom_wkt TEXT, area_km2 REAL,
  personas INTEGER, hogares INTEGER, tamano_hogar REAL, afectacion REAL, ocupacion INTEGER,
  critico INTEGER DEFAULT 0,
  calidad_dato TEXT DEFAULT 'fuente' CHECK(calidad_dato IN ('fuente','estimado')),
  fuente TEXT, fecha_corte TEXT,
  es_debil INTEGER DEFAULT 0, aislada INTEGER DEFAULT 0,
  lambda_h REAL, rafaga_hasta TEXT
);
CREATE TABLE IF NOT EXISTS remitentes (
  remitente_hash TEXT PRIMARY KEY,
  rol TEXT NOT NULL DEFAULT 'ciudadano' CHECK(rol IN ('ciudadano','lider','agente')),
  zonas TEXT DEFAULT '[]', organizacion TEXT, primer_contacto TEXT,
  estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo','suspendido','bloqueado')),
  auditorias_fallidas INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tareas_campo (
  id INTEGER PRIMARY KEY, zona_id INTEGER REFERENCES zonas(id),
  creada_en TEXT NOT NULL, motivo TEXT, prioridad REAL,
  agente_hash TEXT REFERENCES remitentes(remitente_hash),
  estado TEXT NOT NULL DEFAULT 'abierta'
    CHECK(estado IN ('abierta','asignada','validada','escalada','cerrada')),
  cerrada_en TEXT
);
CREATE TABLE IF NOT EXISTS solicitudes (
  id INTEGER PRIMARY KEY, recibida_en TEXT NOT NULL,
  hash_mensaje TEXT UNIQUE NOT NULL, remitente_hash TEXT NOT NULL,
  canal TEXT NOT NULL DEFAULT 'chat' CHECK(canal IN ('chat','agente','manual')),
  texto TEXT, zona_id INTEGER REFERENCES zonas(id), lat REAL, lon REAL,
  tipo_punto TEXT, productos TEXT DEFAULT '[]',
  familias_declaradas INTEGER, familias_efectivas INTEGER,
  lugar_confirmado INTEGER DEFAULT 0,
  estado TEXT NOT NULL DEFAULT 'recibida' CHECK(estado IN
    ('recibida','cuarentena','espera_agente','consolidada','confirmada_regla','en_cola','confirmada','descartada')),
  motivo_cuarentena TEXT, marcas TEXT DEFAULT '[]', senales TEXT DEFAULT '{}',
  p_real REAL, cluster_id INTEGER, consolidada_en INTEGER REFERENCES solicitudes(id),
  pedido_id INTEGER REFERENCES pedidos(id), tarea_id INTEGER REFERENCES tareas_campo(id)
);
CREATE TABLE IF NOT EXISTS parametros (
  version INTEGER PRIMARY KEY, creada_en TEXT NOT NULL,
  aprobada_por TEXT, aplicada INTEGER DEFAULT 0, valores TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sol_zona_t ON solicitudes(zona_id, recibida_en);
CREATE INDEX IF NOT EXISTS ix_sol_rem_t ON solicitudes(remitente_hash, recibida_en);
CREATE INDEX IF NOT EXISTS ix_sol_estado ON solicitudes(estado);
