import os

TESTDATA = os.path.join(os.path.dirname(__file__), 'testdata')


class Settings(dict):
    def getint(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def getfloat(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def with_defaults(cls):
        settings = {
            "OVERLAP": 0.0,
            "LATITUDE": 50,
            "LONGITUDE": 5,
            "CONFIDENCE": 0.7,
            "DATABASE_LANG": "en",
            "PRIVACY_THRESHOLD": 0,
            "EXTRACTION_LENGTH": 6,
            "MODEL": "BirdNET_GLOBAL_6K_V2.4_Model_FP16",
            "DATA_MODEL_VERSION": 1,
            "SENSITIVITY": 1.25,
            "SF_THRESH": 0.003,
            "APPRISE_NOTIFICATION_TITLE": "New backyard bird!",
            "APPRISE_NOTIFY_EACH_DETECTION": "0",
            "APPRISE_NOTIFY_NEW_SPECIES": "0",
            "APPRISE_NOTIFY_NEW_SPECIES_EACH_DAY": "0",
            "APPRISE_MINIMUM_SECONDS_BETWEEN_NOTIFICATIONS_PER_SPECIES": "0",
            "APPRISE_ONLY_NOTIFY_SPECIES_NAMES": "",
            "APPRISE_ONLY_NOTIFY_SPECIES_NAMES_2": "",
            "BIRDNETPI_URL": "",
        }
        return cls(settings)
