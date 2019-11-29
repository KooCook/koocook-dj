Vue.component("ingredient-chooser", {
  computed: {
    liveIngredients() {
      for (let ingredient of this.ingredients) {
        const { number, type } = this.convertToFactor(ingredient.quantity);
        ingredient.type = type;
        ingredient.quantity.number = number;
        ingredient.quantity.prevUnit = ingredient.quantity.unit;
      }
      return this.ingredients.filter(item => !item.removed);
    }
  },
  methods: {
    addIngredient() {
      this.ingredients.push({
        name: "",
        type: "volumeUnit",
        quantity: { unit: "tbsp", number: 0, prevUnit: "tbsp" },
        added: true
      });
    },
    removeIngredient(ingredient) {
      ingredient.removed = true;
      const index = this.ingredients.findIndex(x => x === ingredient);
      if (ingredient.added) this.ingredients.splice(index, 1);
      this.ingredients.push({});
      this.ingredients.pop();
    },
    getTypeByUnit(value, table) {
      for (const prop in table) {
        if (table.hasOwnProperty(prop))
          if (table[prop].find(el => el.unit === value)) return prop;
      }
    },
    convertToFactor(quantity, conversion_table = CONVERSION_FACTORS) {
      const { unit, number, prevUnit } = quantity;
      const type = this.getTypeByUnit(unit, conversion_table);
      try {
        const base = conversion_table[type].filter(x => x.unit === prevUnit)[0]
          .value;
        let conversionFactor =
          conversion_table[type].filter(x => x.unit === unit)[0].value / base;
        return { number: number * conversionFactor, type };
      } catch (e) {
        return { number: number, type };
      }
    }
  },
  data: function() {
    return {
      count: 0
    };
  },
  props: ["ingredients", "selectableUnits"],
  template:
    '<div><div class="is-centered" v-for="ingredient in liveIngredients" :key="ingredient.id">\n' +
    '        <input type="text" v-model="ingredient.name">\n' +
    '        <input autofocus v-model.trim="ingredient.quantity.number"> <b-select class="is-inline" v-model="ingredient.quantity.unit"\n' +
    '                    size="is-small">\n' +
    '                    <option v-for="(name, unit) in selectableUnits" :value="unit">{{ name }}</option>\n' +
    "        </b-select>\n" +
    `    <button type="button" @click='removeIngredient(ingredient)'>-</button>` +
    "    </div>" +
    '<button type="button" @click="addIngredient">Add an ingredient</button>' +
    "</div>"
});
