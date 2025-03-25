"""Configuration flow pour Inforoute 65."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

class Inforoute65ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Inforoute 65", data=user_input)

        data_schema = vol.Schema({
            vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(int, vol.Range(min=10))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return Inforoute65OptionsFlow(config_entry)

class Inforoute65OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        super().__init__()
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # L'utilisateur valide le formulaire d'options
            return self.async_create_entry(title="", data=user_input)

        # Récupère la valeur courante de scan_interval pour la proposer en défaut
        current_interval = self._entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

        data_schema = vol.Schema({
            vol.Required("scan_interval", default=current_interval): vol.All(int, vol.Range(min=10))
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )
