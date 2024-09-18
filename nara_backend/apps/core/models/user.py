from django.contrib.auth.models import AbstractUser

from .base import NBaseModel


class User(NBaseModel, AbstractUser):
    pass