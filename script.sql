CREATE TABLE AEROPORT (
    CODE CHAR(3) NOT NULL PRIMARY KEY,
    NOM VARCHAR(100) NOT NULL,
    NOMLTR VARCHAR(100),
    VILLE VARCHAR(100),
    PAYS VARCHAR(80),
    LATITUDE FLOAT,
    LONGITUDE FLOAT DEFAULT NULL
);


CREATE TABLE COMPAGNIE (
    CODE VARCHAR(10) NOT NULL PRIMARY KEY,
    NOM VARCHAR(100)
);


CREATE TABLE AVION (
    CODE VARCHAR(10) NOT NULL PRIMARY KEY,
    TYPECODE VARCHAR(5),
    TYPENOM VARCHAR(80),
    WIFI BOOLEAN,
    SATELLITE BOOLEAN,
    COMPAGNIE VARCHAR(10) NULL,
    CONSTRAINT FK_APPARTENIR FOREIGN KEY (COMPAGNIE) REFERENCES COMPAGNIE (CODE)
);


CREATE TABLE VOL (
    CODE VARCHAR(20) NOT NULL PRIMARY KEY,
    DATEVOL DATE,
    TYPETRAJET VARCHAR(50),
    ROUTE JSON
);


CREATE TABLE ETAPEDUVOL (
    AERO_DPT CHAR(3) NOT NULL,
    VOL VARCHAR(20) NOT NULL,
    AERO_ARR CHAR(3) NOT NULL,
    AVION VARCHAR(10),
    DPT_DATEINITIALE VARCHAR(30),
    DPT_DERNIEREDATE VARCHAR(30),
    ARR_DATEINITIALE VARCHAR(30),
    ARR_DERNIEREDATE VARCHAR(30),
    STATUS VARCHAR(30),
    RESTRICTED BOOLEAN,
    AVANCEE VARCHAR(30),
    STATUSPUBLIC VARCHAR(50),
    SERVICE VARCHAR(50),
    SERVICENAME VARCHAR(100),
    TIMEZONEDIFF VARCHAR(50),
    CONSTRAINT PK_ETAPEDUVOL PRIMARY KEY (AERO_DPT, VOL, AERO_ARR),
    CONSTRAINT FK_DECOLLER FOREIGN KEY (AERO_DPT) REFERENCES AEROPORT (CODE),
    CONSTRAINT FK_COMPOSER FOREIGN KEY (VOL) REFERENCES VOL (CODE),
    CONSTRAINT FK_ARRIVER FOREIGN KEY (AERO_ARR) REFERENCES AEROPORT (CODE),
    CONSTRAINT FK_UTILISER FOREIGN KEY (AVION) REFERENCES AVION (CODE)
);
