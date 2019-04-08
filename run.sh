#!/bin/bash
export FLASK_APP="app:create_app('development')"
export FLASK_ENV=development
flask run
