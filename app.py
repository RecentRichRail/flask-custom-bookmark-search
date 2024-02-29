from flask import Flask, redirect, request

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

# Function to encode URL
def url_encode(url):
    url = url.replace(" ", "+")
    return url

@app.route('/')
def index():
    return 'Welcome to the Command Redirector!'


@app.route('/search=<command>')
def redirect_command(command):
    for cmd, stored_url, searchable in COMMANDS:
        if command.lower().startswith(cmd):  # Check if the beginning of the requested command matches the command prefix
            if searchable:
                # Extract search query from the request path
                search_query = command[len(cmd):].strip()  # Extract search query after the command prefix
                encoded_query = url_encode(search_query)
                return redirect(stored_url + encoded_query)
            else:
                return redirect(stored_url)

    # If the command does not match any predefined commands or search-related subdomains,
    # treat it as a web search with Brave
    search_query = command
    encoded_query = url_encode(search_query)
    return redirect(DEFAULT_SEARCH_DOMAIN % encoded_query)


if __name__ == '__main__':
    app.run(debug=True)
