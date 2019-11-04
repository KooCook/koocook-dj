from django.contrib import admin

from koocook_core.models import *

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(MetaIngredient)
admin.site.register(KooCookUser)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Rating)
admin.site.register(AggregateRating)
admin.site.register(Tag)
admin.site.register(Comment)


