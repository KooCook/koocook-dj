from django.core.management.base import BaseCommand

from koocook_core import support
from koocook_core import models


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        self.stdout.write('calling createrecipe')
        from ._add_path import add_datatrans
        add_datatrans()
        self.main()

    def main(self):
        r = models.Recipe()
        r.name = 'BA’s Best Buttermilk Pancakes'
        r.author = models.Author.objects.create(name='Jessie Damuck')
        r.image = ['https://assets.bonappetit.com/photos/57acf4fdf1c801a1038bc954/16:9/w_2560,c_limit/buttermilk-pancakes.jpg']
        r.description = "To feed a larger group for breakfast, double the recipe and keep pancakes warm in a 250° oven between batches. This is part of BA's Best, a collection of our essential recipes."
        r.recipe_instructions = [
            'Whisk flour, sugar, baking powder, baking soda, and salt in a large bowl. Whisk eggs, buttermilk, and butter in a medium bowl; stir into dry ingredients until just combined (some lumps are okay).',
            'Heat a griddle or large skillet over medium; brush with oil. Working in batches, scoop ⅓-cupfuls of batter onto griddle. Cook pancakes until bottoms are golden brown and bubbles form on top, about 3 minutes. Flip and cook until cooked through and other side of pancakes are golden brown, about 2 minutes longer. Serve pancakes with maple syrup.',
        ]
        r.aggregate_rating = models.AggregateRating.create_empty(rating_value=4.5, rating_count=5)
        r.save()
        for quantity, name in (
                ('1⅓ cups', 'all-purpose flour'),
                ('3 tablespoons', 'sugar'),
                ('1 teaspoon', 'baking powder'),
                ('1 teaspoon', 'baking soda'),
                ('1 teaspoon', 'kosher salt'),
                (support.Quantity(0, support.unit.SpecialUnit.NONE), 'large eggs'),
                ('1¼ cups', 'buttermilk'),
                ('2 tablespoons', 'unsalted butter, melted'),
        ):
            meta = models.MetaIngredient.objects.create(name=name)
            models.RecipeIngredient.objects.create(recipe=r, meta=meta, quantity=quantity)
            self.stdout.write(f'created {name}')
