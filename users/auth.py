from django.contrib.auth import get_user_model
from .models import CustomUser


class EmailOrUsernameModelBackend(object):

    def authenticate(self, username=None, password=None):
        # user_model = get_user_model()
        if '@' in username:
            # kwargs = {'email': username}
            field = 'email'
            print(field)
        else:
            # kwargs = {'username': username}
            field = 'username'
            print(field)
        try:

            case_insensitive_username_field = '{}__iexact'.format(field)
            user = CustomUser._default_manager.get(**{case_insensitive_username_field: username})

            # user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None