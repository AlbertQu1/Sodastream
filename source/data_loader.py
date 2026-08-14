import pandas as pd
from sqlalchemy import create_engine
from config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD, CASA_LUGAR_UUID
from sqlalchemy import text


_engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}",
    connect_args={"options": "-c search_path=soda_stream"},
)


def _shots_to_intensidad(light: int, medium: int, strong: int) -> str:
    tokens = ["L"] * int(light) + ["M"] * int(medium) + ["S"] * int(strong)
    return ",".join(tokens) if tokens else "-"


def load_consumption() -> pd.DataFrame:
    legacy = pd.read_sql(
        """
        SELECT l.id AS "#", l.event_date AS fecha, c.label AS cilindro_id,
               COALESCE(l.flavor_id, 0) AS sabor_id, COALESCE(l.ml, 0) AS ml,
               l.bottles_prepared AS consumo, '-' AS intensidad
        FROM soda_legacy_consumption l
        JOIN soda_cylinders c ON c.id = l.cylinder_id
        """,
        _engine,
    )

    equipo_nuevo = pd.read_sql(
        """
        SELECT p.id AS "#", p.prepared_timestamp::date AS fecha, c.label AS cilindro_id,
               COALESCE(p.flavor_id, 0) AS sabor_id, COALESCE(p.ml, 0) AS ml,
               p.bottles_prepared AS consumo,
               p.shots_light, p.shots_medium, p.shots_strong
        FROM soda_preparations p
        JOIN soda_cylinders c ON c.id = p.cylinder_id
        """,
        _engine,
    )
    equipo_nuevo["intensidad"] = equipo_nuevo.apply(
        lambda r: _shots_to_intensidad(r["shots_light"], r["shots_medium"], r["shots_strong"]), axis=1
    )
    equipo_nuevo = equipo_nuevo.drop(columns=["shots_light", "shots_medium", "shots_strong"])

    # ids de legacy y de preparations pisan el mismo rango (1,2,3...) -- se
    # renumeran para que "#" siga siendo unico en todo el dataset combinado
    combinado = pd.concat([legacy, equipo_nuevo], ignore_index=True)
    combinado["#"] = range(1, len(combinado) + 1)
    return combinado


def load_refills() -> pd.DataFrame:
    return pd.read_sql('SELECT label AS "Tanque", price AS "Costo" FROM soda_cylinders', _engine)


def load_flavors() -> pd.DataFrame:
    df = pd.read_sql('SELECT id, flavor_name AS "Sabor" FROM soda_flavors ORDER BY id', _engine)
    natural = pd.DataFrame([{"id": 0, "Sabor": "Natural"}])
    return pd.concat([natural, df], ignore_index=True)


def load_market() -> pd.DataFrame:
    df = pd.read_sql('SELECT segment AS "Segmento", brand AS "Marca", year, price FROM soda_market_benchmarks', _engine)
    wide = df.pivot_table(index=["Segmento", "Marca"], columns="year", values="price").reset_index()
    wide.columns = [str(c) for c in wide.columns]  # pivot deja los anios como int; clean_market espera strings
    return wide


def load_flavor_history() -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT id, brand AS marca, flavor_name AS "Sabor", cost AS "Costo", ml, purchase_date AS fecha
        FROM soda_flavors
        WHERE always_available = false
        """,
        _engine,
    )


def load_all() -> dict:
    return {
        "consumption": load_consumption(),
        "refills": load_refills(),
        "flavors": load_flavors(),
        "market": load_market(),
        "flavor_history": load_flavor_history(),
    }
    
def soda_durante_partidas_casa(ventana_horas: int = 2) -> pd.DataFrame:
    """Preparaciones de soda con hora REAL (excluye timestamps sinteticos de
    mediodia que vienen de la migracion del sheet -- esos no reflejan la
    hora real en que se preparo la soda) que caen dentro de +-ventana_horas
    de una partida de board games jugada en 'Casa'. Cruce directo entre
    soda_stream y boardgames_stats, misma base 'casa'."""
    query = text("""
        SELECT sp.prepared_timestamp, sp.bottles_prepared,
               p.fecha AS partida_fecha, j.nombre AS juego
        FROM soda_stream.soda_preparations sp
        JOIN boardgames_stats.partidas p
          ON p.lugar_uuid = :lugar_casa
         AND sp.prepared_timestamp BETWEEN p.fecha - make_interval(hours => :ventana)
                                        AND p.fecha + make_interval(hours => :ventana)
        JOIN boardgames_stats.juegos j ON j.uuid = p.juego_uuid
        WHERE sp.prepared_timestamp::time <> '12:00:00'
        ORDER BY sp.prepared_timestamp
    """)
    with _engine.connect() as conn:
        return pd.read_sql(query, conn, params={"lugar_casa": CASA_LUGAR_UUID, "ventana": ventana_horas})