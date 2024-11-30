import os
import requests
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Healthcheck Worker")

# Environment variables
cf_account_id: str | None = os.getenv("CF_ACCOUNT_ID")
cf_api_token: str | None = os.getenv("CF_API_TOKEN")
cf_tunnel_id: str | None = os.getenv("CF_TUNNEL_ID")
sp_page_id: str | None = os.getenv("SP_PAGE_ID")
sp_api_token: str | None = os.getenv("SP_API_TOKEN")
sp_component_id: str | None = os.getenv("SP_COMPONENT_ID")

# API Base urls
cf_api_base_url = "https://api.cloudflare.com/client/v4/accounts"
sp_api_base_url = "https://api.statuspage.io/v1/pages"

# Check for missing environment variables
required_env_vars = [
    "CF_ACCOUNT_ID",
    "CF_API_TOKEN",
    "CF_TUNNEL_ID",
    "SP_PAGE_ID",
    "SP_API_TOKEN",
    "SP_COMPONENT_ID",
]

missing_vars = [var for var in required_env_vars if os.getenv(var) is None]
if missing_vars:
    msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(msg)
    raise EnvironmentError(msg)


class SpStatus(str, Enum):
    EMPTY = ""
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    DEGRADED_PERFORMANCE = "degraded_performance"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"


class CfStatus(str, Enum):
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    DOWN = "down"


cf_sp_status_mapping: dict[CfStatus, SpStatus] = {
    CfStatus.INACTIVE: SpStatus.EMPTY,
    CfStatus.DEGRADED: SpStatus.DEGRADED_PERFORMANCE,
    CfStatus.HEALTHY: SpStatus.OPERATIONAL,
    CfStatus.DOWN: SpStatus.MAJOR_OUTAGE,
}


def send_request(method: str, url: str, headers: dict, payload=None):
    try:
        logger.info(f"Sending {method} request to URL: {url}")
        response = requests.request(
            method, url, headers=headers, allow_redirects=False, timeout=250
        )

        if response.status_code != 200:
            logger.error(
                f"Failed request. HTTP Status Code: {response.status_code}. Response: {response.text}"
            )
            response.raise_for_status()

        logger.info(f"Successfully completed {method} request to URL: {url}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"A network error occurred: {e}")
        raise


def get_tunnel():
    url = f"{cf_api_base_url}/{cf_account_id}/cfd_tunnel/{cf_tunnel_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cf_api_token}",
    }
    return send_request("GET", url, headers)


def get_component():
    url = f"{sp_api_base_url}/{sp_page_id}/components/{sp_component_id}"
    headers = {"Authorization": f"OAuth {sp_api_token}"}
    return send_request("GET", url, headers)


def patch_component(status: SpStatus):
    url = f"{sp_api_base_url}/{sp_page_id}/components/{sp_component_id}"
    payload = json.dumps({"component": {"status": f"{status.value}"}})
    headers = {
        "Authorization": f"OAuth {sp_api_token}",
        "Content-Type": "application/json",
    }
    return send_request("PATCH", url, headers, payload)


def main():
    try:
        logger.info("Starting status synchronization script.")

        component = get_component()
        component_status = SpStatus(component["status"])
        logger.info(f"Current component status: {component_status.value}")

        if component_status == SpStatus.UNDER_MAINTENANCE:
            logger.info("Component is under maintenance. No changes will be made.")
            return

        # Get the current tunnel status from Cloudflare
        tunnel = get_tunnel()
        if "result" not in tunnel or "status" not in tunnel["result"]:
            raise ValueError("Unexpected response format from Cloudflare API")
        tunnel_status: CfStatus = CfStatus(tunnel["result"]["status"])
        logger.info(f"Current tunnel status: {tunnel_status.value}")

        new_status: SpStatus = cf_sp_status_mapping[tunnel_status]
        if new_status != component_status:
            logger.info(
                f"Status change detected. Updating component status to: {new_status.value}"
            )
            patch_component(new_status)
        else:
            logger.info("No status change detected. No update necessary.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
