from flask import Flask, redirect
import urllib.parse
import json

app = Flask(__name__)

# Read commands from JSON file
with open('src/commands.json', 'r') as file:
    commands_data = json.load(file)
    commands = commands_data['commands']

@app.route('/')
def index():
    # HTML template for displaying command information
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
                <th>Category</th>
                <th>Prefix</th>
                <th>URL</th>
                <th>Search URL</th>
            </tr>
    """
    # Iterate through each command and populate the HTML table
    for command in commands:
        # Display search URL if available, otherwise an empty string
        search_url_display = command.get('search_url', '')
        table_html += f"<tr><td>{command['category']}</td><td>{command['prefix']}</td><td>{command['url']}</td><td>{search_url_display}</td></tr>"
    table_html += """
        </table>
    </body>
    </html>
    """
    return table_html

@app.route('/search=<command>')
def redirect_command(command):
    # Check if a command is provided
    if not command:
        print("No command, Redirect to '/'")
        return redirect('/')

    # Iterate through commands to find a matching prefix
    for cmd in commands:
        # Check if the prefix is a list or a single value
        if isinstance(cmd['prefix'], list):
            prefixes = cmd['prefix']
        else:
            prefixes = [cmd['prefix']]
        # Iterate through prefixes to find a match
        for prefix in prefixes:
            # Check if the command starts with the prefix
            if command.lower().startswith(prefix):
                # Extract search query after the command prefix
                search_query = command[len(prefix):].strip()
                # Redirect based on command category and search query
                if search_query == "" or cmd['category'] == "shortcut":
                    return redirect(cmd['url'])
                else:
                    if cmd['category'] == "search" or cmd['category'] == "default_search":
                        encoded_query = urllib.parse.quote_plus(search_query)
                        return redirect(cmd['search_url'].format(encoded_query))
                    else:
                        # Log error if the category for the URL is not set to 'search'
                        print(f"Failed because category for URL '{cmd['url']}' is not set to 'search' or 'default_search'")
                        break
        else:
            continue
        break
    else:
        # If no matching prefix is found, attempt to use default search command
        for cmd in commands:
            if cmd['category'] == "default_search":
                encoded_query = urllib.parse.quote_plus(command)
                return redirect(cmd['search_url'].format(encoded_query))
        else:
            # Log error if default search command is not found
            print("Failed to find 'default_search'")

if __name__ == '__main__':
    app.run(debug=True)
