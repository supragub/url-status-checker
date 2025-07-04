# This file is part of URL Status Checker.

# Copyright (C) 2024 Gabor VARGA

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import re
import os
import json
import config
import urllib3
import requests
import unicodedata
from typing import List, Dict
from datetime import datetime
from time import sleep


# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def clean_name(name: str) -> str:
    """Cleans the given name by replacing non-alphanumeric characters with underscores and removing accents."""
    name = unicodedata.normalize('NFKD', name).encode(
        'ASCII', 'ignore').decode('utf-8')
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    return re.sub(r'_+', '_', name)


def format_duration(seconds):
    """Formats the duration in seconds into a human-readable format."""
    if seconds < 0:
        return "0s"  # Negative values are not supported; return 0 seconds

    # Convert to integer to avoid decimals in seconds
    seconds = int(seconds)

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_parts = []

    if days > 0:
        formatted_parts.append(f"{days}d")
    if hours > 0:
        formatted_parts.append(f"{hours}h")
    if minutes > 0:
        formatted_parts.append(f"{minutes}m")
    if seconds > 0:
        formatted_parts.append(f"{seconds}s")

    # If all parts are zero, default to 0s
    return ' '.join(formatted_parts) if formatted_parts else "0s"


def fetch_url_status(url: str, timestamp: str):
    """Fetches the status of the URL and returns its status code, message, and timestamp."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        response = requests.get(url, headers=headers,
                                verify=False, timeout=10)  # Ignore SSL errors

        statuscd = str(response.status_code)

        # Custom reason mapping
        if statuscd == "200":
            statusmsg = "OK"
        elif statuscd == "404":
            statusmsg = "Not Found"
        else:
            statusmsg = response.reason  # Default reason from the response

        return url, statuscd, statusmsg, timestamp
    except requests.RequestException as e:
        return url, "Error", str(e), timestamp


def append_log_entry(url: str, statuscd: str, statusmsg: str, timestamp: datetime):
    """Appends a log entry for the URL's status to the corresponding JSON log file."""
    log_filename = os.path.join(config.LOG_DIR, f"{clean_name(url)}.json")
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    if os.path.exists(log_filename):
        with open(log_filename, 'r') as file:
            log_data = json.load(file)
    else:
        log_data = []

    log_data.append({'url': url, 'timestamp': timestamp,
                    'statuscd': statuscd, 'statusmsg': statusmsg})

    with open(log_filename, 'w') as file:
        json.dump(log_data, file, indent=4)


def check_and_log_urls(url_registry: list, timestamp: str):
    """Checks and logs the status of each URL in the registry."""
    for entry in url_registry:
        url, status_code, status_msg, timestamp = fetch_url_status(
            entry['url'], timestamp)
        append_log_entry(url, status_code, status_msg, timestamp)

    update_registry_with_logs(url_registry, config.URL_REGISTRY_FILE)


def load_url_registry(file_path: str) -> list:
    """Loads the URL registry from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def calculate_total_downtime(log_data: List[Dict]) -> int:
    """
    Calculates the total downtime for a URL based on log data.
    A downtime occurs if the status code is not '200'.
    """
    total_downtime = 0

    for i in range(1, len(log_data)):
        # Check if the current and previous entries are downtimes
        if log_data[i - 1]['statuscd'] != '200':
            # Calculate the interval in seconds between two timestamps
            previous_timestamp = datetime.fromisoformat(
                log_data[i - 1]['timestamp'])
            current_timestamp = datetime.fromisoformat(
                log_data[i]['timestamp'])
            interval = (current_timestamp - previous_timestamp).total_seconds()
            total_downtime += interval

    return int(total_downtime)


def calculate_last_change_duration(log_data: List[Dict]) -> int:
    """
    Calculates the time since the last status change for a URL.
    """
    if not log_data:
        return 0

    latest_entry = log_data[-1]
    latest_statuscd = latest_entry['statuscd']

    # Iterate backward to find the last status change
    for entry in reversed(log_data[:-1]):
        if entry['statuscd'] != latest_statuscd:
            last_change_time = datetime.fromisoformat(entry['timestamp'])
            return int((datetime.now() - last_change_time).total_seconds())

    # If no status change, calculate time since the first entry
    first_entry_timestamp = datetime.fromisoformat(log_data[0]['timestamp'])
    return int((datetime.now() - first_entry_timestamp).total_seconds())


def update_registry_with_logs(url_registry: list, registry_file_path: str):
    """Updates each URL entry in the registry with the latest status and downtime information."""
    for entry in url_registry:
        log_filename = os.path.join(
            config.LOG_DIR, f"{clean_name(entry['url'])}.json")

        if not os.path.exists(log_filename):

            continue

        with open(log_filename, 'r') as log_file:
            log_data = json.load(log_file)

        if log_data:
            first_check_time = datetime.fromisoformat(
                log_data[0]['timestamp']).strftime("%Y.%m.%d. %H:%M")
            last_check_time = datetime.fromisoformat(
                log_data[-1]['timestamp']).strftime("%Y.%m.%d. %H:%M")

            # Calculating last change duration and total downtime
            last_change_duration = calculate_last_change_duration(log_data)
            formatted_last_change = format_duration(last_change_duration)

            total_downtime_duration = calculate_total_downtime(
                log_data)
            formatted_total_downtime = format_duration(total_downtime_duration)

            entry.update({
                'statuscd': log_data[-1]['statuscd'],
                'statusmsg': log_data[-1]['statusmsg'],
                'firstcheck': first_check_time,
                'lastcheck': last_check_time,
                'lastchange': formatted_last_change,
                'totaldowntime': formatted_total_downtime
            })

    # Save the updated registry back to the JSON file
    with open(registry_file_path, 'w') as registry_file:
        json.dump(url_registry, registry_file, indent=4)


def save_url_registry(file_path: str, url_registry: list):
    """Saves the updated URL registry to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(url_registry, file, indent=4)


def check_urls_periodically(interval_seconds: int = config.DEFAULT_INTERVAL_SECONDS):
    """Periodically checks the status of URLs from the registry and logs the results."""
    while True:
        current_timestamp = datetime.now().isoformat()
        check_reset_status(current_timestamp)
        print(f"Waiting {interval_seconds} seconds before the next check...")
        sleep(interval_seconds)


def check_reset_status(current_timestamp: str):
    """Checks the status of each URL in the registry and resets the status if it is 'N/A'."""
    url_registry = load_url_registry(config.URL_REGISTRY_FILE)

    for entry in url_registry:

        if entry['statuscd'] == 'N/A' and entry['statusmsg'] == 'N/A' and entry['firstcheck'] == 'N/A' and entry['lastcheck'] == 'N/A' and entry['lastchange'] == 'N/A' and entry['totaldowntime'] == 'N/A':

            log_filename = os.path.join(
                config.LOG_DIR, f"{clean_name(entry['url'])}.json")

            if os.path.exists(log_filename):

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                archive_filename = os.path.join(config.LOG_DIR, f"archive_{
                                                clean_name(entry['url'])}_{timestamp}.json")

                os.rename(log_filename, archive_filename)

    check_and_log_urls(url_registry, current_timestamp)


def run():
    check_urls_periodically()


if __name__ == "__main__":
    run()
