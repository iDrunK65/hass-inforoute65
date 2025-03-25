"""Initialisation de l’intégration Inforoute 65."""

import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS, DEFAULT_SCAN_INTERVAL, DEFAULT_API_URL
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup via configuration.yaml (non utilisé ici)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Chargement de l’intégration quand l’utilisateur l’ajoute via l’UI (config_flow).
    """
    # Récupérer l’intervalle en minutes (entier) depuis la config
    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    update_interval = timedelta(minutes=scan_interval)

    # URL non configurable
    api_url = DEFAULT_API_URL

    # Créer le coordinator
    coordinator = Inforoute65DataUpdateCoordinator(
        hass,
        api_url,
        update_interval
    )
    await coordinator.async_config_entry_first_refresh()

    # Stocker le coordinator dans hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Charger la/les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement de l’intégration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
