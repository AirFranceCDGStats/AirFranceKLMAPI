from ...models.flights import *
from ...models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi
from json import loads


bp = Blueprint(
    name="Vols",
    url_prefix="/flights",
    version=1,
    version_prefix="api/v"
)


# /flights
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des vols",
    description="""
Liste des vols disponibles au départ de l'aéroport de Paris-Charles de Gaulle (`CDG`) dans la prochaine heure.

Les vols sont mis à jour toutes les **`30 minutes`**.
""",
    tag="Vols",
)
@openapi.response(
    status=200,
    content={
        "application/json": FlightsResponse
    },
    description="Liste des vols disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.response(
    status=503,
    content={
        "application/json": FlightsUnavailableResponse
    },
    description="Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getFlights(request: Request) -> JSONResponse:
    """
    Récupère les vols

    :return: Les vols
    """
    if request.app.ctx.cache.nextFlights is None:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {}, 
                "message": "Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(request.app.ctx.cache.nextFlights),
                },
                "data": request.app.ctx.cache.nextFlights
            },
            status=200
        )


# /flights/all
@bp.route("/all", methods=["GET"])
@openapi.definition(
    summary="Liste de tous les vols",
    description="Liste de tous les vols disponibles.",
    tag="Vols",
)
@openapi.response(
    status=200,
    content={
        "application/json": FlightsIDResponse
    },
    description="Liste de tous les vols disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.response(
    status=503,
    content={
        "application/json": FlightsUnavailableResponse
    },
    description="Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getAllFlights(request: Request) -> JSONResponse:
    """
    Récupère tous les vols

    :return: Tous les vols
    """
    if not request.app.ctx.cache.flightsCodes:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(request.app.ctx.cache.flightsCodes),
                },
                "data": request.app.ctx.cache.flightsCodes
            },
            status=200
        )
    

# /flights/all/test
@bp.route("/all/test", methods=["GET"])
@openapi.definition(
    summary="[TEST] Liste de tous les vols",
    description="[TEST] Liste de tous les vols disponibles.",
    tag="Vols",
)
@openapi.response(
    status=200,
    content={
        "application/json": FlightsIDResponse
    },
    description="Liste de tous les vols disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.response(
    status=503,
    content={
        "application/json": FlightsUnavailableResponse
    },
    description="Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getAllFlightsTest(request: Request) -> JSONResponse:
    """
    Récupère tous les vols

    :return: Tous les vols
    """
    async with request.app.ctx.pool.acquire() as connection:
        flights = await connection.fetch("SELECT * FROM vol")


    if not flights:
        return json(
            {
                "success": False,
                "code": 404,
                "info": {
                    "total": len(flights),
                },
                "message": "Le vol n'existe pas."
            },
            status=404
        )
    else:
        flightData = []
        for flight in flights:
            async with request.app.ctx.pool.acquire() as connection:
                legs = await connection.fetch("SELECT * FROM etapeduvol WHERE vol = $1", flight.get("code"))

            legsData = []
            for leg in legs:
                legsData.append(
                    {
                        "aero_dpt": leg.get("aero_dpt"),
                        "aero_arr": leg.get("aero_arr"),
                        "avion": leg.get("avion"),
                        "dpt_dateinitiale": leg.get("dpt_dateinitiale"),
                        "dpt_dernieredate": leg.get("dpt_dernieredate"),
                        "arr_dateinitiale": leg.get("arr_dateinitiale"),
                        "arr_dernieredate": leg.get("arr_dernieredate"),
                        "status": leg.get("status"),
                        "restricted": leg.get("restricted"),
                        "avancee": leg.get("avancee"),
                        "statuspublic": leg.get("statuspublic"),
                        "service": leg.get("service"),
                        "servicename": leg.get("servicename"),
                        "timezoneDiff": leg.get("timezonediff")
                    }
                )

            flightData.append({
                "code": flight.get("code"),
                "datevol": flight.get("datevol").strftime("%Y-%m-%d"),
                "typetrajet": flight.get("typetrajet"),
                "route": loads(flight.get("route", {})),
                "flightLegs": legsData
            })

        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(flights),
                },
                "data": flightData
            },
            status=200
        )


# /flights/<flightID>
@bp.route("/<flightID>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un vol",
    description="Récupère un vol en fonction de son identifiant.",
    tag="Vols",
)
@openapi.response(
    status=200,
    content={
        "application/json": FlightResponse
    },
    description="Le vol a été trouvé"
)
@openapi.response(
    status=404,
    content={
        "application/json": FlightNotFoundResponse
    },
    description="Le vol n'a pas été trouvé."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
async def getFlight(request, flightID: str) -> JSONResponse:
    """
    Récupère un vol

    :param flightID: L'identifiant du vol
    :return: Le vol
    """
    async with request.app.ctx.pool.acquire() as connection:
        flight = await connection.fetch("SELECT * FROM vol WHERE code = $1", flightID)


    if not flight:
        return json(
            {
                "success": False,
                "code": 404,
                "info": {
                    "id": flightID
                },
                "message": "Le vol n'existe pas."
            },
            status=404
        )
    else:
        flight = flight[0]

        async with request.app.ctx.pool.acquire() as connection:
            legs = await connection.fetch("SELECT * FROM etapeduvol WHERE vol = $1", flightID)

        legsData = []
        for leg in legs:
            legsData.append(
                {
                    "aero_dpt": leg.get("aero_dpt"),
                    "aero_arr": leg.get("aero_arr"),
                    "avion": leg.get("avion"),
                    "dpt_dateinitiale": leg.get("dpt_dateinitiale"),
                    "dpt_dernieredate": leg.get("dpt_dernieredate"),
                    "arr_dateinitiale": leg.get("arr_dateinitiale"),
                    "arr_dernieredate": leg.get("arr_dernieredate"),
                    "status": leg.get("status"),
                    "restricted": leg.get("restricted"),
                    "avancee": leg.get("avancee"),
                    "statuspublic": leg.get("statuspublic"),
                    "service": leg.get("service"),
                    "servicename": leg.get("servicename"),
                    "timezoneDiff": leg.get("timezonediff")
                }
            )

        flightData = {
            "code": flight.get("code"),
            "datevol": flight.get("datevol").strftime("%Y-%m-%d"),
            "typetrajet": flight.get("typetrajet"),
            "route": loads(flight.get("route", {})),
            "flightLegs": legsData

        }

        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "id": flightID
                },
                "data": flightData
            },
            status=200
        )


# /flights/unique
@bp.route("/unique", methods=["GET"])
@openapi.definition(
    summary="Liste de tous les vols uniques",
    description="Liste de tous les vols uniques.",
    tag="Vols",
)
@openapi.response(
    status=200,
    content={
        "application/json": FlightsIDResponse
    },
    description="Liste de tous les vols uniques"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.response(
    status=503,
    content={
        "application/json": FlightsUnavailableResponse
    },
    description="Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getUniqueFlights(request) -> JSONResponse:
    """
    Récupère les vols uniques

    :return: Les vols uniques
    """
    if not request.app.ctx.cache.flightsCodes:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        flights = []
        for flightCode in request.app.ctx.cache.flightsCodes:
            if flightCode not in flights:
                flights.append(flightCode)

        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(flights),
                },
                "data": flights
            },
            status=200
        )
