Vue.component('ingredient-chooser', {
    computed: {
        liveIngredients() {
          for (const ingredient of this.ingredients) {

             ingredient.quantity.number = this.convertToFactor(ingredient.quantity, ingredient.quantity.unit, ingredient.type);
             ingredient.quantity.prevUnit = ingredient.quantity.unit;
          }
          return this.ingredients;
        }

    },
    methods: {
        addIngredient() {
                this.ingredients.push({ name: '', type: 'volumeUnit', quantity: {'unit': 'tbsp', 'number': 0, 'prevUnit': 'tbsp'}})
        },
         convertToFactor(quantity, dest_unit, type='volumeUnit', conversion_table=CONVERSION_FACTORS) {
                const { unit, number } = quantity;
                const base = conversion_table[type].filter(x => x.unit === unit)[0].value;
                let conversionFactor = conversion_table[type].filter(x => x.unit === dest_unit)[0].value/base;
                return number*conversionFactor;
            }
    },
  data: function () {
    return {
      count: 0
    }
  }, props: ['ingredients'],
  template: '<div><div class="is-centered" v-for="ingredient in liveIngredients" :key="ingredient.name">\n' +
      '        <input type="text" v-model="ingredient.name">\n' +
      '        <input autofocus v-model.trim="ingredient.quantity.number"> <b-select class="is-inline" v-model="ingredient.quantity.unit"\n' +
      '                    size="is-small">\n' +
      '                    <option value="tbsp">US Tablespoon</option>\n' +
      '                    <option value="mL">Milliliter</option>\n' +
      '        </b-select>\n' +
      '    ' +
      '    </div>' +
      '<button @click="addIngredient">Add an ingredient</button>' +
      '</div>'
});