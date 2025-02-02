"""Sensor platform for the Inforoute 65 integration."""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InforouteDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Correspondance des couleurs à (niveau, texte)
COLOR_MAP = {
    "00FF00": ("C1", "Circulation normale"),
    "FFFF00": ("C2", "Circulation délicate"),
    "FF0000": ("C3", "Circulation difficile"),
    "000000": ("C4", "Circulation impossible"),
    "800080": ("FH", "Route fermée l'hiver"),
    "0000FF": ("DTV", "Déviation tous véhicules"),
    "00FFFF": ("DVL", "Déviation VL seuls"),
    "993300": ("BD1", "Barrière de dégel limitation 12T"),
    "FF00FF": ("BD2", "Barrière de dégel limitation 7,5T"),
    "969696": ("BD3", "Barrière de dégel sans limitation"),
}

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities
) -> None:
    """
    Configure la plateforme sensor lors du chargement de l’intégration.
    Crée une entité pour chaque section de route retournée par le coordinator.
    """
    coordinator: InforouteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for item in coordinator.data:
        pid = item.get("pid")
        tifid = item.get("tifid") or pid  # si pas de tifid, on prend le pid

        name = item.get("lib", "Section de route inconnue")
        unique_id = f"{DOMAIN}_{tifid}"  # ID unique pour l'entité

        entities.append(InforouteSectionSensor(
            coordinator=coordinator,
            item=item,
            name=name,
            unique_id=unique_id,
            tifid=tifid
        ))

    async_add_entities(entities, update_before_add=True)


class InforouteSectionSensor(CoordinatorEntity, SensorEntity):
    """Représente une section de route Inforoute 65 sous forme d’entité 'Sensor'."""

    def __init__(
            self,
            coordinator: InforouteDataUpdateCoordinator,
            item: dict,
            name: str,
            unique_id: str,
            tifid: str,
    ) -> None:
        """Initialise l'entité."""
        super().__init__(coordinator)
        self._item = item
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._tifid = tifid

    @property
    def state(self) -> str:
        """
        Valeur principale de l’entité (le state).
        Ici, on reprend la couleur en guise d’état.
        """
        return (self._item.get("color") or "").upper()

    @property
    def extra_state_attributes(self) -> dict:
        """
        Attributs supplémentaires, incluant la correspondance couleur -> niveau -> texte.
        """
        color = (self._item.get("color") or "").upper()
        niveau, texte = COLOR_MAP.get(color, ("??", "Inconnu"))

        return {
            "level_color": color,
            "level": niveau,
            "level_title": texte,
            "equipment": self._item.get("equipement"),
            "address": self._item.get("address"),
            "lat": self._item.get("lat"),
            "lng": self._item.get("lng"),
            "tifid": self._item.get("tifid"),
        }

    @property
    def device_info(self) -> dict:
        """
        Crée un 'Device' distinct dans l’UI de Home Assistant,
        associé à cette section de route.
        """
        return {
            "identifiers": {(DOMAIN, f"{DOMAIN}_{self._tifid}")},
            "name": self._attr_name,
            "manufacturer": "Ha-Py Region",
            "model": "Inforoute Sensor",
        }

    @property
    def icon(self) -> str:
        """
        Icône (peut éventuellement dépendre de la couleur ou du niveau).
        """
        return "mdi:road-variant"
