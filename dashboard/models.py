from django.db import models

# Create your models here.
class DiscordGuild(models.Model):
    id = models.BigIntegerField(primary_key=True)
    enabled = models.BooleanField(default=True)
    crib_enabled = models.BooleanField(default=False)
    crib_list = models.JSONField(default='[]')
    sauce_enabled = models.BooleanField(default=False)
    sauce_list = models.JSONField(default='[]')
    cartel_enabled = models.BooleanField(default=False)
    cartel_list = models.JSONField(default='[]')
    welcome_enabled = models.BooleanField(default=False)
    welcome_channel = models.BigIntegerField(default='0')
    welcome_list = models.JSONField(default='[]')
    attack_list = models.JSONField(default='[]')
    attack_choices = (
        ('A', 'Attack'),
        ('P', 'Prank'),
    )
    languages = (
        ('0', 'EN'),
        ('1', 'NL'),
    )
    attack_choice = models.CharField(max_length=1, choices=attack_choices,default='A')
    language = models.CharField(max_length=1, choices=languages,default='0')