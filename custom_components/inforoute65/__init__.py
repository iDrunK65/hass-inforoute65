from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import InforouteDataUpdateCoordinator

async def async_setup(hass: HomeAssistant, config: dict):
    """Chargement via configuration.yaml (optionnel).
       Mieux vaut passer par async_setup_entry si on fait un config_flow.
    """
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Chargement quand l'utilisateur ajoute l'intégration (config_flow ou configuration.yaml)."""
    coordinator = InforouteDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    # Stocke le coordinator dans hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # On charge la ou les plateformes (sensor, etc.)
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement de l’intégration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
