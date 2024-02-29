from flask import Flask, redirect, request
import urllib.parse

app = Flask(__name__)

# Define commands with format [prefix, URL, IS_Searchable, search_URL]
COMMANDS = [
    ("fb", "https://facebook.com", False, None),
    ("wiki", "https://wiki.spicerhome.net/index.php", True, "https://wiki.spicerhome.net/index.php?search=%s"),
    ("yt", "https://www.youtube.com/", True, "https://www.youtube.com/results?search_query=%s"),
]

DEFAULT_SEARCH_DOMAIN = "https://search.brave.com/search?q=%s&source=web"

@app.route('/')
def index():
    table_html = """
    <html>
    <head>
        <style>
            table {
                border-collapse: collapse;
                width: 80%;
                margin: 20px auto;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">Flask Custom Bookmark Search</h1>
        <p style="text-align: center;"><a href="https://github.com/RecentRichRail/flask-custom-bookmark-search">GitHub Repository</a></p>
        <table>
            <tr>
                <th>Prefix</th>
                <th>URL</th>
                <th>Searchable</th>
                <th>Search URL</th>
            </tr>
    """
    for cmd, stored_url, searchable, search_url in COMMANDS:
        search_url_display = search_url if search_url else ""
        searchability = "Yes" if searchable else "No"
        table_html += f"<tr><td>{cmd}</td><td>{stored_url}</td><td>{searchability}</td><td>{search_url_display}</td></tr>"
    table_html += """
        </table>
    </body>
    </html>
    """
    return table_html

@app.route('/search=<command>')
def redirect_command(command):
    for cmd, stored_url, searchable, search_url in COMMANDS:
        if command.lower().startswith(cmd):  # Check if the beginning of the requested command matches the command prefix
            if searchable:
                # Extract search query from the request path
                search_query = command[len(cmd):].strip()  # Extract search query after the command prefix
                if search_query == "":
                    return redirect(stored_url)
                encoded_query = urllib.parse.quote_plus(search_query)
                return redirect(search_url % encoded_query)
            else:
                return redirect(stored_url)

    # If the command does not match any predefined commands or search-related subdomains,
    # treat it as a web search with Brave
    search_query = command
    encoded_query = urllib.parse.quote_plus(search_query)
    return redirect(DEFAULT_SEARCH_DOMAIN % encoded_query)

if __name__ == '__main__':
    app.run(debug=True)
