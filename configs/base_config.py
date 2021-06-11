import secrets
import os
class Base:
    FLASK_APP = os.environ.get("FLASK_APP")
    SECRET_KEY = secrets.token_hex(16)
class Development(Base):
    FLASK_ENV= os.environ.get("FLASK_ENV")
    DATABASE = os.environ.get("DATABASE")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

class Staging(Base):
    DATABASE = "d5c04cvapeivr1"
    POSTGRES_USER = "ruusozkswdaiez"
    POSTGRES_PASSWORD = "c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b"