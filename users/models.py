from django.db import models


class UserType(models.Model):
	name = models.CharField(max_length=300, unique=True)

	def __str__(self):
		return '%s' % (self.name)

class User(models.Model):
	username = models.CharField(max_length=300, unique=True, blank=True)
	email = models.EmailField(max_length=300, unique=True, blank=True)
	name = models.CharField(max_length=300, blank=True)
	lastname = models.CharField(max_length=300, blank=True)
	usertype = models.ForeignKey(UserType, related_name='users', on_delete=models.CASCADE, null=True)

	def __str__(self):
		return '%s' % (self.username)

class Group(models.Model):
	name = models.CharField(max_length=300)
	users = models.ManyToManyField(User, related_name='groups')

	def __str__(self):
		return '%s' % (self.name)