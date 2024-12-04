from ...models.companies import *
from ...models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Compagnies",
    url_prefix="/airlines",
    version=1,
    version_prefix="api/v"
)


# /airlines
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste de toutes les compagnies",
    description="Liste de toutes les compagnies.",
    tag="Compagnies",
)
@openapi.response(
    status=200,
    content={
        "application/json": CompaniesResponse
    },
    description="Liste de toutes les compagnies"
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
        "application/json": CompaniesUnavailableResponse
    },
    description="Aucune compagnie n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getAirlines(request: Request) -> JSONResponse:
    """
    Récupère les compagnies

    :return: Les compagnies
    """
    if not request.app.ctx.cache.companies:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucune compagnie n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(request.app.ctx.cache.companies),
                },
                "data": request.app.ctx.cache.companies
            },
            status=200
        )
