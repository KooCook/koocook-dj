from django.contrib import admin

from koocook_core.models import *

# Register your models here.
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(MetaIngredient)
admin.site.register(KoocookUser)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Rating)
admin.site.register(AggregateRating)
admin.site.register(Tag)
admin.site.register(TagLabel)
admin.site.register(Comment)


class FeedbackAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('subject', 'body', 'image_tag', 'video_tag')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('author', 'status'),
        }),
    )
    list_display = ('subject', 'date_published', 'was_solve')
    list_filter = ['date_published']
    actions = ['solved', 'unsolved']
    readonly_fields = ('image_tag', 'video_tag', )

    def solved(self, request, queryset):
        queryset.update(status=True)

    def unsolved(self, request, queryset):
        queryset.update(status=False)

    solved.short_description = "Mark selected stories as solved"
    unsolved.short_description = "Mark selected stories as unsolved"


admin.site.register(Feedback, FeedbackAdmin)
