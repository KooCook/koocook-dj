from social_core.backends.google import GoogleOAuth2


def associate_social_profile(backend, user, response, *args, **kwargs):
    if isinstance(backend, GoogleOAuth2):
        print(response.get('picture'))
        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')
            ext = url.split('.')[-1]
            user.avatar.save(
               '{0}.{1}'.format('avatar', ext),
               ContentFile(urllib2.urlopen(url).read()),
               save=False
            )
            user.save()
