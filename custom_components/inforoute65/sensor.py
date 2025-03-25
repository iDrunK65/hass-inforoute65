import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Correspondance des couleurs -> (niveau, texte)
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
    coordinator: Inforoute65DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for item in coordinator.data:
        pid = item.get("pid")
        tifid = item.get("tifid") or pid
        lib = item.get("lib", "Route inconnue")
        unique_base = f"{tifid}"

        # 1) Capteur "Circulation"
        sensors.append(
            InforouteSectionCirculationSensor(
                coordinator=coordinator,
                item=item,
                name=f"Circulation {lib}",
                unique_id=f"{unique_base}_circulation",
                device_name=lib,
            )
        )

        # 2) Capteur "Emplacement"
        sensors.append(
            InforouteSectionEmplacementSensor(
                coordinator=coordinator,
                item=item,
                name=f"Emplacement {lib}",
                unique_id=f"{unique_base}_emplacement",
                device_name=lib,
            )
        )

        # 3) Capteur "Diagnostics"
        sensors.append(
            InforouteSectionDiagnosticSensor(
                coordinator=coordinator,
                item=item,
                name=f"Diagnostics {lib}",
                unique_id=f"{unique_base}_diagnostics",
                device_name=lib,
            )
        )

    async_add_entities(sensors, update_before_add=True)

class BaseInforouteSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, item, name, unique_id, device_name):
        super().__init__(coordinator)
        self._item = item
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._device_name = device_name

    @property
    def device_info(self):
        pid = self._item.get("pid")
        tifid = self._item.get("tifid") or pid

        return {
            "identifiers": {(DOMAIN, f"{DOMAIN}_{tifid}")},
            "name": self._device_name,
            "manufacturer": "Ha-Py Region",
            "model": "Inforoute Sensor",
        }

class InforouteSectionCirculationSensor(BaseInforouteSensor):
    """
    Affiche un état en fonction de la couleur, dérivée de l'API (item["color"]).
    On mappe la couleur via COLOR_MAP pour obtenir (niveau, texte).
    """

    @property
    def state(self):
        # On calcule le texte en se basant sur la couleur
        color = (self._item.get("color") or "").upper()
        _, texte = COLOR_MAP.get(color, ("??", "Inconnu"))
        # L'état principal sera le texte, ex: "Circulation normale"
        return texte

    @property
    def extra_state_attributes(self):
        # On récupère la couleur, cherche le niveau+texte, et on renvoie tout
        color = (self._item.get("color") or "").upper()
        niveau, texte = COLOR_MAP.get(color, ("??", "Inconnu"))
        return {
            "level_color": color,
            "level": niveau,
            "level_title": texte,
        }

    @property
    def icon(self) -> str:
        return "mdi:car-brake-alert"

class InforouteSectionEmplacementSensor(BaseInforouteSensor):
    @property
    def state(self):
        return self._item.get("address") or "Adresse inconnue"

    @property
    def extra_state_attributes(self):
        return {
            "lat": self._item.get("lat"),
            "lng": self._item.get("lng"),
            "address": self._item.get("address"),
        }

    @property
    def icon(self) -> str:
        return "mdi:map-marker"

class InforouteSectionDiagnosticSensor(BaseInforouteSensor):
    @property
    def state(self):
        return self._item.get("tifid") or "N/A"

    @property
    def extra_state_attributes(self):
        return {
            "tifid": self._item.get("tifid"),
            "equipment": self._item.get("equipement"),
            "poids": self._item.get("poids"),
        }

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        return "mdi:information-outline"
