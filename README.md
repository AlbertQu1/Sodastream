# Gasificador — Análisis de ROI y consumo

Tracking de consumo de agua gasificada casera: costo por litro, ahorro vs. precio de mercado de referencia, y retorno de inversión (ROI) del equipo, con soporte para jarabes/sabores.

## Estado del proyecto

🚧 En reescritura. La lógica de negocio se validó en iteraciones previas, pero el script se está construyendo desde cero con un diseño más sólido antes de subir código a este repo.

Requiere un `.env` con tus credenciales (ver `.env.example`).

## Modelo de datos

El proyecto parte de una base de datos en Google Sheets con estas tablas:

- **Consumo** — log diario: fecha, consumo, sabor_id, ml, cilindro_id
- **Recargas** — costo de cada cilindro al recargarse (incluye cilindros con costo $0, los incluidos con el equipo)
- **Sabor_id** — catálogo de sabores, incluye `0 = agua natural` como categoría base
- **Sabor_historico** — compras de jarabes: fecha, costo, tamaño
- **Precios** — benchmark externo de mercado por segmento, actualizable año con año
- **Equipos** *(pendiente de agregar)* — costo de equipo(s), fecha de compra/venta

## Estructura del repo

```
.
├── README.md
├── .env.example
├── .gitignore
└── src/              # script(s) activos, en construcción
```