"""Plateforme sensor pour Inforoute 65."""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: Inforoute65DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for item in coordinator.data:
        pid = item.get("pid")
        tifid = item.get("tifid") or pid
        name = item.get("lib") or "Section de route inconnue"
        unique_id = f"inforoute65_{tifid}"

        entities.append(InforouteSectionSensor(
            coordinator=coordinator,
            item=item,
            name=name,
            unique_id=unique_id
        ))

    async_add_entities(entities, update_before_add=True)

class InforouteSectionSensor(CoordinatorEntity, SensorEntity):
    """Entité représentant une section de route."""

    def __init__(self, coordinator, item, name, unique_id):
        super().__init__(coordinator)
        self._item = item
        self._attr_name = name
        self._attr_unique_id = unique_id

    @property
    def state(self):
        # Exemple : on affiche la 'color' comme état
        return (self._item.get("color") or "").upper()

    @property
    def extra_state_attributes(self):
        return {
            "lib": self._item.get("lib"),
            "description": self._item.get("description"),
            "type_geom": self._item.get("type_geom"),
            "tifid": self._item.get("tifid"),
        }

    @property
    def device_info(self):
        pid = self._item.get("pid")
        tifid = self._item.get("tifid") or pid

        return {
            "identifiers": {(DOMAIN, f"inforoute65_{tifid}")},
            "name": self._item.get("lib") or "Route Inforoute 65",
            "manufacturer": "Ha-Py Region",
            "model": "Inforoute Sensor",
        }

    @property
    def icon(self):
        return "mdi:road-variant"
