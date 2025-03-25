"""Plateforme button pour Inforoute 65."""

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """
    Configure la plateforme button lors du chargement de l’intégration.
    On crée un unique bouton pour forcer le refresh.
    """
    coordinator: Inforoute65DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    button_entity = InforouteRefreshButton(
        coordinator=coordinator,
        entry_id=entry.entry_id,
    )

    async_add_entities([button_entity])


class InforouteRefreshButton(CoordinatorEntity, ButtonEntity):
    """
    Bouton permettant de déclencher manuellement un refresh du Coordinator.
    """

    def __init__(self, coordinator: Inforoute65DataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_force_refresh"
        self._attr_name = "Actualiser"

    async def async_press(self) -> None:
        """Action effectuée quand l'utilisateur appuie sur le bouton."""
        _LOGGER.info("Bouton de rafraîchissement Inforoute activé.")
        # Demander un refresh immédiat du coordinator
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """
        Optionnel : rattacher le bouton au même appareil que vos capteurs,
        si vous souhaitez qu'il apparaisse dans le même 'device'.
        """
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
        }
