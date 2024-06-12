from sanic_ext import openapi


class Info:
    airports = openapi.Integer(
        description="Nombre d'aéroports en cache",
        example=200,
    )
    flights = openapi.Integer(
        description="Nombre de vols en cache",
        example=80_000,
    )
    companies = openapi.Integer(
        description="Nombre de compagnies en cache",
        example=50,
    )


class StatusResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    info = Info
    message = openapi.String(
        description="Message de retour",
        example="L'API est en ligne."
    )
