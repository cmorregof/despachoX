# datos/

`esquema.sql` es el contrato entre los tres módulos. Para crear la base local:

```
sqlite3 datos/despachox.db < datos/esquema.sql
```

`despachox.db` no se sube al repositorio. Los datos de prueba (puntos, acopios, lotes, vehículos) van en `datos/semilla/` como CSV, todos sintéticos.
