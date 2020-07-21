# populates birds
import os

# configuring the default environement 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whistly_project.settings')

import django
django.setup()

import random
from birds.models import Bird
from users.models import CustomUser
from faker import Faker

fake = Faker()


def dummy_birds_multiply_users(n=10):
    """
    Populates the Bird's nest with data.
    1 User x 1 Bird
    """
    for x in range(n):
        
        user = fake.first_name()
        pwd = fake.pystr()
        email = fake.email()
        new_user = CustomUser(username=user,
                            password=pwd,
                            email=email)
        new_user.save()
        location = fake.country()
        comment = fake.paragraph()
        species = fake.last_name()
        new_bird = Bird(species=species,
                        location=location,
                        photographer=new_user,
                        photographer_comment=comment,
                        picture=(os.path.join('test_birds',
                                random.choice([x for x in os.listdir(os.path.join("media", "test_birds"))]))))
        new_bird.save()

def dummy_birds_single_user(n=10):
    """
    Populates the Bird's nest with data.
    1 User x (n)Birds
    """
    pwd = fake.pystr()
    email = fake.email()
    
    # un-comment if user hasn't been created yet
    # new_user = CustomUser(username='SuperUser',
    #                         password=pwd,
    #                         email=email)
    # new_user.save()

    Super_User = CustomUser.objects.get(username='SuperUser')

    for x in range(n):
        location = fake.country()
        comment = fake.paragraph()
        species = fake.last_name()
        new_bird = Bird(species=species,
                        location=location,
                        photographer=Super_User,
                        photographer_comment=comment,
                        picture=(os.path.join('test_birds',
                                random.choice([x for x in os.listdir(os.path.join("media", "test_birds"))]))))
        new_bird.save()

if __name__ == "__main__":
    print('Creating New Users and saving new birds!')
    # for single users with 1 bird each
    # dummy_birds_multiply_users(20)
    # for single user with multiple birds
    dummy_birds_single_user(5)
    print('Process completed')