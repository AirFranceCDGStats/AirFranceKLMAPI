from sanic.response import JSONResponse, redirect
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="public"
)


# /
@bp.route("/")
@openapi.exclude()
async def index(request: Request) -> JSONResponse:
    return redirect("/docs")
