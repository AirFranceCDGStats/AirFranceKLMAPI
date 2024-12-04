from AirPy.client import AirPyClient
from sanic import Sanic, Request
from sanic_ext import openapi
from .config import AppConfig
from .routes.service.service import bp as RouteService
from .routes.aeroports.aeroports import bp as RouteAeroports
from .routes.vols.vols import bp as RouteVols
from .routes.planes.planes import bp as RoutePlanes
from .routes.compagnies.compagnies import bp as RouteCompagnies
from .routes.public.public import bp as RoutePublic
from .routes.websocket.websocket import bp as RouteWebsocket
from .utils.logger import Logger
from .utils.cache import Cache
from dotenv import load_dotenv
from os import environ
from aiohttp import ClientSession
from apscheduler.triggers.interval import IntervalTrigger
from textwrap import dedent
from asyncpg import create_pool
from datetime import datetime


load_dotenv(dotenv_path=f".env")


# Initialisation de l'application
app = Sanic(
    name="AirFranceKLMAPI",
    config=AppConfig(),
)


# Ajoute les statistiques Prometheus
PrometheusStatistics(app)


# Ajoute des informations à la documentation OpenAPI
app.ext.openapi.raw(
    {
        "servers": [
            {
                "url": f"{environ.get('API_DOMAIN')}",
                "description": "Serveur de production"
            }
        ],
    }
)

app.ext.openapi.describe(
    title=app.name,
    version=f"v{app.config.API_VERSION}",
    description=dedent(
        """
            ![banner](/static/images/banner.png)
            # Introduction
            Documentation de l'API de cache de l'API officielle d'Air France KLM.
            <br>
            <br>
            API réalisée dans le cadre d'une SAE (Situation d'Apprentissage Évaluée) à l'IUT de Reims.
            <br>
            <br>
            ## Crédits
            - Nathan Eullaffroy
            - Lucas Debeve
            - Paul Bayfield
            <br>
            <br>
            <br>

            *[Voir l'API officielle d'AirFranceKLM](https://developer.airfranceklm.com)*
        """
    ),
)

app.static("/static", "./static")


# Enregistrement des routes
app.blueprint(RouteService)
app.blueprint(RouteAeroports)
app.blueprint(RouteVols)
app.blueprint(RouteCompagnies)
app.blueprint(RoutePlanes)
app.blueprint(RoutePublic)
app.blueprint(RouteWebsocket)
openapi.exclude(bp=RouteWebsocket)


@app.listener("before_server_start")
async def setup_app(app: Sanic, loop):
    app.ctx.logs = Logger("logs")
    app.ctx.requests = Logger("web")
    app.ctx.session = ClientSession()

    # Chargement des clients
    app.ctx.clients = []
    for key in environ.keys():
        if key.startswith("AIRFRANCEKLM_API_KEY_"):
            app.ctx.clients.append(AirPyClient(environ.get(key), app.ctx.session))
            app.ctx.logs.info(f"[ENV] Client : {key} chargé !")

    app.ctx.logs.info(f"{len(app.ctx.clients)} Clients chargés !")

    # Chargement de la base de données
    try:
        app.ctx.pool = await create_pool(
            user=environ.get("POSTGRES_USER"),
            password=environ.get("POSTGRES_PASSWORD"),
            database=environ.get("POSTGRES_DB"),
            host=environ.get("POSTGRES_HOST", "localhost"),
            port=int(environ.get("POSTGRES_PORT", 5432)),
            loop=loop
        )
    except OSError:
        app.ctx.logs.error("Impossible de se connecter à la base de données !")
        app.ctx.logs.debug("Arrêt de l'API !")
        exit(1)


    # Chargement du cache
    app.ctx.cache = Cache(
        clients=app.ctx.clients,
        logs=app.ctx.logs,
        pool=app.ctx.pool
    )
    await app.ctx.cache.loadCache()

    app.ctx.cache.add_job(app.ctx.cache.refreshFlights, IntervalTrigger(seconds=int(environ.get("CACHE", 1880))), id="cache")
    app.ctx.cache.start()

    await app.ctx.cache.refreshFlights()

    if environ.get("HISTORICAL", "false").lower() == "true":
        await app.ctx.cache.historicalFlights()


    app.ctx.logs.info("API démarrée")


@app.listener("after_server_stop")
async def close_app(app: Sanic, loop):
    await app.ctx.pool.close()
    await app.ctx.session.close()

    app.ctx.logs.info("API arrêtée")


@app.on_request
async def before_request(request: Request):
    request.ctx.start = datetime.now().timestamp()


@app.on_response
async def after_request(request: Request, response):
    end = datetime.now().timestamp()
    process = end - request.ctx.start

    app.ctx.requests.info(f"{request.headers.get('CF-Connecting-IP', request.client_ip)} - [{request.method}] {request.url} - {response.status} ({process * 1000:.2f}ms)")


if __name__ == "__main__":
    """
    Lancement de l'API en mode développement
    """
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True,
        auto_reload=True
    )
