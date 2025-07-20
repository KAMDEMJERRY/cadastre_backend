import factory
from django.contrib.auth.models import User
from lotissement.models import Lotissement, Bloc, Parcelle
import random

class Userfactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class Lotissementfactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lotissement
    
    name = factory.Faker('company')
    addresse = factory.Faker('address')
    description = factory.Faker('text')

class Blocfactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bloc
    
    name = factory.Faker('building_number')
    lotissement = factory.SubFactory(Lotissementfactory)
    description = factory.Faker('sentence')

class Parcellefactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parcelle
    
    # bloc = factory.SubFactory(Blocfactory)
    # proprietaire = factory.SubFactory(Userfactory)
    superficie = factory.LazyAttribute(lambda _: random.uniform(100, 1000))
    perimetre = factory.LazyAttribute(lambda _: random.uniform(50, 200))