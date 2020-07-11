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

def dummy_birds(n=10):
    """
    Populates the Bird's nest with data.
    """
    
    many_birds = CustomUser.objects.get(username='many_birds')

    for x in range(n):
        
        # # user = fake.first_name()
        # pwd = fake.pystr()
        # email = fake.email()
        
        # new_user = CustomUser(username='bird_collector',
        #                     password=pwd,
        #                     email='bird_collector@email.com')

        # new_user.save()
        
        location = fake.country()
        comment = fake.paragraph()
        species = fake.last_name()

        new_bird = Bird(species=species,
                        location=location,
                        photographer=many_birds,
                        photographer_comment=comment,
                        picture=('test_birds\\' +
                                random.choice([x for x in os.listdir("media\\test_birds")])))
        
        new_bird.save()

if __name__ == "__main__":
    print('Creating New Users and saving new birds!')
    dummy_birds(20)
    print('Process completed')