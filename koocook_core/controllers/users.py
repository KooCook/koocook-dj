from .base import BaseController
from ..models import KoocookUser


class UserProfileController(BaseController):

    def __init__(self, request_fields: dict):
        super().__init__(KoocookUser, request_fields)
