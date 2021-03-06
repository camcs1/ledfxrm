"""Adds config flow for Ledfxrm."""
from homeassistant import config_entries
from homeassistant.core import callback
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol
import logging
import requests
from custom_components.ledfxrm.const import (  # pylint: disable=unused-import
    CONF_HOST,
    CONF_PORT,
    CONF_START,
    CONF_STOP,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_SUBDEVICES,
    CONF_SHOW_BLADELIGHT,
    CONF_START_METHOD,
    CONF_STOP_METHOD,
    CONF_START_BODY,
    CONF_STOP_BODY,
    CONF_ADVANCED,
    BINARY_SENSOR,
    SENSOR,
    SWITCH,
    LIGHT,
    DOMAIN,
    PLATFORMS,
)


class LedfxrmFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Ledfxrm."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            if CONF_HOST in user_input:
                name, version = await self.get_rest_status(
                    user_input[CONF_HOST], user_input[CONF_PORT]
                )
                if hasattr(self, "data_attr"):
                    logging.warning(
                        "WHYYYY 111 %s ----- %s ",
                        user_input[CONF_SHOW_SUBDEVICES],
                        user_input[CONF_SHOW_BLADELIGHT],
                    )
                    self.data_attr[CONF_HOST] = user_input[CONF_HOST]
                    self.data_attr[CONF_PORT] = user_input[CONF_PORT]
                    self.data_attr["name"] = name
                    self.data_attr["version"] = version
                    self.data_attr[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
                    self.data_attr[CONF_SHOW_SUBDEVICES] = user_input[
                        CONF_SHOW_SUBDEVICES
                    ]
                    self.data_attr[CONF_SHOW_BLADELIGHT] = user_input[
                        CONF_SHOW_BLADELIGHT
                    ]
                else:
                    self.data_attr = {}
                    self.data_attr[CONF_HOST] = user_input[CONF_HOST]
                    self.data_attr[CONF_PORT] = user_input[CONF_PORT]
                    self.data_attr["name"] = name
                    self.data_attr["version"] = version
                    self.data_attr[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
                    self.data_attr[CONF_SHOW_SUBDEVICES] = user_input[
                        CONF_SHOW_SUBDEVICES
                    ]
                    self.data_attr[CONF_SHOW_BLADELIGHT] = user_input[
                        CONF_SHOW_BLADELIGHT
                    ]

                if user_input[CONF_ADVANCED] is True:
                    return await self._show_config_form_2(user_input)
                return self.async_create_entry(
                    title=self.data_attr["name"], data=self.data_attr
                )
            if CONF_START in user_input:
                if hasattr(self, "data_attr"):
                    self.data_attr[CONF_START] = user_input[CONF_START]
                    self.data_attr[CONF_START_METHOD] = user_input[CONF_START_METHOD]
                    self.data_attr[CONF_STOP_METHOD] = user_input[CONF_STOP_METHOD]
                    self.data_attr[CONF_START_BODY] = user_input[CONF_START_BODY]
                    self.data_attr[CONF_STOP_BODY] = user_input[CONF_STOP_BODY]
                    self.data_attr[CONF_STOP] = user_input[CONF_STOP]
            if hasattr(self, "data_attr"):
                # logging.warning("DATA: %s", self.data_attr)
                return self.async_create_entry(
                    title=self.data_attr["name"], data=self.data_attr
                )
            return await self._show_config_form(user_input)
        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return LedfxrmOptionsFlowHandler(config_entry)

    async def _show_config_form(
        self, user_input=None
    ):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.1.56"): str,
                    vol.Required(CONF_PORT, default=8888): int,
                    vol.Optional(CONF_SCAN_INTERVAL, default=300): int,
                    vol.Optional(CONF_SHOW_SUBDEVICES, default=False): bool,
                    vol.Optional(CONF_ADVANCED, default=False): bool,
                    vol.Optional(CONF_SHOW_BLADELIGHT, default=False): bool,
                }
            ),
            errors=self._errors,
        )

    async def _show_config_form_2(
        self, user_input=None
    ):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_START_METHOD, default="GET"): vol.In(
                        ["GET", "PUT", "POST", "DELETE"]
                    ),
                    vol.Optional(CONF_START_METHOD, default="GET"): vol.In(
                        ["GET", "PUT", "POST", "DELETE"]
                    ),
                    vol.Optional(
                        CONF_START, default="192.168.1.56:23002/?ledfxstart"
                    ): str,
                    vol.Optional(CONF_START_BODY, default=""): str,
                    vol.Optional(CONF_STOP_METHOD, default="GET"): vol.In(
                        ["GET", "PUT", "POST", "DELETE"]
                    ),
                    vol.Optional(CONF_STOP_BODY, default=""): str,
                    vol.Optional(
                        CONF_STOP, default="192.168.1.56:23002/?ledfxstop"
                    ): str,
                }
            ),
            errors=self._errors,
        )

    async def get_rest_status(self, thehost, theport):
        """Return true if credentials is valid."""
        loop = asyncio.get_event_loop()
        url = "http://" + thehost + ":" + str(theport) + "/api/info"
        async with aiohttp.ClientSession(loop=loop, trust_env=True) as session:
            async with session.get(url, ssl=False) as resp:
                rest_info = await resp.json()
                name = rest_info["name"]
                version = rest_info["version"]
                # logging.warning('Config for %s | Version: %s', name, version)
        # return yz
        return name, version


class LedfxrmOptionsFlowHandler(config_entries.OptionsFlow):
    """Ledfxrm config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    # vol.Optional(CONF_SCAN_INTERVAL, default=self.options.get(CONF_SCAN_INTERVAL, 300)): int,
                    vol.Required(
                        BINARY_SENSOR, default=self.options.get(BINARY_SENSOR, True)
                    ): bool,
                    vol.Required(SENSOR, default=self.options.get(SENSOR, True)): bool,
                    vol.Required(SWITCH, default=self.options.get(SWITCH, True)): bool,
                    vol.Required(LIGHT, default=self.options.get(LIGHT, True)): bool,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_HOST), data=self.options
        )
