from models.status import StatusResponse
from models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Service",
    version=1,
    version_prefix="api/v"
)


# /status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="Statut de l'API",
    description="Retourne le statut de l'API.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={
        "application/json": StatusResponse
    },
    description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimitedResponse
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
async def getStatus(request: Request) -> JSONResponse:
    """
    Retourne le statut de l'API.

    :return: JSONResponse
    """
    return json(
        {
            "success": True,
            "code": 200,
            "info": {
                "airports": len(request.app.ctx.cache.airportsCodes),
                "flights": len(request.app.ctx.cache.flightsCodes),
                "companies": len(request.app.ctx.cache.companies),
            },
            "message": "L'API est en ligne."
        },
        status=200
    )