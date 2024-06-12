from dotenv import load_dotenv
from os import environ


load_dotenv(dotenv_path=".env")


__title__ = "AirFranceKLMAPI"
__author__ = "PaulBayfield"
__version__ = "1.0.1"
__description__ = "Un wrapper pour l'API d'Air France KLM"

__baseURL__ = environ["AIRFRANCEKLM_SERVICE_URL"]
__headers__ = {
    "User-Agent": f"{__title__}/{__version__} (réalisé par github.com/PaulBayfield)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Language": "fr-FR"
}


from .client import AFKLMClient

from .exceptions import *
