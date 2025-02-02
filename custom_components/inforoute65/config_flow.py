import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

class Inforoute65ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration pour Inforoute 65."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Unique étape de config."""
        errors = {}

        if user_input is not None:
            # On crée l'entrée de configuration dès que l’utilisateur valide le champ
            return self.async_create_entry(
                title="Inforoute 65",
                data=user_input
            )

        # On ne demande QUE le scan_interval, imposant un minimum de 10
        data_schema = vol.Schema({
            vol.Required(
                "scan_interval",
                default=DEFAULT_SCAN_INTERVAL
            ): vol.All(int, vol.Range(min=10))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Retourne la gestion des options (facultatif)."""
        return Inforoute65OptionsFlow(config_entry)


class Inforoute65OptionsFlow(config_entries.OptionsFlow):
    """Gestion des options, si on veut laisser l’utilisateur modifier le scan_interval après coup."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # On relit l'intervalle actuel pour le proposer en défaut
        current_interval = self.config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

        data_schema = vol.Schema({
            vol.Required("scan_interval", default=current_interval): vol.All(int, vol.Range(min=10))
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )
