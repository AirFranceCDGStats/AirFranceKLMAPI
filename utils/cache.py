from AirFranceKLMAPI import AFKLMClient, NotFoundError
from utils.date import getDateRange, getDate
from utils.logger import Logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from json import dumps
from asyncio import sleep
from asyncpg import Pool
from datetime import datetime, timedelta


class Cache(Scheduler):
    """
    Classe de gestion du cache
    """
    def __init__(self, clients: list[AFKLMClient], logs: Logger, pool: Pool) -> None:
        super().__init__()
        self.clients = clients
        self.logs = logs
        self.pool = pool

        self.nextFlights = []
        self.airports = []
        self.airportsCodes = []
        self.flightsCodes = []
        self.companies = []
        self.planes = []
        self.planesCodes = []

        self.currentClient = 0


    async def loadCache(self) -> None:
        """
        Chargement du cache
        """
        await self.loadAirports()
        await self.loadFlights()
        await self.loadCompanies()
        await self.loadPlanes()


    async def loadAirports(self) -> None:
        """
        Chargement des aéroports
        """
        self.logs.info("[DB] [AIRPORTS] En cours de chargement des aéroports...")

        self.logs.debug("[DB] [AIRPORTS] SELECT * FROM aeroport")

        async with self.pool.acquire() as connection:
            airports = await connection.fetch("SELECT * FROM aeroport")

            for airport in airports:
                self.airports.append(dict(airport))
                self.airportsCodes.append(airport.get("code"))


        self.logs.info("[DB] [AIRPORTS] Aéroports chargés !")


    async def loadFlights(self) -> None:
        """
        Chargement des vols
        """
        self.logs.info("[DB] [FLIGHTS] En cours de chargement des vols...")

        self.logs.debug("[DB] [FLIGHTS] SELECT code FROM vol")

        async with self.pool.acquire() as connection:
            flightsCodes = await connection.fetch("SELECT code FROM vol")

            for flightCode in flightsCodes:
                self.flightsCodes.append(flightCode.get("code"))


        self.logs.info("[DB] [FLIGHTS] Vols chargés !")


    async def loadCompanies(self) -> None:
        """
        Chargement des compagnies
        """
        self.logs.info("[DB] [COMPANIES] En cours de chargement des compagnies...")

        self.logs.debug("[DB] [COMPANIES] SELECT * FROM compagnie")

        async with self.pool.acquire() as connection:
            companies = await connection.fetch("SELECT * FROM compagnie")

            for company in companies:
                self.companies.append(dict(company))


        self.logs.info("[DB] [COMPANIES] Compagnies chargées !")


    async def loadPlanes(self) -> None:
        """
        Chargement des avions
        """
        self.logs.info("[DB] [PLANES] En cours de chargement des avions...")

        self.logs.debug("[DB] [PLANES] SELECT * FROM avion")

        async with self.pool.acquire() as connection:
            planes = await connection.fetch("SELECT * FROM avion")

            for plane in planes:
                self.planes.append(dict(plane))
                self.planesCodes.append(plane.get("code"))


        self.logs.info("[DB] [PLANES] Avions chargés !")


    async def refreshFlights(self) -> None:
        """
        Chargement du cache
        """
        self.logs.info("[CACHE] En cours de chargement des nouveaux vols...")

        flights = []

        client = self.clients[self.currentClient]
        self.currentClient = (self.currentClient + 1) % len(self.clients)

        self.logs.debug(f"[CACHE] Utilisation du client n°{self.currentClient} ({client.key}...)")

        try:
            start, end = getDateRange()

            flights, page = await client.flights.get(
                startRange=start,
                endRange=end,
                timeType="U",
                departureCity="PAR",
                carrierCode="AF",
            )

            if page.get("totalPages", 1) > 1:
                for i in range(1, page.get("totalPages", 1)):
                    await sleep(1)
                    moreFlights, _ = await client.flights.get(
                        startRange=start,
                        endRange=end,
                        timeType="U",
                        departureCity="PAR",
                        carrierCode="AF",
                        page=i,
                    )

                    flights.extend(moreFlights)
        except NotFoundError:
            self.logs.error("Impossible de charger le cache : Aucun vol trouvé")
            pass
        except Exception as e:
            self.logs.error(f"Impossible de charger le cache : {e}")
            pass


        self.logs.debug(f"[CACHE] {len(flights)} vols chargés !")

        await self.save(flights)

        self.logs.info("[CACHE] Nouveaux vols chargés !")


    async def historicalFlights(self) -> None:
        """
        Chargement des anciens vols
        """
        self.logs.info("[CACHE] En cours de chargement des anciens vols...")

        flights = []

        client = self.clients[self.currentClient]

        self.logs.debug(f"[CACHE] Utilisation du client n°{self.currentClient} ({client.key}...)")

        await sleep(10)

        try:
            async with self.pool.acquire() as connection:
                date = await connection.fetchval("SELECT date FROM historique ORDER BY date DESC LIMIT 1")

            end = date  
            for _ in range(1, 8):
                start = date - timedelta(hours=24)

                flights, page = await client.flights.get(
                    startRange=start.strftime("%Y-%m-%dT00:00:00Z"),
                    endRange=end.strftime("%Y-%m-%dT00:00:00Z"),
                    timeType="U",
                    departureCity="PAR",
                    carrierCode="AF",
                )

                if page.get("totalPages", 1) > 1:
                    for i in range(1, page.get("totalPages", 1)):
                        await sleep(1)
                        moreFlights, _ = await client.flights.get(
                            startRange=start.strftime("%Y-%m-%dT00:00:00Z"),
                            endRange=end.strftime("%Y-%m-%dT00:00:00Z"),
                            timeType="U",
                            departureCity="PAR",
                            carrierCode="AF",
                            page=i,
                        )

                        flights.extend(moreFlights)

                self.logs.debug(f"[CACHE] {len(flights)} vols chargés !")

                await self.save(flights)
        except NotFoundError:
            self.logs.error("Impossible de charger le cache : Aucun vol trouvé")
            pass
        except Exception as e:
            self.logs.error(f"Impossible de charger le cache : {e}")
            pass

        self.logs.info("[CACHE] Anciens vols chargés !")


    async def save(self, flights: list) -> None:
        """
        Sauvegarde des aéroports et des vols

        :param flights: Les vols
        """
        self.logs.info("[CACHE] Sauvegarde des données...")

        flightsToSave = []
        airportsToSave = []
        companiesToSave = []
        planesToSave = []

        for flight in flights:
            if flight.get("airline").get("code", "") == "AF":
                if "CDG" in flight.get("route", [""]):
                    flightLegs = flight.get("flightLegs", [])

                    train = False
                    for flightLeg in flightLegs:
                        if flightLeg.get("serviceTypeName", "") == "Service operated by Surface Vehicle":
                            train = True
                        else:
                            airport: dict = flightLeg.get("departureInformation", {}).get("airport", {})
                            if airport.get("code") not in self.airportsCodes:
                                self.airportsCodes.append(airport.get("code"))
                                self.airports.append(
                                    {
                                        "code": airport.get("code"),
                                        "nom": airport.get("name"),
                                        "nomfr": airport.get("nameLangTranl"),
                                        "ville": airport.get("city").get("name"),
                                        "pays": airport.get("city").get("country").get("name"),
                                        "latitude": airport.get("location").get("latitude"),
                                        "longitude": airport.get("location").get("longitude")
                                    }
                                )

                                airportsToSave.append(airport)

                            airport: dict = flightLeg.get("arrivalInformation", {}).get("airport", {})
                            if airport.get("code") not in self.airportsCodes:
                                self.airportsCodes.append(airport.get("code"))
                                self.airports.append(
                                    {
                                        "code": airport.get("code"),
                                        "nom": airport.get("name"),
                                        "nomfr": airport.get("nameLangTranl"),
                                        "ville": airport.get("city").get("name"),
                                        "pays": airport.get("city").get("country").get("name"),
                                        "latitude": airport.get("location").get("latitude"),
                                        "longitude": airport.get("location").get("longitude")
                                    }
                                )

                                airportsToSave.append(airport)

                            if flightLeg.get("aircraft", {}).get("ownerAirlineCode", None) and {"code": flightLeg.get("aircraft", {}).get("ownerAirlineCode", ""), "nom": flightLeg.get("aircraft", {}).get("ownerAirlineName", "")} not in self.companies:
                                self.companies.append({"code": flightLeg.get("aircraft", {}).get("ownerAirlineCode", ""), "nom": flightLeg.get("aircraft", {}).get("ownerAirlineName", "")})

                                companiesToSave.append({"code": flightLeg.get("aircraft", {}).get("ownerAirlineCode", ""), "nom": flightLeg.get("aircraft", {}).get("ownerAirlineName", "")})

                            if flightLeg.get("aircraft", {}).get("registration", "") not in self.planesCodes:
                                self.planesCodes.append(flightLeg.get("aircraft", {}).get("registration", ""))
                                self.planes.append(
                                    {
                                        "code": flightLeg.get("aircraft", {}).get("registration", ""),
                                        "typecode": flightLeg.get("aircraft", {}).get("typeCode", ""),
                                        "typenom": flightLeg.get("aircraft", {}).get("typeName", ""),
                                        "wifi": flightLeg.get("aircraft", {}).get("wifiEnabled", "") == "Y",
                                        "satellite": flightLeg.get("aircraft", {}).get("satelliteConnectivityOnBoard", "") == "Y",
                                        "compagnie": flightLeg.get("aircraft", {}).get("ownerAirlineCode", "")
                                    }
                                )

                                planesToSave.append(flightLeg.get("aircraft"))


                    if not train:
                        if flight not in flightsToSave:
                            flightsToSave.append(flight)


        cleanFlights = []
        async with self.pool.acquire() as connection:
            for airport in airportsToSave:
                self.logs.debug(f"[DB] [AIRPORTS] INSERT INTO aeroport VALUES ({airport.get('code')}, {airport.get('name')}, {airport.get('nameLangTranl')}, {airport.get('city').get('name')}, {airport.get('city').get('country').get('name')}, {airport.get('location').get('latitude')}, {airport.get('location').get('longitude')})")
                await connection.execute("INSERT INTO aeroport VALUES ($1, $2, $3, $4, $5, $6, $7)", airport.get("code"), airport.get("name"), airport.get("nameLangTranl"), airport.get("city").get("name"), airport.get("city").get("country").get("name"), airport.get("location").get("latitude"), airport.get("location").get("longitude"))


            for company in companiesToSave:
                self.logs.debug(f"[DB] [COMPANIES] INSERT INTO compagnie VALUES ({company.get('code')}, {company.get('nom')})")
                await connection.execute("INSERT INTO compagnie VALUES ($1, $2)", company.get("code"), company.get("nom"))


            for plane in planesToSave:
                if plane.get('registration', None):
                    self.logs.debug(f"[DB] [PLANES] INSERT INTO avion VALUES ({plane.get('registration')}, {plane.get('typeCode')}, {plane.get('typeName')}, {plane.get('wifiEnabled') == 'Y'}, {plane.get('satelliteConnectivityOnBoard') == 'Y'}, {plane.get('ownerAirlineCode')})")
                    await connection.execute("INSERT INTO avion VALUES ($1, $2, $3, $4, $5, $6)", plane.get("registration"), plane.get("typeCode"), plane.get("typeName"), plane.get("wifiEnabled") == "Y", plane.get("satelliteConnectivityOnBoard") == "Y", plane.get("ownerAirlineCode"))


            async with connection.transaction():
                for flight in flightsToSave:
                    self.logs.debug(f"[DB] [FLIGHTS] INSERT INTO vol VALUES ({flight.get('id')}, {getDate(flight.get('flightScheduleDate'))}, {flight.get('haul')}, {dumps(flight.get('route'))})")
                    await connection.execute("""
                        INSERT INTO vol
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (code) DO UPDATE
                        SET DATEVOL = $2, TYPETRAJET = $3, ROUTE = $4
                    """,
                        flight.get("id"), 
                        getDate(flight.get("flightScheduleDate")), 
                        flight.get("haul"), 
                        dumps(flight.get("route"))
                    )

                    legs = []
                    for flightLeg in flight.get("flightLegs", []):
                        dpt_dateinitiale: str = flightLeg.get("departureInformation").get("times").get("scheduled")
                        dpt_dernieredate: str = flightLeg.get("departureInformation").get("times").get("latestPublished")
                        arr_dateinitiale: str = flightLeg.get("arrivalInformation").get("times").get("scheduled")
                        arr_dernieredate: str = flightLeg.get("arrivalInformation").get("times").get("latestPublished")

                        d_dpt_dateinitiale = getDate(dpt_dateinitiale)
                        d_dpt_dernieredate = getDate(dpt_dernieredate)
                        d_arr_dateinitiale = getDate(arr_dateinitiale)
                        d_arr_dernieredate = getDate(arr_dernieredate)

                        status = "ON_TIME"
                        if dpt_dateinitiale != dpt_dernieredate or arr_dateinitiale != arr_dernieredate:
                            if (d_arr_dateinitiale - d_arr_dernieredate).seconds > 120:
                                status = "AHEAD"
                            if (d_dpt_dernieredate - d_dpt_dateinitiale).seconds > 120:
                                status = "DELAYED_DEPARTURE"
                            if (d_arr_dernieredate - d_arr_dateinitiale).seconds > 120:
                                status = "DELAYED_ARRIVAL"
                            if (d_arr_dernieredate - d_arr_dateinitiale).seconds > 300:
                                status = "DELAYED"
                        if flightLeg.get("legStatusPublic") == "CANCELLED":
                            status = "CANCELLED"

                        self.logs.debug(f"[DB] [FLIGHTS] INSERT INTO etapeduvol VALUES ({flightLeg.get('status')}, {flightLeg.get('aircraft').get('registration')}, {flightLeg.get('departureInformation').get('airport').get('code')}, {flight.get('id')}, {flightLeg.get('arrivalInformation').get('airport').get('code')}, {getDate(flightLeg.get('departureInformation').get('times').get('scheduled'))}, {getDate(flightLeg.get('departureInformation').get('times').get('latestPublished'))}, {getDate(flightLeg.get('arrivalInformation').get('times').get('scheduled'))}, {getDate(flightLeg.get('arrivalInformation').get('times').get('latestPublished'))}, {flightLeg.get('status')}, {flightLeg.get('restricted')}, {flightLeg.get('serviceType')}, {flightLeg.get('legStatusPublic')})")
                        await connection.execute("""
                            INSERT INTO ETAPEDUVOL (AERO_DPT, VOL, AERO_ARR, AVION, DPT_DATEINITIALE, DPT_DERNIEREDATE, ARR_DATEINITIALE, ARR_DERNIEREDATE, STATUS, RESTRICTED, AVANCEE, STATUSPUBLIC, SERVICE, SERVICENAME, TIMEZONEDIFF)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                            ON CONFLICT (AERO_DPT, VOL, AERO_ARR) DO UPDATE
                            SET AVION = $4, DPT_DATEINITIALE = $5, DPT_DERNIEREDATE = $6, ARR_DATEINITIALE = $7, ARR_DERNIEREDATE = $8, STATUS = $9, RESTRICTED = $10, AVANCEE = $11, STATUSPUBLIC = $12, SERVICE = $13, SERVICENAME = $14, TIMEZONEDIFF = $15
                        """, 
                            flightLeg.get("departureInformation").get("airport").get("code"), 
                            flight.get("id"), 
                            flightLeg.get("arrivalInformation").get("airport").get("code"),
                            flightLeg.get("aircraft").get("registration", None), 
                            dpt_dateinitiale,
                            dpt_dernieredate,
                            arr_dateinitiale,
                            arr_dernieredate,
                            status,
                            flightLeg.get("restricted"), 
                            flightLeg.get("completionPercentage"), 
                            flightLeg.get("legStatusPublic"),
                            flightLeg.get("serviceType"),
                            flightLeg.get("serviceTypeName"),
                            flightLeg.get("timeZoneDifference")
                        )

                        legs.append(
                            {
                                "aero_dpt": flightLeg.get("departureInformation").get("airport").get("code"),
                                "aero_arr": flightLeg.get("arrivalInformation").get("airport").get("code"),
                                "avion": flightLeg.get("aircraft").get("registration", None),
                                "dpt_dateinitiale": dpt_dateinitiale,
                                "dpt_dernieredate": dpt_dernieredate,
                                "arr_dateinitiale": arr_dateinitiale,
                                "arr_dernieredate": arr_dernieredate,
                                "status": status,
                                "restricted": flightLeg.get("restricted"),
                                "avancee": flightLeg.get("completionPercentage"),
                                "statuspublic": flightLeg.get("legStatusPublic"),
                                "service": flightLeg.get("serviceType"),
                                "servicename": flightLeg.get("serviceTypeName"),
                                "timezonediff": flightLeg.get("timeZoneDifference")
                            }
                        )

                    cleanFlights.append(
                        {
                            "code": flight.get("id"),
                            "datevol": flight.get("flightScheduleDate"),
                            "typetrajet": flight.get("haul"),
                            "route": flight.get("route"),
                            "flightLegs": legs
                        }
                    )

        self.nextFlights = cleanFlights


        if 0 <= datetime.now().hour < 1:
            await self.saveStats()


        self.logs.info("[CACHE] Données sauvegardées !")


    async def saveStats(self):
        """
        Sauvegarde des statistiques
        """
        self.logs.info("[CACHE] Sauvegarde des statistiques...")


        async with self.pool.acquire() as connection:
            nbvols = await connection.fetchval("SELECT COUNT(*) FROM vol")
            nbetapes = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol")
            nbavions = await connection.fetchval("SELECT COUNT(*) FROM avion")
            nbaeroports = await connection.fetchval("SELECT COUNT(*) FROM aeroport")
            nbetape_on_time = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol WHERE STATUS = 'ON_TIME'")
            nbetape_delayed_departure = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol WHERE STATUS LIKE 'DELAYED_DEPARTURE'")
            nbetape_delayed_arrival = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol WHERE STATUS = 'DELAYED_ARRIVAL'")
            nbetape_delayed = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol WHERE STATUS = 'DELAYED'")
            nbetape_cancelled = await connection.fetchval("SELECT COUNT(*) FROM etapeduvol WHERE STATUS = 'CANCELLED'")
            average_delay_departure = await connection.fetchval("SELECT AVG(EXTRACT(EPOCH FROM TO_TIMESTAMP(DPT_DERNIEREDATE, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"+\"TZH:TZM') -TO_TIMESTAMP(DPT_DATEINITIALE, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"+\"TZH:TZM'))) FROM etapeduvol WHERE STATUS LIKE 'DELAYED_DEPARTURE'")
            average_delay_arrival = await connection.fetchval("SELECT AVG(EXTRACT(EPOCH FROM TO_TIMESTAMP(ARR_DERNIEREDATE, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"+\"TZH:TZM') -TO_TIMESTAMP(ARR_DATEINITIALE, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"+\"TZH:TZM'))) FROM etapeduvol WHERE STATUS IN ('DELAYED_ARRIVAL', 'DELAYED')")
            gaz = 0.0

            self.logs.debug(f"[DB] [STATS] INSERT INTO historique VALUES ({datetime.now(), nbvols, nbetapes, nbavions, nbaeroports, nbetape_on_time, nbetape_delayed_departure, nbetape_delayed_arrival, nbetape_delayed, nbetape_cancelled, gaz})")
            await connection.execute(
                """
                    INSERT INTO historique VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (date) DO NOTHING
                """, 
                datetime.now(), 
                nbvols, 
                nbetapes, 
                nbavions, 
                nbaeroports, 
                nbetape_on_time, 
                nbetape_delayed_departure, 
                nbetape_delayed_arrival, 
                nbetape_delayed, 
                nbetape_cancelled, 
                round(average_delay_departure / 60, 2),
                round(average_delay_arrival / 60, 2),
                gaz
            )


        self.logs.info("[CACHE] Statistiques sauvegardées !")
