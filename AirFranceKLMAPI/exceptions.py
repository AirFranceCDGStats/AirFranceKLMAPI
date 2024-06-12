class APIError(Exception):
    def __init__(self, error: str = "Une erreur est survenue lors de la requête."):
        self.error = error
        super().__init__(self.error)

    
    def __str__(self):
        return self.error


class NotFoundError(Exception):
    def __init__(self, error: str = "La ressource demandée est introuvable."):
        self.error = error
        super().__init__(self.error)


    def __str__(self):
        return self.error


class UnauthorizedError(Exception):
    def __init__(self, error: str = "Vous n'êtes pas autorisé à accéder à cette ressource."):
        self.error = error
        super().__init__(self.error)


    def __str__(self):
        return self.error
