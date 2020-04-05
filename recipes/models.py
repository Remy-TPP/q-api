from django.db import models
from django.conf import settings

class Weight(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return '%s' % (self.name)       

class Amount(models.Model):
    unit = models.FloatField()
    weight = models.ForeignKey(Weight, on_delete=models.CASCADE)
        

class Ingredient(models.Model):
    name = models.CharField(max_length=300)
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % (self.name)

class Recipe(models.Model):
    title = models.CharField(max_length=300)
    desc = models.CharField(max_length=300)
    image = models.ImageField(upload_to='images/%Y-%m-%d')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')

    def __str__(self):
        return '%s' % (self.title)

# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
#     usertypes = models.ManyToManyField(UserType, related_name='users')
#     friends = models.ManyToManyField("self", blank=True)
#     groups = models.ManyToManyField(Group, related_name='users')

#     def __str__(self):
#         return '%s' % (self.user.username)