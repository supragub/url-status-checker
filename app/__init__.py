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
from flask import Flask
from dotenv import load_dotenv


def create_app():
    # Ellenőrizzük a környezeti változót, hogy megtudjuk, melyik fájlt kell betölteni
    # Alapértelmezett érték: production
    env = os.getenv('FLASK_ENV', 'production')

    if env == 'development':
        load_dotenv('.env.development')
    else:
        load_dotenv('.env.production')

    app = Flask(__name__, static_folder='static')

    # Flask konfiguráció beállítása a környezeti változókból
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Importáljuk az útvonalakat az inicializálás után
    with app.app_context():
        from app import routes

    return app
