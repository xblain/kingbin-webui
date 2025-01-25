from django.db import models
from .managers import DiscordUserOAuth2Manager
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager, PermissionsMixin
class MyUserManager(BaseUserManager):
    def create_superuser(self, email, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
# Create your models here.
class DiscordUser(AbstractBaseUser,PermissionsMixin):
    objects = DiscordUserOAuth2Manager()
    id = models.DecimalField(primary_key=True, max_digits=99, decimal_places=0,)
    discord_tag = models.CharField(max_length=100)
    avatar = models.CharField(max_length=100)
    public_flags = models.IntegerField()
    flags = models.IntegerField()
    locale = models.CharField(max_length=100)
    mfa_enabled = models.BooleanField()
    last_login = models.DateTimeField(null=True)
    token = models.CharField(max_length=100)
    refreshtoken = models.CharField(max_length=100)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []
    def __str__(self):
        return str(self.id)


    #def is_authenticated(self, request):
    #    return True


    #def is_anonymous(self, request):
    #    return False

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_full_name(self):
        pass

    def get_short_name(self):
        pass
    
class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    sauce = models.BigIntegerField(default=0)
    coins = models.BigIntegerField(default=0)
    emoji = models.CharField(max_length=100, default="")
    category = models.BigIntegerField(default=0)
    for_sale = models.BooleanField(default=False)
    tradeable = models.BooleanField(default=False)





