from django.conf import settings
from django.contrib.auth.models import User
import bcrypt

class UnixAuth(object):
  supports_object_permissions = False
  supports_anonymous_user = False
  supports_inactive_user = False

  def authenticate(self, username=None, password=None):
    if password == "": # Default value
      return None
    # Try to authenticate with default backend
    try:
      # Return the local user, if login/pass match
      user = User.objects.get(username=username)
      if user.check_password(password):
        return user

      # Only the password is invalid. It is maybe outdated in database
      unix_pw = self.get_blowfish_passwd(username)
      if unix_pw and bcrypt.hashpw(password.encode('ascii'), unix_pw.encode('ascii')).decode('ascii') == unix_pw:
        user.set_password(password)
        user.save()
        return user

    # There is no local user
    except User.DoesNotExist:
      unix_pw = self.get_blowfish_passwd(username)
      # Credentials are ok, create a user in database
      if unix_pw and bcrypt.hashpw(password.encode('ascii'), unix_pw.encode('ascii')).decode('ascii') == unix_pw:
        user = User(username=username)
        user.set_password(password)
        user.save()
        return user

    # Invalid credentials
    return None

  def get_user(self, user_id):
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None

  def get_blowfish_passwd(self, login):
    with open(getattr(settings, 'UNIX_FILE', 'shadow.blowfish')) as f:
      for credentials in f.read().split("\n"):
        try:
          unix_l, unix_pw = credentials.split(":")[:2]
          if unix_l == login:
            return unix_pw
        except Exception as e:
          print(e)
          return
    return None
