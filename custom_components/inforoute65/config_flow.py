"""Config flow for Inforoute 65 integration."""
import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class Inforoute65ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inforoute 65."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gère l'étape de configuration via l'UI."""
        errors = {}

        if user_input is not None:
            # L'utilisateur a validé le formulaire
            return self.async_create_entry(
                title="Inforoute 65",
                data=user_input
            )

        # Formulaire à afficher
        data_schema = vol.Schema({
            vol.Required("scan_interval", default=10): vol.All(int, vol.Range(min=10)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Si on veut gérer des options avancées plus tard."""
        return Inforoute65OptionsFlowHandler(config_entry)


class Inforoute65OptionsFlowHandler(config_entries.OptionsFlow):
    """Gestion des options éventuelles."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Options modifiables après coup, si besoin."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Par exemple, on peut redemander le scan_interval ici
        data_schema = vol.Schema({
            vol.Required("scan_interval", default=self.config_entry.data.get("scan_interval", 10)):
                vol.All(int, vol.Range(min=10)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )
