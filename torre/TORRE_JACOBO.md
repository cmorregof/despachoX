# Torre de control · Jacobo · rol C (tablero)
Última actualización: 2026-11-20 14:05 (hora de Colombia)

## Estado en una frase
Entorno listo y primera versión del tablero (mapa + «Por revisar») corriendo con la semilla de Carlos.

## Hecho (con el commit o archivo que lo prueba)
- Repositorio clonado en `C:\Users\Jacobo\despachoX`.
- `.env` creado desde `.env.example` (sin valores).
- `.venv` con Python 3.12 y `requirements.txt` instalado (70 paquetes).
- Grafo de Manizales en `despacho/cache/` (6395 nodos) y semilla cargada (15 puntos, 2 acopios, 5 vehículos, 34 lotes, 20 pedidos).
- `tablero/app.py`: mapa con acopios, puntos críticos, pedidos, cierres y rutas; columna «Por revisar» con Confirmar, Descartar y Levantar, cada acción anotada en la bitácora.

## En curso (qué, hasta dónde llegó, qué falta)
- Paso 3 del encargo: bloque «Plan» (Calcular, tabla por vehículo, Aprobar y Rechazar, aviso de recálculo).

## Siguiente paso exacto (el comando o el archivo por donde seguir)
Agregar el bloque «Plan» a `tablero/app.py`, llamando `python -m despacho.optimizar` con subprocess.

## Decisiones y por qué
- Python 3.12 para el `.venv`, igual que B-despacho (OR-Tools y osmnx pueden no tener paquetes para 3.15).
- No se crea `tablero/datos_falsos.py`: la semilla de Carlos ya está en `main` (canal, 11:36).

## Bloqueos y preguntas para el capitán

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (solo PowerShell)
- `.venv\Scripts\activate`
- `python -m despacho.red` y `python -m despacho.semilla --cargar --reiniciar` (la primera vez)
- `streamlit run tablero/app.py`
- El tablero no usa claves de `.env`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2 (prototipo): pantalla de la demo.
- Criterio 5 (viabilidad): se ve que el despachador humano aprueba cada plan.
