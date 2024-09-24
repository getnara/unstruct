from django.contrib.auth.models import AbstractUser

from apps.common.models import NBaseModel


class User(NBaseModel, AbstractUser):
    pass
