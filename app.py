import logging
from flask import Flask, redirect, render_template, request, jsonify
import urllib.parse
import json
import uuid
import jwt
import requests

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

# Read commands from JSON file 
try:
    with open('src/settings.json', 'r') as file:
        settings_data = json.load(file)
except FileNotFoundError:
    logging.error("Could not find commands.json file.")
    settings_data = {'settings': []}

settings = settings_data['settings']
allow_logging = settings[0]['allow_logging']
require_hanko_login = settings[0]['require_hanko_login']
hanko_server_address = settings[0]['hanko_server_address']
default_search_server_address = settings[0]['default_search_server_address']
API_URL = settings[0]['API_URL'] #change this to your url from cloud.hanko.io
AUDIENCE = settings[0]['AUDIENCE'] #change this to the domain you're hosting on, and make sure it matches the URL on cloud.hanko.io

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
if require_hanko_login:
    # setup hanko login check
    # Retrieve the JWKS from the Hanko API
    jwks_url = f"{API_URL}/.well-known/jwks.json"
    jwks_response = requests.get(jwks_url)
    jwks_data = jwks_response.json()
    public_keys = {}
    for jwk in jwks_data["keys"]:
        kid = jwk["kid"]
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

def check_for_login():
    # Retrieve the JWT from the cookie
    logging.info(f"Checking for jwt cookie...")
    jwt_cookie = request.cookies.get("hanko")
    # print(jwt_cookie)
    if not jwt_cookie: #check that the cookie exists
        logging.info(f"No jwt cookie found. Redirecting to /login...")
        # return redirect("/login")
        # return render_template('login.html', API_URL=API_URL, redirect=command)
        return False
    try:
        logging.info(f"jwt cookie found. Verifying...")
        kid = jwt.get_unverified_header(jwt_cookie)["kid"]
        payload = jwt.decode(
            str(jwt_cookie), 
            public_keys[kid],
            algorithms=["RS256"],
            audience=AUDIENCE,
        )
        pprint(payload)
    except Exception as e:
        # The JWT is invalid
        logging.info(f"JWT is invalid. Redirecting to /login...")
        print(e)
        # return jsonify({"message": "unauthorised"})
        # return redirect("/login")
        return False
    # return jsonify({"message": "authorised"})
    logging.info(f"JWT is valid.")
    return True

# Default page, this page shows the list of commands
@app.route('/')
def index():

    if require_hanko_login:
        request.is_authenticated = check_for_login()
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

