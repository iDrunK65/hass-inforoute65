import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, DEFAULT_API_URL, DEFAULT_SCAN_INTERVAL
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]  # ou ["sensor", "button", etc.]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup via configuration.yaml, si besoin. Ici on ne l'utilise pas."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Chargement de l'intégration depuis l'UI."""
    # On récupère la valeur du scan_interval
    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    # On utilise l’URL fixée en dur
    api_url = DEFAULT_API_URL

    # On crée le coordinateur
    coordinator = Inforoute65DataUpdateCoordinator(
        hass,
        api_url,
        timedelta(minutes=scan_interval),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # On charge la/les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement de l'intégration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
