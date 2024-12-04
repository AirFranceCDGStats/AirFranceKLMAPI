from sanic_ext import openapi


@openapi.component
class FlightLeg:
    aero_dpt = openapi.String(
        description="Code de l'aéroport de départ",
        example="CDG",
    )
    aero_arr = openapi.String(
        description="Code de l'aéroport d'arrivée",
        example="EDI",
    )
    avion = openapi.String(
        description="Code de l'avion",
        example="FHBLQ",
    )
    dpt_dateinitiale = openapi.String(
        description="Date de départ initiale",
        example="2024-06-10T15:40:00.000+02:00",
    )
    dpt_dernieredate = openapi.String(
        description="Dernière date de départ",
        example="2024-06-10T15:40:00.000+02:00",
    )
    arr_dateinitiale = openapi.String(
        description="Date d'arrivée initiale",
        example="2024-06-10T16:30:00.000+01:00",
    )
    arr_dernieredate = openapi.String(
        description="Dernière date d'arrivée",
        example="2024-06-10T16:30:00.000+01:00",
    )
    status = openapi.String(
        description="Statut du vol",
        example="Scheduled",
    )
    restricted = openapi.Boolean(
        description="Vol restreint",
        example=False,
    )
    avancee = openapi.String(
        description="Avancée du vol",
        example="0",
    )
    statuspublic = openapi.String(
        description="Statut public du vol",
        example="ON_TIME",
    )
    service = openapi.String(
        description="Service",
        example="J",
    )
    servicename = openapi.String(
        description="Nom du service",
        example="Normal Service",
    )
    timezonediff = openapi.String(
        description="Différence de fuseau horaire",
        example="-0100",
    )


@openapi.component
class Flight:
    code = openapi.String(
        description="Code du vol",
        example="20240610+AF+1486",
    )
    datevol = openapi.String(
        description="Date du vol",
        example="2024-06-10",
    )
    typetrajet = openapi.String(
        description="Type de trajet",
        example="MEDIUM",
    )
    route = openapi.Array(
        items=openapi.String(
            description="Code de l'aéroport",
            example="CDG",
        ),
        description="Route du vol",
    )
    flightLegs = openapi.Array(
        items=FlightLeg,
        description="Liste des vols",
    )
    

class Info:
    total = openapi.Integer(
        description="Nombre total de vols",
        example=200,
    )


class CodeInfo:
    code = openapi.String(
        description="Code du vol",
        example="20240610+AF+1486"
    )


class FlightsResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=200,
    )
    info = Info
    data = openapi.Array(
        items=Flight,
        description="Liste des vols",
    )


class FlightsIDResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=200,
    )
    info = Info
    data = openapi.Array(
        items=openapi.String(
            description="ID du vol",
            example="20240610+AF+1486",
        ),
        description="Liste des vols",
    )


class FlightsUnavailableResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=503,
    )
    info = openapi.Object(
        properties={},
        description="Informations",
    )
    message = openapi.String(
        description="Message de retour",
        example="Aucun vol n'est disponible pour le moment. Veuillez réessayer plus tard."
    )


class FlightResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=200,
    )
    info = CodeInfo
    data = Flight


class FlightNotFoundResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=404,
    )
    info = openapi.Object(
        properties={},
        description="Informations",
    )
    message = openapi.String(
        description="Message de retour",
        example="Le vol n'a pas été trouvé."
    )
