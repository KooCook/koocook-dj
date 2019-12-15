from django.db import models
from django.contrib.postgres import fields
from django.utils.safestring import mark_safe

__all__ = ('Feedback',)


class Feedback(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True
    )
    date_published = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    image = fields.ArrayField(models.CharField(max_length=200), null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    status = models.BooleanField(default=False)

    def was_solve(self):
        return self.status

    @mark_safe
    def image_tag(self):
        tag = u''
        if self.image is not None:
            for img in self.image:
                if img[0] == '[':
                    img = img[1:]
                if img[-1] == ']':
                    img = img[:-1]
                tag += u'<img src=%s style="width: 80vw; height: auto; margin-bottom: 12px;"/>' % img
        return tag

    @mark_safe
    def video_tag(self):
        tag = u''
        if self.video is not None:
            tag += u'<iframe src=%s width=80vw height=auto style="margin-bottom: 12px;"></iframe>' % self.video
        return tag

    def __str__(self):
        return self.subject

    was_solve.boolean = True
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    video_tag.short_description = 'Video'
    video_tag.allow_tags = True
