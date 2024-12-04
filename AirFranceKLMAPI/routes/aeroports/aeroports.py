from ...models.airports import *
from ...models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Aeroports",
    url_prefix="/airports",
    version=1,
    version_prefix="api/v"
)


# /airports
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des aéroports",
    description="Liste des aéroports disponibles au départ de l'aéroport de Paris-Charles de Gaulle (`CDG`).",
    tag="Aeroports",
)
@openapi.response(
    status=200,
    content={
        "application/json": AirportsResponse
    },
    description="Liste des aéroports disponibles"
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
        "application/json": AirportsUnavailableResponse
    },
    description="Aucun aéroport n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getAirports(request: Request) -> JSONResponse:
    """
    Récupère les aéroports

    :return: Les aéroports
    """
    if not request.app.ctx.cache.airports:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun aéroport n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(request.app.ctx.cache.airports),
                },
                "data": request.app.ctx.cache.airports
            },
            status=200
        )
    

# /airports/{airportCode}
@bp.route("/<airportCode>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un aéroport",
    description="Détails d'un aéroport en fonction de son code.",
    tag="Aeroports",
)
@openapi.response(
    status=200,
    content={
        "application/json": AirportResponse
    },
    description="Détails de l'aéroport"
)
@openapi.response(
    status=404,
    content={
        "application/json": AirportNotFoundResponse
    },
    description="Aucun aéroport n'est disponible."
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
        "application/json": AirportsUnavailableResponse
    },
    description="Aucun aéroport n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getAirport(request: Request, airportCode: str) -> JSONResponse:
    """
    Récupère un aéroport

    :param airportCode: Le code de l'aéroport
    :return: L'aéroport
    """
    if not request.app.ctx.cache.airports:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun aéroport n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        airport = next((a for a in request.app.ctx.cache.airports if a.get("code", None) == airportCode), None)

        if airport is None:
            return json(
                {
                    "success": False,
                    "code": 404,
                    "info": {
                        "code": airportCode
                    },
                    "message": "L'aéroport n'existe pas."
                },
                status=404
            )
        else:
            return json(
                {
                    "success": True,
                    "code": 200,
                    "info": {
                        "code": airportCode
                    },
                    "data": airport
                },
                status=200
            )
