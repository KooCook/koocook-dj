from koocook_core.models import Author, Recipe, Post, Comment


def main():
    for i, author in enumerate(Author.objects.all()):
        m = i % 4
        if m % 2 == 0:
            Recipe.objects.create(author=author, name=f'recipe {i}')
        if m % 2 == 1:
            Post.objects.create(author=author)
    authors = Author.objects.all()
    for i, obj in enumerate(list(Recipe.objects.all()) + list(Post.objects.all())):
        m = i % 4
        if m % 2 == 0:
            comment = Comment.objects.create(author=authors[i], item_reviewed=obj)
        if m == 2:
            Comment.objects.create(author=authors[i - 1], reviewed_comment=comment)
