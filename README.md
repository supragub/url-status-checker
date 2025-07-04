# URL status checker

## About the project

Designed to check the status of URLs and API endpoints. This is not production ready, it is a proof of concept for a website status checker. Do not use it in production, it is not secure and does not handle errors properly. You can use it locally.

## Built with

[![Python][Python]][Python-url]
[![Flask][Flask]][Flask-url]
[![JavaScript][JavaScript]][JavaScript-url]
[![HTML5][HTML5]][HTML5-url]
[![CSS3][CSS3]][CSS3-url]

## Project Structure

```
url-status-checker/
├── app/                  # Main application package
│   ├── __init__.py       # Flask app factory
│   ├── routes.py         # Flask routes
│   ├── data/             # Data files (e.g., url_registry.json)
│   ├── static/           # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── templates/        # HTML templates
│       └── index.html
├── logs/                 # Log files
│   ├── flask_error.log
│   ├── flask_output.log
│   └── requirements.log
├── requirements.txt      # Python dependencies
├── run.py                # Entry point to run the Flask app
├── start.ps1       # Script to start the app locally (Windows)
├── .env.example          # Example environment variables
├── LICENSE
├── README.md
└── .gitignore
```

## Prerequisites:

### Install latest Python

Don't forget to add Python path to the environment variables.
Minimum requirements Python 3.8

```
https://www.python.org/downloads/
```

## Getting Started

### 1. Clone Bitbucket repository

```
git clone https://github.com/supragub/url-status-checker.git
```

### 2. Run app in local

Windows:

```
powershell.exe -File start.ps1
```

### 3. Shutdown app in local

Windows:
```
To stop the app, open Windows Task Manager and end the process named "Python".
```

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[Flask]: https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/
[JavaScript]: https://img.shields.io/badge/javascript-000000?style=for-the-badge&logo=javascript&logoColor=white
[JavaScript-url]: https://www.javascript.com/
[HTML5]: https://img.shields.io/badge/html5-000000?style=for-the-badge&logo=html5&logoColor=white
[HTML5-url]: https://html.spec.whatwg.org/
[CSS3]: https://img.shields.io/badge/css3-000000?style=for-the-badge&logo=css3&logoColor=white
[CSS3-url]: https://www.w3.org/Style/CSS/Overview.en.html