"""Constants for PVOutput Uploader integration."""

DOMAIN = "pvoutput_uploader"

PVOUTPUT_URL = "https://pvoutput.org/service/r2/addstatus.jsp"

CONF_NAME = "name"
CONF_API_KEY = "api_key"
CONF_SYSTEM_ID = "system_id"
CONF_POWER_ENTITY = "power_entity"
CONF_ENERGY_ENTITY = "energy_entity"
CONF_TEMPERATURE_ENTITY = "temperature_entity"
CONF_UPLOAD_INTERVAL = "upload_interval"
CONF_START_TIME = "start_time"
CONF_END_TIME = "end_time"

DEFAULT_UPLOAD_INTERVAL = 5
DEFAULT_START_TIME = "06:00"
DEFAULT_END_TIME = "22:00"
