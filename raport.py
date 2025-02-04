import smtplib  # Import the SMTP library to send emails
import ssl  # Import the SSL library for secure connections

para_path = "parameters.txt"  # Path to the parameters file that contains email and SMTP server details
log = "log.txt"  # Path to the log file containing the log data


def load_parameters(path):
    # Function to load parameters from the file
    params = {}

    # Open and read the parameters file line by line
    with open(path, "r") as file:
        for line in file:
            key, value = line.strip().split("=")  # Split each line into key and value
            params[key] = value  # Store the key-value pair in the params dictionary
    return params  # Return the dictionary containing the parameters

# Load the parameters from the file
params = load_parameters(para_path)

# Extract the parameters from the loaded dictionary
SMTP_SERVER = params["SMTP_SERVER"]  # SMTP server address
SMTP_PORT = int(params["SMTP_PORT"])  # SMTP server port (as an integer)
EMAIL_USER = params["EMAIL_USER"]  # The email user (sender's email)
EMAIL_PASSWORD = params["EMAIL_PASSWORD"]  # The email password (sender's password)
TO_EMAIL = "admin@brandivo.ro"  # The recipient's email address

log_status = {}  # Initialize a dictionary to store log data by date and domain

# Open and read the log file
with open(log, 'r') as logs:
    for line in logs:
        parts = line.strip().split(' - ')  # Split each line by the " - " delimiter

        # Skip the line if it doesn't have enough parts
        if len(parts) < 3:
            continue

        # Extract the date-time, HTTP code, and domain from the line
        date_time, http_code, domain = parts
        date = date_time.strip().split(" ")[0]  # Extract just the date (YYYY-MM-DD)

        # If the date doesn't exist in the log_status dictionary, create an entry for it
        if date not in log_status:
            log_status[date] = {}

        # If the domain doesn't exist for the given date, create an entry for it
        if domain not in log_status[date]:
            log_status[date][domain] = {}

        # If the HTTP code doesn't exist for the given domain and date, initialize its count
        if http_code not in log_status[date][domain]:
            log_status[date][domain][http_code] = 0

        # Increment the count for the specific HTTP code of the given domain and date
        log_status[date][domain][http_code] += 1


subject = "Report"  # Subject of the email
message_body = "Log Status Report:\n\n"  # Initialize the body of the email with a header
message_body += "Summary of statuses for the monitored domains:\n\n"  # Add a subtitle

# Iterate through the log status dictionary (grouped by date)
for date, domains in log_status.items():
    message_body += f"Date: {date}\n"  # Add the current date to the message
    ok_count = 0  # Initialize a variable to count the "OK" status codes
    error_count = 0  # Initialize a variable to count the "Not Found" status codes
    
    # Iterate through the domains for the given date
    for domain, status in domains.items():
        # Create a string representing the status codes and their counts
        status_str = ', '.join([f"{code} = {count}" for code, count in status.items()])
        
        # Check if there are "OK" and "Not Found" status codes and increment their respective counters
        if "OK" in status:
            ok_count += status["OK"]
        if "Not Found" in status:
            error_count += status["Not Found"]
        
        # Add the domain and its status details to the message body
        message_body += f"  Domain: {domain} - Status: {status_str}\n"
    
    message_body += '\n'  # Add a blank line for separation
    # Add a summary of the total "OK" and "Not Found" statuses for the given date
    message_body += f"Total statuses for {date}, OK: {ok_count}, Total 'Not Found' errors: {error_count}.\n\n"


# Construct the final message with subject and body
message = f"Subject: {subject}\n\n{message_body}"

# Create an SSL context for a secure connection to the SMTP server
context = ssl.create_default_context()

# Use the SMTP_SSL class to send the email securely
with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
    server.login(EMAIL_USER, EMAIL_PASSWORD)  # Log in to the SMTP server with provided credentials
    server.sendmail(EMAIL_USER, TO_EMAIL, message)  # Send the email from the sender to the recipient
