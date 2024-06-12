from . import __headers__
from .requests import AKMLRequests
from utils.logger import Logger
from aiohttp import ClientSession
from typing import Literal


class AFKLMClient:
    def __init__(self, key: str, session: ClientSession, logs: Logger) -> None:
        self.key = key[:8]
        self.__headers = {
            **__headers__,
            "Api-Key": key
        }

        self.client = AKMLRequests(headers=self.__headers, session=session, logs=logs)

        self.flights = Flights(self.client)


class Flights:
    def __init__(self, client: AKMLRequests) -> None:
        self.client = client


    async def get(
        self,
        startRange: str = None,
        endRange: str = None,
        departureCity: str = None,
        arrivalCity: str = None,
        carrierCode: str = None,
        timeType: Literal["U", "L"] = "U",
        page: int = 0,
    ) -> tuple[list[dict], dict]:
        """
        Récupère les vols

        :return: Les vols
        """
        return await self.client.getFlights(
            startRange=startRange,
            endRange=endRange,
            departureCity=departureCity,
            arrivalCity=arrivalCity,
            carrierCode=carrierCode,
            timeType=timeType,
            page=page,
        )
