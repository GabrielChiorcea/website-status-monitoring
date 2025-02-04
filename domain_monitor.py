import http.client  # Import the HTTP client library to make HTTP requests
import datetime  # Import the datetime library to work with dates and times
import smtplib  # Import the smtplib library to send emails
import ssl  # Import the SSL library for secure connections
import time  # Import the time library for introducing delays
import os  # Import the os library for working with file system
import re  # Import the regular expression (regex) library for pattern matching

# Parameters
now = datetime.datetime.now()  # Get the current date and time
formatted_now = now.strftime("%Y-%m-%d %H:%M")  # Format the current date and time as a string
broke_request = "broke_request.txt"  # Path to the file that will hold failed domains
codes = {200, 301, 302, 303, 304, 307, 308}  # Set of valid HTTP status codes
domain_pattern = r"(\d{3}) - .+? - (\S+\.\S+)"  # Regular expression pattern to match domain in log lines
para_path = "parameters.txt"  # Path to the file containing configuration parameters


def load_parameters(file_path):
    """Function to load configuration parameters from a file."""
    params = {}
    with open(file_path, 'r') as p:
        for line in p:
            key, value = line.strip().split("=")  # Split each line by "=" to get key-value pairs
            params[key] = value  # Store the key-value pair in the dictionary
    return params  # Return the dictionary containing parameters

# Load parameters from the configuration file
params = load_parameters(para_path)

# Extract parameters from the loaded dictionary
SMTP_SERVER = params["SMTP_SERVER"]  # SMTP server address
SMTP_PORT = int(params["SMTP_PORT"])  # SMTP server port (converted to integer)
EMAIL_USER = params["EMAIL_USER"]  # Sender's email address
EMAIL_PASSWORD = params["EMAIL_PASSWORD"]  # Sender's email password
TO_EMAIL = "admin@brandivo.ro"  # Recipient's email address


def check_domain(url):
    """Function to check the status of a given URL (domain)."""
    clean_url = url.replace("https://", "").replace("http://", "").replace("//", "")  # Clean the URL
    
    try:
        # Connect to the server using HTTPS
        conn = http.client.HTTPSConnection(clean_url)
        # Send a GET request to the root of the domain
        conn.request("GET", "/")
        # Get the response
        response = conn.getresponse()
        return response  # Return the response to process further
    except Exception as e:
        # If an error occurs, write the error message to the error log
        with open("error.txt", "a") as file:
            file.write(f"Connection Error: {str(e)}\n")
        return None  # If an error occurs, return None


def log(url, response):
    """Function to log a domain if the response is valid."""
    with open("log.txt", "a") as file:
        # Write the formatted date, status, and domain information to the log file
        w = f"{formatted_now} {response.status} - {response.reason} - {url} \n"
        file.write(w)


def alert():
    """Function to check the status of each domain in 'broke_request.txt' and handle failures."""
    if os.path.exists(broke_request):  # If the 'broke_request' file exists
        with open(broke_request, 'r') as lines:
            # Read all lines from the file and store them
            lines_to_process = lines.readlines()

        # Reprocess each line (domain) from the file
        for line in lines_to_process:
            match = re.search(domain_pattern, line)  # Try to match the domain pattern
            
            if match:  # If a match is found
                domain = match.group(2)  # Extract the domain from the matched group

                times = 0  # Initialize retry attempts
                success = False  # Flag to track success
                
                while times < 3:
                    times += 1
                    print(f"Attempt {times} for {domain}...")

                    # Introduce delays between retries
                    if times == 1:
                        time.sleep(5)  # 5 seconds for the first attempt
                    elif times == 2:
                        time.sleep(10)  # 10 seconds for the second attempt
                    elif times == 3:
                        time.sleep(15)  # 15 seconds for the third attempt

                    response = check_domain(domain)  # Check the domain again

                    if response:
                        if response.status in codes:  # If the status code is valid
                            log(domain, response)  # Log the response
                            success = True  # Mark the attempt as successful
                            print(f"Valid status for {domain}: {response.status}")
                            os.remove(broke_request)  # Remove the 'broke_request' file after success
                            break
                    else:
                        print(f"Error connecting to {domain}, retrying...")

                # If all attempts failed, send an email alert
                if not success:
                    message = f"Subject: domain {domain} is down"  # Prepare the alert message
                    context = ssl.create_default_context()  # Create an SSL context for secure email transmission
                    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                        server.login(EMAIL_USER, EMAIL_PASSWORD)  # Log in to the SMTP server
                        server.sendmail(EMAIL_USER, TO_EMAIL, message)  # Send the email alert
                    os.remove(broke_request)  # Remove the 'broke_request' file after sending the alert

                # If the domain was successful, remove it from the 'broke_request' file
                if success:
                    with open(broke_request, 'r') as file:
                        lines = file.readlines()  # Read all lines from the 'broke_request' file
                    # Rewrite the file excluding the resolved domain
                    with open(broke_request, 'w') as file:
                        for line in lines:
                            if domain not in line:
                                file.write(line)
    else:
        print("No issues detected.")


# Read domains from 'domain.txt' and check their status
with open('domain.txt', 'r') as api_file:
    for line in api_file:
        url = line.strip()  # Clean the URL by removing leading/trailing spaces
        response = check_domain(url)  # Check the domain's status
        if response:
            if response.status not in codes:  # If the response status is not valid
                with open(broke_request, "a") as file:
                    # Log the invalid status in the 'broke_request' file
                    file.write(f"{formatted_now} {response.status} - {response.reason} - {url} \n")
            log(url, response)  # Log the valid response

# Check for domains that need to be re-checked for failure
alert()
