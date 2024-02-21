from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import sys


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        # if not username:
        #     raise ValueError(_('The username must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # user.username = email
        user.set_password(password)
        user.save()
        return user

    def create_admin(self, username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError(_('The username must be set'))
        # email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def validateEmail(self, email):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        try:
            if self.validateEmail(username):
                return self.create_user(username, password, **extra_fields)
            else:
                return self.create_admin(username, password, **extra_fields)
        except ValidationError as e:
            raise ValueError('on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e))