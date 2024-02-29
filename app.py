from flask import Flask, redirect, request
import urllib.parse

app = Flask(__name__)

COMMANDS = {
    'fb': "https://facebook.com/",
    'm': "messenger://",
    'mw': "https://www.messenger.com/",
    'wa': "whatsapp://",
    'waw': "https://web.whatsapp.com/",
    'gm': "https://mail.google.com/mail/u/0",
    # Include other commands here
}

DEFAULT_SEARCH_DOMAIN = "https://search.brave.com/search?q=%s&source=web"

# Dictionary to map search-related subdomains to their corresponding search domains
SEARCH_DOMAINS = {
    'wiki': "https://wiki.spicerhome.net/index.php?search=%s&title=Special%3ASearch&wprov=acrw1_-1",
    # Add more search-related domains here
}

@app.route('/')
def index():
    return 'Welcome to the Command Redirector!'

@app.route('/<command>')
def redirect_command(command):
    if command.lower() in COMMANDS:
        return redirect(COMMANDS[command.lower()])
    else:
        for subdomain, search_domain in SEARCH_DOMAINS.items():
            if command.startswith(subdomain + " "):
                search_query = request.full_path[len(subdomain) + 2:]  # remove subdomain and space from the command
                encoded_query = urllib.parse.quote_plus(search_query)
                return redirect(search_domain % encoded_query)
        return redirect(DEFAULT_SEARCH_DOMAIN % command)

if __name__ == '__main__':
    app.run(debug=True)
