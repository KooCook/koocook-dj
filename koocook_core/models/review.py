from django.db import models

__all__ = ['Comment', 'Rating', 'AggregateRating']


class Comment(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField()
    body = models.TextField()
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
    )
    # item_reviewed = models.URLField()
    reviewed_recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_post = models.ForeignKey(
        'koocook_core.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @property
    def item_reviewed(self):
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @item_reviewed.setter
    def item_reviewed(self, obj):
        from koocook_core.models.recipe import Recipe
        from koocook_core.models.post import Post
        try:
            if self.reviewed_recipe:
                assert isinstance(obj, Recipe)
                self.reviewed_recipe = obj
            elif self.reviewed_post:
                assert isinstance(obj, Post)
                self.reviewed_post = obj
            elif self.reviewed_comment:
                assert isinstance(obj, self.__class__)
                self.reviewed_comment = obj
        except AssertionError as e:
            raise TypeError('item_reviewed must be of the correct type '
                            '\'{}\' not \'\''.format(
                             type(self.reviewed_recipe or self.reviewed_post or self.reviewed_comment),
                             type(obj))) from e.__context__


class Rating(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    rating_value = models.IntegerField()
    best_rating = models.IntegerField()
    worst_rating = models.IntegerField()
    # item_reviewed = models.URLField()
    reviewed_recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_post = models.ForeignKey(
        'koocook_core.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_comment = models.ForeignKey(
        'koocook_core.Comment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @property
    def item_reviewed(self):
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @item_reviewed.setter
    def item_reviewed(self, obj):
        from koocook_core.models.recipe import Recipe
        from koocook_core.models.post import Post
        try:
            if self.reviewed_recipe:
                assert isinstance(obj, Recipe)
                self.reviewed_recipe = obj
            elif self.reviewed_post:
                assert isinstance(obj, Post)
                self.reviewed_post = obj
            elif self.reviewed_comment:
                assert isinstance(obj, Comment)
                self.reviewed_comment = obj
        except AssertionError as e:
            raise TypeError('item_reviewed must be of the correct type '
                            '\'{}\' not \'\''.format(
                             type(self.reviewed_recipe or self.reviewed_post or self.reviewed_comment),
                             type(obj))) from e.__context__


class AggregateRating(models.Model):
    rating_value = models.DecimalField(
        decimal_places=10,
        max_digits=13,
        # every vote counts until 10 B
    )
    rating_count = models.IntegerField()
    best_rating = models.IntegerField()
    worst_rating = models.IntegerField()

    def add_rating(self, rating: Rating):
        pass

    def remove_rating(self, rating: Rating):
        pass

    @property
    def item_reviewed(self):
        return self.recipe or self.post or self.comment
