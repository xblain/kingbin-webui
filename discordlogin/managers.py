from django.contrib.auth import models

class DiscordUserOAuth2Manager(models.UserManager):
    def createNewDiscordUser(self, user):
        print('Inside Discord User Manager')
        discordTag = '%s#%s' %(user['username'], user['discriminator'])
        newUser = self.create(
            id=user['id'],
            avatar=user['avatar'],
            public_flags=user['public_flags'],
            flags=user['flags'],
            locale=user['locale'],
            mfa_enabled=user['mfa_enabled'],
            discord_tag=discordTag,
            token='0',
            refreshtoken='0',
            is_staff='0',

        )
        return newUser