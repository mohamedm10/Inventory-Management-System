import secrets
import os

class Base:
    FLASK_APP = os.environ.get("FLASK_APP")
    SECRET_KEY = secrets.token_hex(16)
class Development(Base):
    FLASK_ENV= os.environ.get("FLASK_ENV")
    # DATABASE = os.environ.get("DATABASE")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:12345@localhost:5433/kiosk"

class Staging(Base):
    DATABASE = "d5c04cvapeivr1"
    POSTGRES_USER = "ruusozkswdaiez"
    POSTGRES_PASSWORD = "c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b"
    SQLALCHEMY_DATABASE_URI = "postgresql://ruusozkswdaiez:c9424fa337795052a1500084fa6b4442d12b3977458eeac2bba5a2300964783b@ec2-79-125-30-28.eu-west-1.compute.amazonaws.com:5432/d5c04cvapeivr1"