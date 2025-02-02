import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Inforoute65DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities
) -> None:
    """
    Configure la plateforme sensor lors du chargement de l’intégration.
    Crée 3 entités distinctes (Circulation, Emplacement, Diagnostics)
    par section de route.
    """
    coordinator: Inforoute65DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for item in coordinator.data:
        pid = item.get("pid")
        tifid = item.get("tifid") or pid
        lib = item.get("lib", "Route inconnue")

        unique_base = f"{tifid}"  # base pour l'unique_id de chaque sensor

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

        # 3) Capteur "Diagnostics" (marqué comme diagnostic dans l'UI)
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
    """
    Classe de base pour partager le device_info.
    Chaque sensor hérite de cette classe et définit son propre 'state' et 'attributes'.
    """

    def __init__(self, coordinator, item, name, unique_id, device_name):
        super().__init__(coordinator)
        self._item = item
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._device_name = device_name

    @property
    def device_info(self):
        """
        Retourne le même "appareil" pour les 3 capteurs de la même section de route,
        en utilisant pid/tifid comme identifiant unique.
        """
        # On peut prendre pid ou tifid pour l'identifiant du device
        pid = self._item.get("pid")
        tifid = self._item.get("tifid") or pid

        return {
            "identifiers": {(DOMAIN, f"{DOMAIN}_{tifid}")},
            "name": self._device_name,  # ex. "COL DE SPANDELLES"
            "manufacturer": "Ha-Py Region",
            "model": "Inforoute Sensor",
        }


class InforouteSectionCirculationSensor(BaseInforouteSensor):
    """
    Capteur "Circulation" :
      - state = level_title
      - attributs = level_color, level, level_title
    """

    @property
    def state(self) -> str:
        """Retourne 'level_title' comme état principal."""
        return self._item.get("level_title") or "Inconnu"

    @property
    def extra_state_attributes(self) -> dict:
        """Inclut la couleur brute, le niveau (C1, C2...), etc."""
        return {
            "level_color": self._item.get("level_color"),
            "level": self._item.get("level"),
            "level_title": self._item.get("level_title"),
        }

    @property
    def icon(self) -> str:
        """Icône personnalisée pour la circulation."""
        return "mdi:car-brake-alert"


class InforouteSectionEmplacementSensor(BaseInforouteSensor):
    """
    Capteur "Emplacement" :
      - state = address
      - attributs = lat, lng, address
    """

    @property
    def state(self) -> str:
        """Retourne l'adresse comme état."""
        return self._item.get("address") or "Adresse inconnue"

    @property
    def extra_state_attributes(self) -> dict:
        """Inclut la lat, lng, address."""
        return {
            "lat": self._item.get("lat"),
            "lng": self._item.get("lng"),
            "address": self._item.get("address"),
        }

    @property
    def icon(self) -> str:
        """Icône personnalisée pour l'emplacement."""
        return "mdi:map-marker"


class InforouteSectionDiagnosticSensor(BaseInforouteSensor):
    """
    Capteur "Diagnostics" :
      - entity_category = EntityCategory.DIAGNOSTIC
      - state = tifid (ou None)
      - attributs = tifid, equipment, poid
    """

    @property
    def state(self) -> str:
        """Retourne tifid comme état principal."""
        return self._item.get("tifid") or "N/A"

    @property
    def extra_state_attributes(self) -> dict:
        """Inclut tifid, equipment, poid."""
        return {
            "tifid": self._item.get("tifid"),
            "equipment": self._item.get("equipement"),
            "poids": self._item.get("poids"),  # selon la donnée renvoyée par l'API
        }

    @property
    def entity_category(self):
        """
        Marque ce capteur comme "Diagnostic",
        il sera listé dans la catégorie Diagnostiques dans l'UI.
        """
        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Icône pour le diagnostic."""
        return "mdi:information-outline"
