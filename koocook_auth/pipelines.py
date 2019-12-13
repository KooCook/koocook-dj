from social_core.backends.google import GoogleOAuth2
import logging
import urllib.request

logger = logging.getLogger(__name__)


def associate_social_profile(backend, user, response, *args, **kwargs):
    if isinstance(backend, GoogleOAuth2):
        logger.info(f"Associate social profile with {user.username}")
        if response.get('picture'):
            url = response.get('picture')
            req = urllib.request.Request(url=url)
            resp = urllib.request.urlopen(req)
            if resp.status not in [400, 404, 403, 408, 409, 501, 502, 503]:
                user.koocook_user.avatar = {'type': 'url', 'content': url}
                user.koocook_user.save()
