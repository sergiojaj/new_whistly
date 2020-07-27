from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

# to manage uploaded files while still in memory (before saving)
from django.core.files.uploadedfile import InMemoryUploadedFile

import uuid

# to save the newly resized image into memory before saving
from io import BytesIO
from PIL import Image
import sys

from .utils import file_size

# Create your models here.

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ''created'' and 
    ''modified'' fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Bird(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    species = models.CharField(max_length=150, blank=False)
    location = models.CharField(max_length=200, blank=False)
    picture = models.ImageField(upload_to='bird', blank=False, validators=[file_size])
    photographer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='photographers',)
    photographer_comment = models.TextField(max_length=500)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.species

    def get_absolute_url(self):
        return reverse("bird_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """
        Resize image before calling save()
        Using ByteIO() to encode and save the file into system memory
        before saving to filesystem.
        """
        image = Image.open(self.picture)
        output = BytesIO()
        width, height = image.size
        image = image.resize((int(width/2),int(height/2)),
                                Image.ANTIALIAS)
        image.save(output, format='JPEG', optimize=True, quality=75)
        output.seek(0)
        self.picture = InMemoryUploadedFile(output, 'ImageField', self.picture.name, 'image/jpeg', output.tell(), None)
        return super().save(*args, **kwargs)
    
    def rotate_right(self, *args, **kwards):
        """
        Method to rotate pictures uploaded by users by 90 degrees
        """
        original = Image.open(self.picture)
        rotated = BytesIO()
        original = original.transpose(Image.ROTATE_90)
        original.save(rotated, format='JPEG')
        rotated.seek(0)
        self.picture = InMemoryUploadedFile(rotated, 'ImageField', self.picture.name, 'image/jpeg', rotated.tell(), None)
        self.rotate_save()
        
        return reverse('bird_detail', kwargs={'pk':self.pk})

    def rotate_left(self, *args, **kwards):
        """
        Method to rotate pictures uploaded by users by 270 degrees
        """
        original = Image.open(self.picture)
        rotated = BytesIO()
        original = original.transpose(Image.ROTATE_270)
        original.save(rotated, format='JPEG')
        rotated.seek(0)
        self.picture = InMemoryUploadedFile(rotated, 'ImageField', self.picture.name, 'image/jpeg', rotated.tell(), None)
        self.rotate_save()
        print('this is left')
        return reverse('bird_detail', kwargs={'pk':self.pk})

    def rotate_save(self, *args, **kwargs):
        """
        Save rotated image without changing its quality as the
        custom method save
        """
        return super().save(*args, **kwargs)
    
class Comment(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    comment = models.CharField(max_length=600, blank=False)
    comment_approved = models.BooleanField(default=False)
    bird = models.ForeignKey(Bird,
                        on_delete=models.CASCADE,
                        related_name='comments',)
    comment_creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,        
    )

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        return reverse("bird_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.comment


class Reply(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    reply = models.CharField(max_length=600, blank=False)
    reply_approved = models.BooleanField(default=False)
    comment = models.ForeignKey(Comment, 
        on_delete=models.CASCADE,
        related_name='replies',)
    reply_creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,        
    )

    def __str__(self):
        return self.reply

class Seed(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seeded = models.BooleanField(default=False)
    seeder = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    bird = models.ForeignKey(Bird,
                         on_delete=models.CASCADE,
                         related_name='seeds',)
    
    def __str__(self):
        return f'Seeder: {self.seeder} on bird {self.bird}'