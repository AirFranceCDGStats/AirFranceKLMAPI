from ...models.status import StatusResponse, HistoriqueResponse
from ...models.responses import RateLimitedResponse
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


# /historique
@bp.route("/historique", methods=["GET"])
@openapi.definition(
    summary="Historique de l'API",
    description="Retourne l'historique de l'API.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={
        "application/json": HistoriqueResponse
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
async def getHistorique(request: Request) -> JSONResponse:
    """
    Retourne l'historique de l'API.

    :return: JSONResponse
    """
    data = []

    async with request.app.ctx.pool.acquire() as connection:
        historique = await connection.fetch("SELECT * FROM HISTORIQUE ORDER BY DATE DESC LIMIT 30")

    for row in historique:
        data.append(
            {
                "date": row["date"].strftime("%d/%m/%Y %H:%M:%S"),
                "airports": row["nbaeroports"],
                "flights": row["nbvols"],
                "companies": row["nbavions"],
                "steps": row["nbetapes"],
                "on_time": row["nbetape_on_time"],
                "delayed_departure": row["nbetape_delayed_departure"],
                "delayed_arrival": row["nbetape_delayed_arrival"],
                "delayed": row["nbetape_delayed"],
                "cancelled": row["nbetape_cancelled"],
                "gaz": row["gaz"],
            }
        )

    return json(
        {
            "success": True,
            "code": 200,
            "info": data
        },
        status=200
    )
