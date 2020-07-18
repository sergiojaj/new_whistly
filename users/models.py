from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import uuid

from birds.utils import file_size

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, default='default/default_profile_pic.jpg', validators=[file_size])
    about_user = models.TextField(max_length=600, blank=True, default='Enter a nice description here')
    registered_at = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return super().username
    