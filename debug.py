import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from core.views import CustomUserCreationForm
from core.models import User

print("Custom form meta model:", CustomUserCreationForm._meta.model)


from django.http import QueryDict
data = QueryDict(mutable=True)
data.update({
    'username': 'anjuadmin012',
    'password1': "asdfg123l;'",
    'password2': "asdfg123l;'",
    'role': 'SHOPKEEPER',
})

form = CustomUserCreationForm(data=data)
print("Is valid?", form.is_valid())

