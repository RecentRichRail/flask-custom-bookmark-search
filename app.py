from flask import Flask, redirect, request
import urllib.parse

app = Flask(__name__)

# Define commands with format [prefix, URL/search_URL, IS_Searchable]
COMMANDS = [
    ("fb", "https://facebook.com", False),
    ("m", "messenger://", False),
    ("mw", "https://www.messenger.com/", False),
    ("wa", "whatsapp://", False),
    ("waw", "https://web.whatsapp.com/", False),
    ("gm", "https://mail.google.com/mail/u/0", False),
    # Add more commands here
    ("wiki", "https://wiki.spicerhome.net/index.php?search=", True),
    # Add more search-related commands here
]

DEFAULT_SEARCH_DOMAIN = "https://search.brave.com/search?q=%s"


@app.route('/')
def index():
    return 'Welcome to the Command Redirector!'


@app.route('/search=<command>')
def redirect_command(command):
    for cmd, url, searchable in COMMANDS:
        if command.lower().startswith(cmd):  # Check if the beginning of the requested command matches the command prefix
            if searchable:
                # Extract search query from the request path
                search_query = request.full_path.split('=', 1)[-1].strip()
                encoded_query = urllib.parse.quote_plus(search_query)
                return redirect(url % encoded_query)
            else:
                return redirect(url)

    # If the command does not match any predefined commands or search-related subdomains,
    # treat it as a web search with Brave
    search_query = request.full_path.split('=', 1)[-1].strip()
    encoded_query = urllib.parse.quote_plus(search_query)
    return redirect(DEFAULT_SEARCH_DOMAIN % encoded_query)


if __name__ == '__main__':
    app.run(debug=True)
