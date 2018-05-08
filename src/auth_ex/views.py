from django.views.generic.edit import CreateView

from .models import User
from .forms import RegistrationForm


class UserCreateView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'auth/registration.html'
