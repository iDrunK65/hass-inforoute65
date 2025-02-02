"""Initialisation de l'intégration Inforoute 65."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """
    Chargement si on utilise configuration.yaml (optionnel).
    Dans cet exemple, on fait tout via config_flow, donc on renvoie simplement True.
    """
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Chargement de l'intégration quand l'utilisateur l'ajoute via l'UI (config_flow).
    """
    # Récupère les données fournies lors de la configuration (config_flow)
    api_url = entry.data.get("api_url")
    scan_interval = entry.data.get("scan_interval", 10)

    # Crée une instance de notre coordinateur de données, avec l'URL et l'intervalle voulu
    coordinator = Inforoute65DataUpdateCoordinator(
        hass,
        api_url,
        timedelta(minutes=scan_interval),
    )

    # Première mise à jour (peut lever une exception si l'API est inaccessible)
    await coordinator.async_config_entry_first_refresh()

    # On stocke le coordinateur dans hass.data pour y accéder dans d'autres fichiers
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # On charge les plateformes déclarées (ex : "sensor")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Déchargement de l'intégration.
    (Par exemple si l'utilisateur la supprime depuis l'UI).
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
