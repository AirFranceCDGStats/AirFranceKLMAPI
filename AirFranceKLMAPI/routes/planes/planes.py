from ...models.planes import *
from ...models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Avions",
    url_prefix="/planes",
    version=1,
    version_prefix="api/v"
)


# /planes
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des avions",
    description="Liste des avions disponibles.",
    tag="Avions",
)
@openapi.response(
    status=200,
    content={
        "application/json": PlanesResponse
    },
    description="Liste des avions disponibles."
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
        "application/json": PlanesUnavailableResponse
    },
    description="Aucun avion n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getPlanes(request: Request) -> JSONResponse:
    """
    Récupère les avions

    :return: Les avions
    """
    if not request.app.ctx.cache.planes:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun avion n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        return json(
            {
                "success": True,
                "code": 200,
                "info": {
                    "total": len(request.app.ctx.cache.planes),
                },
                "data": request.app.ctx.cache.planes
            },
            status=200
        )
    

# /planes/{planeCode}
@bp.route("/<planeCode>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un avion",
    description="Détails d'un avion en fonction de son code.",
    tag="Avions",
)
@openapi.response(
    status=200,
    content={
        "application/json": PlaneResponse
    },
    description="Détails de l'avion"
)
@openapi.response(
    status=404,
    content={
        "application/json": PlaneNotFoundResponse
    },
    description="Aucun avion n'est disponible."
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
        "application/json": PlanesUnavailableResponse
    },
    description="Aucun avion n'est disponible pour le moment. Veuillez réessayer plus tard."
)
async def getPlane(request: Request, planeCode: str) -> JSONResponse:
    """
    Récupère un avion

    :param planeCode: Le code de l'avion
    :return: L'avion
    """
    if not request.app.ctx.cache.planes:
        return json(
            {
                "success": False,
                "code": 503,
                "info": {},
                "message": "Aucun avion n'est disponible pour le moment. Veuillez réessayer plus tard."
            },
            status=503
        )
    else:
        avion = next((a for a in request.app.ctx.cache.planes if a.get("code", None) == planeCode), None)

        if avion is None:
            return json(
                {
                    "success": False,
                    "code": 404,
                    "info": {
                        "code": planeCode
                    },
                    "message": "L'avion n'existe pas."
                },
                status=404
            )
        else:
            return json(
                {
                    "success": True,
                    "code": 200,
                    "info": {
                        "code": planeCode
                    },
                    "data": avion
                },
                status=200
            )
