# users/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    """ A form for user registration, extending Django's default UserCreationForm
        to include the email field directly on the signup form.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # Specify the fields to include in the form
        # We add 'email' to the default 'username'
        fields = ('username', 'email')

