import os
import logging
import logging.handlers


class Logger:
    """
    Classe pour gérer les logs
    """
    def __init__(self, file: str) -> None:
        """
        Initialisation du logger
        """
        self.file = file

        self.logsPath = os.path.join(f"{os.getcwd()}", 'logs')
        if not os.path.exists(self.logsPath):
            os.makedirs(self.logsPath)

        self.logger = logging.getLogger(f"AirFranceKLMAPI - {self.file}")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.handlers.RotatingFileHandler(
            filename=f"{self.logsPath}/{self.file}.log",
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,
            backupCount=5,
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Logger initialisé")
    

    def info(self, message: str) -> None:
        """
        Log un message d'information
        
        :param message: Le message
        """
        self.logger.info(message)

    
    def warning(self, message: str) -> None:
        """
        Log un message d'avertissement

        :param message: Le message
        """
        self.logger.warning(message)

    
    def error(self, message: str) -> None:
        """
        Log un message d'erreur

        :param message: Le message
        """
        self.logger.error(message)

    
    def critical(self, message: str) -> None:
        """
        Log un message critique

        :param message: Le message
        """
        self.logger.critical(message)

    
    def debug(self, message: str) -> None:
        """
        Log un message de débogage

        :param message: Le message
        """
        self.logger.debug(message)
