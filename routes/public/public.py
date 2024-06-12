from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="public"
)


# /
@bp.route("/")
@openapi.exclude()
async def index(request: Request) -> JSONResponse:
    return json({"message": "Hello, World!"})
