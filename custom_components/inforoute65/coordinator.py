"""Coordinator for the Inforoute 65 integration."""

import logging
import aiohttp
import async_timeout

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


class Inforoute65DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordonnateur qui va chercher les données de l'API Inforoute 65."""

    def __init__(
            self,
            hass: HomeAssistant,
            api_url: str,
            update_interval: timedelta,
    ) -> None:
        """
        Initialize the coordinator.
        :param hass: Référence vers l’instance Home Assistant
        :param api_url: URL de l’API Inforoute 65
        :param update_interval: Fréquence de rafraîchissement (timedelta)
        """
        super().__init__(
            hass,
            _LOGGER,
            name="Inforoute 65 Coordinator",
            update_interval=update_interval,
        )
        self.api_url = api_url

    async def _async_update_data(self) -> dict:
        """
        Fetch the latest data from the Inforoute 65 API.
        Returns a list or dict of items to be consumed by entities.
        """
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(self.api_url)
                    data = await response.json()

            # "data" devrait ressembler à { "OI": [ ... ] }
            all_items = data.get("OI", [])

            # Filtrer les objets "POINT" si vous ne les voulez pas
            filtered_items = [
                item for item in all_items
                if item.get("type_geom") != "POINT"
            ]

            return filtered_items

        except Exception as err:
            raise UpdateFailed(f"Erreur lors de la récupération des données: {err}") from err
