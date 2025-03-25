"""Constants for the Inforoute 65 integration."""

from typing import Final
from homeassistant.const import Platform

DOMAIN: Final = "inforoute65"
PLATFORMS: Final = [Platform.BUTTON, Platform.SENSOR]

DEFAULT_NAME: Final = "Inforoute 65"
DEFAULT_SCAN_INTERVAL: Final = 10

DEFAULT_API_URL = (
    "https://inforoute.ha-py.fr/myd/proxy.php?cluster=&tifid="
    "&type=30.09;31.02;32.01;30.06&theme=&categorie=31.04.02;30.05.02"
)
