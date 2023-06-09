import os

import asyncpg
import uvicorn
from fastapi.openapi.utils import get_openapi

from lib.sql_connect import app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 10020 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Welcome to Cleaner app API",
        version="0.9",
        description="This is main API of project",
        routes=app.routes,
        tags=[
            {'name': 'System', 'description': "Checking login and password, as well as system settings."},
            {'name': 'Auth', 'description': "Auth user methods in server"},
            {'name': "User", 'description': "User's information. Checking login and password"},
            {'name': "Orders", 'description': "Work with orders in service"},
            {'name': "Message", 'description': "All routes about moder message line"},
            {'name': "For all", 'description': "Routes for all users"},
            {'name': "Work", 'description': "All about users work and work types"},
            {'name': "Admin users", 'description': "All admins routes for work with users"},

        ]
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

