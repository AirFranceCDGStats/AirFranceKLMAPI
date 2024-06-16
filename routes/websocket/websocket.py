from models.status import StatusResponse
from models.responses import RateLimitedResponse
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request, Websocket
from sanic_ext import openapi
from asyncio import sleep


bp = Blueprint(
    name="Websocket",
    version=1,
    version_prefix="api/v"
)


@bp.websocket("/stats")
async def stats(request: Request, ws: Websocket):
    """
    Retourne le statut de l'API en temps réel.

    :return: WebSocket
    """
    while True:
        await ws.send(
            {
                "success": True,
                "code": 200,
                "info": {
                    "airports": len(request.app.ctx.cache.airportsCodes),
                    "flights": len(request.app.ctx.cache.flightsCodes),
                    "companies": len(request.app.ctx.cache.companies),
                },
                "message": "L'API est en ligne."
            }
        )
        await sleep(5)
