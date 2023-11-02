from django.urls import reverse_lazy
from django.views import generic

from .forms import SignupForm


class SignupView(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
