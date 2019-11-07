Vue.component('ingredient-chooser', {
    computed: {
        liveIngredients() {
             for (let ingredient of this.ingredients) {
                 ingredient.quantity.number = this.convertToFactor(ingredient.quantity);
                 ingredient.quantity.prevUnit = ingredient.quantity.unit;
             }
             return this.ingredients;
         }
    },
    methods: {
        addIngredient() {
                this.ingredients.push({ name: '', type: 'volumeUnit', quantity: {'unit': 'tbsp', 'number': 0, 'prevUnit': 'tbsp'}})
        },
        getTypeByUnit(value, table) {
            for (const prop in table) {
                if (table.hasOwnProperty(prop))
                    if (table[prop].find(el => el.unit === value)) return prop;
            }
        },
         convertToFactor(quantity, conversion_table=CONVERSION_FACTORS) {
                const { unit, number, prevUnit } = quantity;
                const type = this.getTypeByUnit(unit, conversion_table);
                try {
                    const base = conversion_table[type].filter(x => x.unit === prevUnit)[0].value;
                    let conversionFactor = conversion_table[type].filter(x => x.unit === unit)[0].value / base;
                    return number * conversionFactor;
                } catch (e) {
                    return 0;
                }
            }
    },
  data: function () {
    return {
      count: 0,
    }
  }, props: ['ingredients', 'selectableUnits'],
  template: '<div><div class="is-centered" v-for="ingredient in liveIngredients" :key="ingredient.id">\n' +
      '        <input type="text" v-model="ingredient.name">\n' +
      '        <input autofocus v-model.trim="ingredient.quantity.number"> <b-select class="is-inline" v-model="ingredient.quantity.unit"\n' +
      '                    size="is-small">\n' +
      '                    <option v-for="(name, unit) in selectableUnits" :value="unit">{{ name }}</option>\n' +
      '        </b-select>\n' +
      '    ' +
      '    </div>' +
      '<button @click="addIngredient">Add an ingredient</button>' +
      '</div>'
});