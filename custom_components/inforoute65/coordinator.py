import logging
import aiohttp
import async_timeout

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    DEFAULT_API_URL,
    DEFAULT_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

class Inforoute65DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordonnateur qui va chercher les données de l'API Inforoute."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=DEFAULT_SCAN_INTERVAL,  # Utiliser l'intervalle défini dans const.py
        )
        self.api_url = DEFAULT_API_URL

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(self.api_url)
                    data = await response.json()

            # data doit ressembler à { "OI": [...] }
            all_items = data.get("OI", [])

            # Filtrer les "POINT" si besoin
            filtered_items = [
                item for item in all_items
                if item.get("type_geom") != "POINT"
            ]

            return filtered_items

        except Exception as err:
            raise UpdateFailed(f"Erreur lors de la récupération des données: {err}") from err
