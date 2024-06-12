from sanic_ext import openapi


@openapi.component
class Company:
    code = openapi.String(
        description="Code de la compagnie aérienne",
        example="AF",
    )
    name = openapi.String(
        description="Nom de la compagnie aérienne",
        example="AIR FRANCE",
    )


class Info:
    total = openapi.Integer(
        description="Nombre total de compagnies aériennes",
        example=200,
    )


class CompaniesResponse:
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
        items=Company,
        description="Liste des compagnies aériennes",
    )


class CompaniesUnavailableResponse:
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
        example="Aucune compagnie aérienne n'est disponible pour le moment. Veuillez réessayer plus tard."
    )
