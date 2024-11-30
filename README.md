# Cloudflare Tunnel Status to Statuspage Sync

This repository hosts a Python script that synchronizes the status of a Cloudflare tunnel with a component on Statuspage. The purpose is to automate status updates for your infrastructure by reflecting the current status of a Cloudflare tunnel directly to a Statuspage component.

## Features
- **Cloudflare Tunnel Status Check**: Fetches the status of a specified Cloudflare tunnel.
- **Statuspage Integration**: Updates a specified Statuspage component based on the Cloudflare tunnel status.
- **Automatic Mapping**: Maps Cloudflare tunnel statuses to appropriate Statuspage component statuses for easy tracking.

## Prerequisites
- **Python 3.8 or higher**
- **Environment Variables**: The script requires several environment variables to be set up for proper functioning.

### Required Environment Variables
- `CF_ACCOUNT_ID`: Your Cloudflare Account ID.
- `CF_API_TOKEN`: The API token for accessing Cloudflare APIs.
- `CF_TUNNEL_ID`: The Tunnel ID for the Cloudflare tunnel you want to monitor.
- `SP_PAGE_ID`: The Statuspage page ID where your component resides.
- `SP_API_TOKEN`: The API token for accessing Statuspage APIs.
- `SP_COMPONENT_ID`: The component ID on Statuspage that you want to update.

## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Set the required environment variables.
2. Run the script:
   ```sh
   python cloudflare_status_sync.py
   ```

### Example Execution with Environment Variables
Before running the script, ensure all the necessary environment variables are defined in your shell:
```sh
export CF_ACCOUNT_ID="your_cloudflare_account_id"
export CF_API_TOKEN="your_cloudflare_api_token"
export CF_TUNNEL_ID="your_cloudflare_tunnel_id"
export SP_PAGE_ID="your_statuspage_page_id"
export SP_API_TOKEN="your_statuspage_api_token"
export SP_COMPONENT_ID="your_statuspage_component_id"
```
Then execute the script:
```sh
python cloudflare_status_sync.py
```

## How It Works
1. **Get Tunnel Status**: The script fetches the current status of the Cloudflare tunnel by making a request to the Cloudflare API.
2. **Get Component Status**: The current status of the component on Statuspage is fetched.
3. **Status Comparison**: If the Cloudflare tunnel status differs from the Statuspage component status, the component is updated to match the tunnel status.
4. **Under Maintenance Handling**: If the component is marked as `under_maintenance`, no changes are made.

### Cloudflare to Statuspage Status Mapping
- `inactive` -> Empty (No status update)
- `degraded` -> `degraded_performance`
- `healthy` -> `operational`
- `down` -> `major_outage`

## Logging
The script includes logging that provides detailed information about its execution, including successful and failed API requests.

- Logs are printed to the console and formatted as: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling
- The script handles missing environment variables and unexpected API responses gracefully.
- In case of network errors or other request exceptions, the script will log the error and raise an appropriate exception.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributions
Feel free to open issues or submit pull requests to contribute to the project. Your feedback and ideas are always welcome!
