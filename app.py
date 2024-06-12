from AirFranceKLMAPI.client import AFKLMClient
from sanic import Sanic
from routes.service.service import bp as RouteService
from routes.aeroports.aeroports import bp as RouteAeroports
from routes.vols.vols import bp as RouteVols
from routes.planes.planes import bp as RoutePlanes
from routes.compagnies.compagnies import bp as RouteCompagnies
from routes.public.public import bp as RoutePublic
from utils.logger import Logger
from utils.cache import Cache
from dotenv import load_dotenv
from os import environ
from datetime import datetime
from aiohttp import ClientSession
from apscheduler.triggers.interval import IntervalTrigger
from textwrap import dedent
from asyncpg import create_pool


load_dotenv(dotenv_path=f".env")


app = Sanic(
    name="AirFranceKLMAPI"
)

app.config.API_HOST = f"{environ.get('API_HOST', '0.0.0.0')}:{environ.get('API_PORT', 5000)}"
#app.config.API_HOST = "airfrance.bayfield.dev"
app.config.API_BASEPATH = ""
app.config.API_SCHEMES = ["https"]
app.config.API_VERSION = "1.0.0"
app.config.API_TERMS_OF_SERVICE = "https://airfrance.bayfield.dev/terms"
app.config.API_CONTACT_EMAIL = "airfrance@bayfield.dev"

app.config.OAS = True
app.config.OAS_UI_REDOC = True
app.config.OAS_PATH_TO_REDOC_HTML = "scalar.html"
app.config.OAS_UI_SWAGGER = False
app.config.OAS_UI_DEFAULT = "redoc"
app.config.OAS_URI_TO_JSON = "/openapi.json"
app.config.OAS_URL_PREFIX = "/docs"

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


@app.listener("before_server_start")
async def setup_app(app: Sanic, loop):
    app.ctx.launch_time = int(datetime.utcnow().timestamp())
    app.ctx.logs = Logger("logs")
    app.ctx.requests = Logger("requests")
    app.ctx.session = ClientSession()

    # Chargement des clients
    app.ctx.clients = []
    for key in environ.keys():
        if key.startswith("AIRFRANCEKLM_API_KEY_"):
            app.ctx.clients.append(AFKLMClient(environ.get(key), app.ctx.session, app.ctx.logs))
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


    app.ctx.logs.info("API démarrée")


@app.listener("after_server_stop")
async def close_app(app: Sanic, loop):
    await app.ctx.session.close()

    app.ctx.logs.info("API arrêtée")


@app.on_response
async def after_request(request, response):
    app.ctx.requests.info(f"[{request.method}] {request.url} - {response.status}")


if __name__ == "__main__":
    """
    Lancement de l'API en mode développement
    """
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        auto_reload=True
    )
