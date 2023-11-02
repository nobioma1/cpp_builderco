from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

UserModel = get_user_model()


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        first_name_field = self.fields["first_name"]
        first_name_field.widget.attrs["autofocus"] = True
        first_name_field.widget.attrs.update({
            "required": ''
        })

        self.fields["last_name"].widget.attrs.update({
            "required": ''
        })

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'password1', "password2"]
