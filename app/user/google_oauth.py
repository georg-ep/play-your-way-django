from user.models import User


class GoogleUser(object):
    USER_FIELD_NAME = 'google_id'

    def __init__(self, google_response):
        self.id = google_response['sub']
        self.email = google_response['email']
        self.given_name = google_response['given_name']
        self.family_name = google_response['family_name']

    def get_user(self):
        user, created = User.objects.get_or_create(email=self.email)
        user.google_id = self.id
        user.is_email_verified = True
        if created:
            user.name = self.given_name
            user.surname = self.family_name
        user.save()
        return user
