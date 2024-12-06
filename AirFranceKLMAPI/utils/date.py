import datetime

from pytz import timezone


def getDateRange():
    """
    Renvoie une plage de dates de 30 minutes avant et 1h après l'heure actuelle
    
    :return: La plage de dates
    """
    now = datetime.datetime.now(tz=timezone("Europe/Paris"))

    before = now - datetime.timedelta(minutes=30)
    after = now + datetime.timedelta(hours=1)

    before_str = before.strftime("%Y-%m-%dT%H:%M:%SZ")
    after_str = after.strftime("%Y-%m-%dT%H:%M:%SZ")

    return (before_str, after_str)


def getDate(date: str) -> str:
    """
    Convertir la date

    :param date: Date à convertir
    :return: str
    """
    if len(date) == 10:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
