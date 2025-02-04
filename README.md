# Domain Status Monitoring and Reporting Script

## Overview

This Python project consists of two scripts:

1. **Domain Monitoring Script:** Monitors the status of specified domains (websites), checks their response codes, handles failures by retrying connections, and sends email alerts when necessary.
2. **Reporting Script (`raport.py`):** Generates daily reports of domain statuses, including statistics for each monitored domain and the HTTP response codes.

These scripts are designed to help ensure that all monitored domains are functional and to notify administrators when there are issues that need attention. Additionally, the reporting script allows administrators to receive periodic status updates.

## Features

- **Domain Status Monitoring:**
  - The script checks the response status of each domain and ensures it returns valid HTTP status codes such as `200 OK`.
- **Retry Mechanism:**
  - If a domain is down, the script retries the connection multiple times (with increasing delay) to check if the issue resolves.
- **Error Logging:**
  - Errors and failures are logged for review. If a domain fails after multiple attempts, it is flagged for further action.
- **Email Alerts:**
  - When a domain is still down after retries, an email alert is sent to the administrator.
- **Daily Reports:**
  - `raport.py` generates daily reports on domain status, including the number of successful and failed status checks, providing a summary of the domain health.
- **Customizable Parameters:**
  - The script's parameters such as SMTP server settings, email credentials, and domains to monitor are loaded from a configuration file for flexibility.

## How It Works

### Domain Monitoring Script

1. **Domain Checking:**
   - The script starts by reading a list of domains from `domain.txt`.
   - For each domain, it performs an HTTPS request and checks the response code.

2. **Logging:**
   - The script logs the status of each domain, whether it is up or down, with the date and time of the request in `log.txt`.
   - If a domain returns an invalid HTTP status code (e.g., not `200 OK`), the domain is recorded in `broke_request.txt`.

3. **Retries and Alerts:**
   - For domains that are down or unreachable, the script retries the connection up to three times, with increasing delay between attempts.
   - If the domain still does not respond properly after all retries, an email alert is sent to the administrator.
   - The domain is then removed from the retry list (`broke_request.txt`).

4. **Parameter Configuration:**
   - All configurable parameters such as SMTP server settings (for sending email alerts) and email credentials are stored in a separate `parameters.txt` file, making the script easily configurable.

### Reporting Script (`raport.py`)

- `raport.py` generates a daily summary of the domain statuses, including the number of successful checks and the number of "Not Found" errors for each domain.
- The report is structured to provide an overview of how well the domains are functioning, highlighting any errors detected in the last 24 hours.

### Using Cron for Automation

To automate the domain monitoring and report generation, you can use **cron jobs** on Linux-based systems to run the scripts at specific intervals, such as daily or weekly.

For example, to run the monitoring script and the reporting script every day, you can add these lines to your crontab file:

```bash
# Open crontab file for editing
crontab -e

# Run domain monitoring script every 6 hours
0 */6 * * * /usr/bin/python3 /path/to/your/domain_monitor.py

# Run the report generation script daily at 8 AM
0 8 * * * /usr/bin/python3 /path/to/your/raport.py
