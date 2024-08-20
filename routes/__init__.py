from flask import Blueprint

from .home import home_router
from .auth import auth_router

ROUTES: list[Blueprint] = [
    home_router,
    auth_router
]