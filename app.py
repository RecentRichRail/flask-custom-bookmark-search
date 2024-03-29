import logging
from flask import Flask, redirect, render_template, request, jsonify
import urllib.parse
import json
import uuid
import requests
import os

from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

only_prefixes = []
all_prefixes_classes = []
default_search = ""

class Prefixes:
    def __init__(self, prefixes, category, url, search_url = ""):
        self.prefixes = prefixes
        self.category = category
        self.url = url
        self.search_url = search_url

class Request:
    def __init__(self, original_request):
        self.id = uuid.uuid4()
        self.original_request = original_request
        self.prefix = ""
        self.search_query = ""
        self.category = ""
        self.encoded_query = ""
        self.is_search = False
        self.url = ""
        self.search_url = ""

# try:
#     with open('src/settings.json', 'r') as file:
#         settings_data = json.load(file)
# except FileNotFoundError:
#     logging.error("Could not find commands.json file.")
#     settings_data = {'settings': []}
        
# settings = settings_data['settings']
# allow_logging = settings[0]['allow_logging']
# require_hanko_login = settings[0]['require_hanko_login']
# hanko_server_address = settings[0]['hanko_server_address']
# default_search_server_address = settings[0]['default_search_server_address']

allow_logging = os.environ.get('allow_logging')
require_hanko_login = os.environ.get('require_hanko_login')
hanko_server_address = os.environ.get('hanko_server_address')
default_search_server_address = os.environ.get('default_search_server_address')

# Read commands from JSON file 
try:
    with open('src/commands.json', 'r') as file:
        commands_data = json.load(file)
except FileNotFoundError:
    logging.error("Could not find commands.json file.")
    commands_data = {'commands': []}

commands = commands_data['commands']
for cmd in commands:
    try: 
        if cmd['search_url']:
            all_prefixes_classes.append(Prefixes(cmd['prefix'], cmd['category'], cmd['url'], cmd['search_url']))
    except KeyError:
        all_prefixes_classes.append(Prefixes(cmd['prefix'], cmd['category'], cmd['url']))

    for prefix in cmd['prefix']:
        only_prefixes.append(prefix)

    if cmd['category'] == "default_search":
        if default_search == "":
            default_search = Prefixes(cmd['prefix'], cmd['category'], cmd['url'], cmd['search_url'])
        else:
            print(f"Unable to set default_search to {cmd['url']} because it is already set to {default_search.url}")

def check_for_login():
    logging.info(f"Getting jwt from browser")
    jwt_cookie = request.cookies.get("hanko")
    # Send the JWT to the API for authentication
    logging.info(f"Sending jwt for authentication")
    response = requests.post(
        f"{hanko_server_address}/auth",
        headers={"Authorization": f"Bearer {jwt_cookie}"}
    )

    # Check the response from the API
    if response.status_code == 200:
        logging.info(f"JWT is valid.")
        return True
    else:
        logging.error(f"JWT is invalid.")
        return False

# Default page, this page shows the list of commands
@app.route('/')
def index():

    if require_hanko_login:
        request.is_authenticated = check_for_login()
        logging.info(f"is_authenticated = {request.is_authenticated}")
        if not request.is_authenticated:
            return redirect(f"{hanko_server_address}/login?redirect={default_search_server_address}/")

    # Render the HTML template and pass the commands data
    return render_template('index.html', commands=commands)

# Redirect to the appropriate URL based on the command
@app.route('/search=<command>')
def redirect_command(command):
    request = Request(command)

    if require_hanko_login:
        request.is_authenticated = check_for_login()
        logging.info(f"is_authenticated = {request.is_authenticated}")
        if not request.is_authenticated:
            return redirect(f"{hanko_server_address}/login?redirect={default_search_server_address}/search={command}")

    if not command:
        return redirect('/')

    # Check if first word in command is in prefixes
    request.prefix = command.split(' ')[0].lower()
    logging.info(f"'{request.prefix}' has been set as the prefix")
    request.search_query = command.replace(request.prefix, '', 1).strip()
    logging.info(f"'{request.search_query}' has been set as the search_query")
    if request.prefix in only_prefixes:
        logging.info(f"'{request.prefix}' is in only_prefixes")
        # Check all_prefixes_classes for the prefix
        for prefixes in all_prefixes_classes:
            if request.prefix in prefixes.prefixes:
                logging.info(f"'{request.prefix}' is in {prefixes.prefixes}")
                request.category = prefixes.category
                logging.info(f"'{request.category}' has been set as the category")
                request.url = prefixes.url
                logging.info(f"'{request.url}' has been set as the url")
                if request.search_query:
                    request.encoded_query = urllib.parse.quote_plus(request.search_query)
                    logging.info(f"'{request.encoded_query}' has been set as the encoded_query")
                    request.category = "search"
                    logging.info(f"'{request.category}' has been set as the category")
                    request.is_search = True
                    logging.info(f"'{request.is_search}' has been set as the is_search")
                    request.search_url = prefixes.search_url
                    logging.info(f"'{request.search_url}' has been set as the search_url")
                break

    # If no prefix then use default_search
    else:
        request.search_query = command
        logging.info(f"'{request.search_query}' has been set as the search_query")
        request.encoded_query = urllib.parse.quote_plus(request.search_query)
        logging.info(f"'{request.encoded_query}' has been set as the encoded_query")
        request.category = "search"
        logging.info(f"'{request.category}' has been set as the category")
        request.is_search = True
        logging.info(f"'{request.is_search}' has been set as the is_search")
        request.url = default_search.url
        logging.info(f"'{request.url}' has been set as the url")
        request.search_url = default_search.search_url
        logging.info(f"'{request.search_url}' has been set as the search_url")

    if allow_logging:
        with open('requests.csv', 'a') as file:
                file.write(f"{request.id},{request.original_request},{request.prefix},{request.search_query},{request.category},{request.url},{request.search_url}\n")

    if request.is_search:
        logging.info(f"'request.is_search' is True")
        logging.info(f"redirecting to {request.search_url.format(request.encoded_query)}")
        return redirect(request.search_url.format(request.encoded_query))

    else:
        logging.info(f"'request.is_search' is False")
        logging.info(f"redirecting to {request.url}")
        return redirect(request.url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', debug=True)

