from sanic import Blueprint, Request, Websocket
from asyncio import sleep
from json import dumps


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
        async with request.app.ctx.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor("SELECT * FROM HISTORIQUE ORDER BY DATE DESC LIMIT 1"):
                    await ws.send(
                        dumps(
                            {
                                "success": True,
                                "code": 200,
                                "stats": {
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
                            }
                        )
                    )

        await sleep(15)
