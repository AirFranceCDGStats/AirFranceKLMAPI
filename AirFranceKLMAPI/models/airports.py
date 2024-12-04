from sanic_ext import openapi


@openapi.component
class Airport:
    code = openapi.String(
        description="Code de l'aéroport",
        example="CDG",
    )
    nom = openapi.String(
        description="Nom de l'aéroport",
        example="CHARLES DE GAULLE AIRPORT",
    )
    nomltr = openapi.String(
        description="Nom de l'aéroport en toutes lettres",
        example="aéroport Paris-Charles de Gaulle",
    )
    ville = openapi.String(
        description="Ville de l'aéroport",
        example="PARIS",
    )
    pays = openapi.String(
        description="Pays de l'aéroport",
        example="FRANCE",
    )
    latitude = openapi.Float(
        description="Latitude de l'aéroport",
        example=49.0097,
    )
    longitude = openapi.Float(
        description="Longitude de l'aéroport",
        example=2.5486,
    )


class Info:
    total = openapi.Integer(
        description="Nombre total d'aéroports",
        example=200,
    )


class CodeInfo:
    code = openapi.String(
        description="Code de l'aéroport",
        example="CDG",
    )


class AirportsResponse:
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
        items=Airport,
        description="Liste des aéroports",
    )


class AirportsUnavailableResponse:
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
        example="Aucun aéroport n'est disponible pour le moment. Veuillez réessayer plus tard."
    )


class AirportResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=200,
    )
    info = CodeInfo
    data = Airport


class AirportNotFoundResponse:
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
        example="L'aéroport n'existe pas."
    )
