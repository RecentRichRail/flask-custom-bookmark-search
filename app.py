import logging
from flask import Flask, redirect, render_template
import urllib.parse
import json
import uuid

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

# Default page, this page shows the list of commands
@app.route('/')
def index():
    # Render the HTML template and pass the commands data
    return render_template('index.html', commands=commands)

# Redirect to the appropriate URL based on the command
@app.route('/search=<command>')
def redirect_command(command):

    if not command:
        return redirect('/')
    
    request = Request(command)

    # Check if first word in command is in prefixes
    first_word = command.split(' ')[0].lower()
    requested_command_without_first_word = command.replace(first_word, '', 1).strip()
    if first_word in only_prefixes:
        request.prefix = first_word
        # Check all_prefixes_classes for the prefix
        for prefixes in all_prefixes_classes:
            if request.prefix in prefixes.prefixes:
                request.category = prefixes.category
                request.url = prefixes.url
                if requested_command_without_first_word:
                    request.search_query = requested_command_without_first_word
                    request.encoded_query = urllib.parse.quote_plus(request.search_query)
                    request.category = "search"
                    request.is_search = True
                    request.url = prefixes.url
                    request.search_url = prefixes.search_url
    # If no prefix then use default_search
    else:
        # request.prefix = False
        request.search_query = command
        encoded_query = urllib.parse.quote_plus(command)
        return redirect(default_search.search_url.format(encoded_query))

    if request.is_search:
        return redirect(request.search_url.format(request.encoded_query))
    else:
        return redirect(request.url.format(request.encoded_query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', debug=True)
