from . import __baseURL__
from .exceptions import APIError, NotFoundError, UnauthorizedError
from utils.logger import Logger
from aiohttp import ClientSession, ContentTypeError
from typing import Literal


class AKMLRequests:
    def __init__(self, headers: dict, session: ClientSession, logs: Logger) -> None:
        self.__headers = headers
        self.session = session
        self.logs = logs


    async def getFlights(
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
        query = f"timeType={timeType}&pageSize=100"
        if startRange is not None:
            query += f"&startRange={startRange}"
        if endRange is not None:
            query += f"&endRange={endRange}"
        if departureCity is not None:
            query += f"&departureCity={departureCity}"
        if arrivalCity is not None:
            query += f"&arrivalCity={arrivalCity}"
        if carrierCode is not None:
            query += f"&carrierCode={carrierCode}"

        query += f"&pageNumber={page}"


        self.logs.debug(f"/opendata/flightstatus?{query}")


        try:
            async with self.session.get(f"{__baseURL__}/opendata/flightstatus?{query}", headers=self.__headers, ssl=True) as response:
                if response.status != 200:
                    if response.status == 404:
                        try:
                            errors: dict = await response.json()
                            error: str = "; ".join([e.get("message", None) for e in errors.get("errors", {})])
                        except:
                            error = None

                        raise NotFoundError(
                            error=error
                        )
                    elif response.status == 403:
                        raise UnauthorizedError()
                    else:
                        raise APIError()
                else:
                    json: dict = await response.json()
                    return json.get("operationalFlights", []), json.get("page", {})
        except ContentTypeError:
            raise APIError
