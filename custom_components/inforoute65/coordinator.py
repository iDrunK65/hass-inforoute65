import logging
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class Inforoute65DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordonnateur pour Inforoute 65."""

    def __init__(self, hass: HomeAssistant, api_url: str, update_interval: timedelta) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Inforoute 65 Coordinator",
            update_interval=update_interval,
        )
        self.api_url = api_url

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    resp = await session.get(self.api_url)
                    data = await resp.json(content_type=None)

            all_items = data.get("OI", [])
            # Filtrer si besoin
            filtered_items = [item for item in all_items if item.get("type_geom") != "POINT"]
            return filtered_items

        except Exception as err:
            raise UpdateFailed(f"Erreur: {err}") from err
