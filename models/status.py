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


class HistoriqueStatsResponse:
    airports = openapi.Integer(
        description="Nombre d'aéroports",
        example=200,
    )
    flights = openapi.Integer(
        description="Nombre de vols",
        example=80_000,
    )
    companies = openapi.Integer(
        description="Nombre de compagnies",
        example=50,
    )
    steps = openapi.Integer(
        description="Nombre d'étapes",
        example=200,
    )
    on_time = openapi.Integer(
        description="Nombre d'avions à l'heure",
        example=200,
    )
    delayed_departure = openapi.Integer(
        description="Nombre de départ retardé",
        example=200,
    )
    delayed_arrival = openapi.Integer(
        description="Nombre d'arrivée retardée",
        example=200,
    )
    delayed = openapi.Integer(
        description="Nombre de vols retardés (départ et arrivée)",
        example=200,
    )
    cancelled = openapi.Integer(
        description="Nombre de vols annulés",
        example=200,
    )
    gaz = openapi.Integer(
        description="Nombre de litres de gaz consommés",
        example=200,
    )


class HistoriqueResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de retour",
        example=200,
    )
    info =  openapi.Array(
        items=HistoriqueStatsResponse,
        description="Historique de l'API",
    )
    