# This file is part of URL Status Checker.
#
# Copyright (C) 2024 Gabor VARGA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import subprocess
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def start_status_checker():
    """Start the status_checker.py script."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        status_checker_path = os.path.join(base_dir, 'status_checker.py')
        logs_dir = os.path.join(base_dir, '..', 'logs')

        with open(os.path.join(logs_dir, 'status_checker_output.log'), 'w') as out, open(os.path.join(logs_dir, 'status_checker_error.log'), 'w') as err:
            subprocess.Popen([sys.executable, status_checker_path],
                             stdout=out, stderr=err, cwd=base_dir)
    except Exception as e:
        print(f"Failed to start status_checker.py: {e}")


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static')

    # Set the secret key to a random value if not set in the environment
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

    with app.app_context():
        from app import routes

    start_status_checker()

    return app

