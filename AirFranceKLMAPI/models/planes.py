from sanic_ext import openapi


@openapi.component
class Plane:
    code = openapi.String(
        description="Code de l'avion",
        example="FHBNA",
    )
    typecode = openapi.String(
        description="Code de type de l'avion",
        example="320",
    )
    typenom = openapi.String(
        description="Nom de type de l'avion",
        example="AIRBUS A320",
    )
    wifi = openapi.Boolean(
        description="Wifi disponible",
        example=True,
    )
    satellite = openapi.Boolean(
        description="Satellite disponible",
        example=True,
    )
    compagnie = openapi.String(
        description="Code de la compagnie propriétaire de l'avion",
        example="AF",
    )


class Info:
    total = openapi.Integer(
        description="Nombre total d'avions",
        example=200,
    )


class CodeInfo:
    code = openapi.String(
        description="Code de l'avion",
        example="FHBNA",
    )


class PlanesResponse:
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
        items=Plane,
        description="Liste des avions",
    )


class PlanesUnavailableResponse:
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
        example="Aucun avion n'est disponible pour le moment. Veuillez réessayer plus tard."
    )


class PlaneResponse:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    code = openapi.Integer(
        description="Code de la requête",
        example=200,
    )
    info = CodeInfo
    data = Plane


class PlaneNotFoundResponse:
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
        example="L'avion n'existe pas."
    )
