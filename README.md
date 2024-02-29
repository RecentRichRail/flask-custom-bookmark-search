# Flask Custom Bookmark Search

Flask Custom Bookmark Search is a simple Flask application that redirects users to predefined URLs or performs searches based on user input. This project demonstrates how to containerize a Flask application using Docker.

## Features

- Redirects users to predefined URLs for specific commands.
- Performs searches on different search engines or services based on user input.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker: [Install Docker](https://docs.docker.com/get-docker/) on your local machine.

## Installation

To install and run the Flask Custom Bookmark Search locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/your_username/flask-custom-bookmark-search.git
    ```

2. Navigate to the project directory:

    ```bash
    cd flask-custom-bookmark-search
    ```

3. Build the Docker image:

    ```bash
    docker build -t flask-custom-bookmark-search .
    ```

4. Run the Docker container:

    ```bash
    docker run -p 5000:5000 flask-custom-bookmark-search
    ```

5. Access the application in your browser at `http://localhost:5000`.

## Usage

- Visit the URL `http://localhost:5000` in your web browser.
- Enter a command in the address bar to perform a redirection or search.
  - For predefined commands (e.g., `fb`, `wiki`), you will be redirected to the corresponding URL.
  - For search queries (e.g., `wiki How to use Docker`), you will be redirected to a search page.

## Configuration

- Add or modify predefined commands and their corresponding URLs in `app.py`.
- Customize search-related subdomains and their corresponding search domains in `app.py`.
- Adjust the default search domain in `app.py`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for feature requests, bug fixes, or improvements.
