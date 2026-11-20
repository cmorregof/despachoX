-- DespachoX · contrato de datos (SQLite). Archivo de trabajo: datos/despachox.db (no se sube).
-- Los tres módulos solo se hablan a través de estas tablas:
--   entrada/  escribe pedidos y cierres
--   despacho/ lee pedidos, lotes, vehiculos, cierres y escribe planes y paradas
--   tablero/  lee todo y cambia estados (confirmar, aprobar, entregar)
-- Si necesitas cambiar una tabla, avisa por el grupo antes de hacerlo.

CREATE TABLE IF NOT EXISTS puntos (        -- puntos de entrega (barrio, albergue, comedor)
  id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, barrio TEXT, comuna TEXT,
  lat REAL NOT NULL, lon REAL NOT NULL,
  critico INTEGER DEFAULT 0                -- 1 = punto crítico (cuenta para el indicador)
);
CREATE TABLE IF NOT EXISTS acopios (       -- centros de acopio / bodegas
  id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, lat REAL NOT NULL, lon REAL NOT NULL,
  tiene_frio INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS lotes (         -- inventario por lote
  id INTEGER PRIMARY KEY, acopio_id INTEGER REFERENCES acopios(id),
  producto TEXT NOT NULL, kg REAL NOT NULL,
  perecedero INTEGER DEFAULT 0, vence_en TEXT,      -- ISO 8601; NULL si no vence pronto
  empaque_activo INTEGER DEFAULT 0                  -- supuesto: alarga vida útil (patente UNAL)
);
CREATE TABLE IF NOT EXISTS vehiculos (
  id INTEGER PRIMARY KEY, nombre TEXT,
  tipo TEXT CHECK(tipo IN ('camion','campero','moto','a_pie')) NOT NULL,
  capacidad_kg REAL NOT NULL, acopio_id INTEGER REFERENCES acopios(id),
  lat REAL, lon REAL,                                -- posición actual (para recalcular)
  estado TEXT DEFAULT 'libre' CHECK(estado IN ('libre','en_ruta','fuera'))
);
CREATE TABLE IF NOT EXISTS pedidos (       -- lo que escribe entrada/
  id INTEGER PRIMARY KEY, creado_en TEXT NOT NULL,
  punto_id INTEGER REFERENCES puntos(id),
  familias INTEGER, kg_estimado REAL,
  productos TEXT,                          -- JSON: [{"producto":"arroz","kg":20}, ...]
  urgencia INTEGER DEFAULT 2 CHECK(urgencia BETWEEN 1 AND 3),   -- 3 = más urgente
  limite_en TEXT,                          -- hora tope de entrega (ISO 8601)
  estado TEXT DEFAULT 'nuevo' CHECK(estado IN ('nuevo','confirmado','asignado','entregado','descartado')),
  duplicado_de INTEGER REFERENCES pedidos(id),
  texto_original TEXT,                     -- sin nombres ni teléfonos
  remitente_hash TEXT                      -- hash del chat, nunca el id en claro
);
CREATE TABLE IF NOT EXISTS cierres (       -- vías bloqueadas, lo que escribe entrada/
  id INTEGER PRIMARY KEY, creado_en TEXT NOT NULL,
  descripcion TEXT, lugar TEXT, lat REAL, lon REAL,
  osm_u INTEGER, osm_v INTEGER,            -- arista del grafo de osmnx (la llena despacho/)
  tipos_bloqueados TEXT DEFAULT '["camion","campero","moto"]',  -- JSON
  estado TEXT DEFAULT 'reportado' CHECK(estado IN ('reportado','confirmado','levantado')),
  texto_original TEXT
);
CREATE TABLE IF NOT EXISTS planes (        -- lo que escribe despacho/
  id INTEGER PRIMARY KEY, creado_en TEXT NOT NULL,
  motivo TEXT,                             -- 'inicial', 'cierre 12', 'pedido nuevo'
  estado TEXT DEFAULT 'propuesto' CHECK(estado IN ('propuesto','aprobado','rechazado','reemplazado')),
  aprobado_por TEXT, aprobado_en TEXT,
  segundos_calculo REAL, resumen TEXT      -- JSON con métricas del plan
);
CREATE TABLE IF NOT EXISTS paradas (
  id INTEGER PRIMARY KEY, plan_id INTEGER REFERENCES planes(id),
  vehiculo_id INTEGER REFERENCES vehiculos(id), orden INTEGER NOT NULL,
  punto_id INTEGER REFERENCES puntos(id), pedido_id INTEGER REFERENCES pedidos(id),
  llegada_estimada TEXT, kg REAL,
  geometria TEXT                           -- JSON: [[lat,lon],...] del tramo hasta esta parada
);
CREATE TABLE IF NOT EXISTS paquetes (      -- trazabilidad; codigo = contenido del QR
  codigo TEXT PRIMARY KEY, pedido_id INTEGER REFERENCES pedidos(id),
  lote_id INTEGER REFERENCES lotes(id), kg REAL,
  estado TEXT DEFAULT 'en_bodega' CHECK(estado IN ('en_bodega','en_ruta','entregado','perdido')),
  entregado_en TEXT
);
CREATE TABLE IF NOT EXISTS bitacora (      -- quién decidió qué
  id INTEGER PRIMARY KEY, cuando TEXT NOT NULL, quien TEXT, accion TEXT, detalle TEXT
);
