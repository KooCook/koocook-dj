const CONVERSION_FACTORS = {
  volumeUnit: [
    { unit: "tbsp", value: 0.000015 },
    { unit: "tsp", value: 0.000005 },
    { unit: "cup", value: 0.00024 },
    { unit: "mL", value: 0.001 },
    { unit: "cu.m.", value: 1 }
  ],
  massUnit: [
    { unit: "g", value: 0.001 },
    { unit: "mg", value: 0.000001 },
    { unit: "kg", value: 1 }
  ]
};

const glob = { FOLLOWING: [] };
Vue.prototype.$glob = glob;

const CONVERSION_UNITS = {
  tbsp: "US tablespoon",
  mL: "millilitre",
  g: "gram",
  kg: "kilogram",
  mg: "milligram"
};

const GLOBAL_DATA = {
  searchTerm: '',
  searchParams: '',
  isFiltersOpen: false
};

String.prototype.format = function() {
  let str = this;
  for (const arg in arguments) {
    str = str.replace("{" + arg + "}", arguments[arg])
  }
  return str
};

function getCookie(name) {
  const re = new RegExp(name + "=([^;]+)");
  const value = re.exec(document.cookie);
  return value != null ? unescape(value[1]) : null;
}

String.prototype.format = function() {
  let str = this;
  for (const arg in arguments) {
    str = str.replace("{" + arg + "}", arguments[arg])
  }
  return str
};

function getCookie(name) {
  const re = new RegExp(name + "=([^;]+)");
  const value = re.exec(document.cookie);
  return value != null ? unescape(value[1]) : null;
}

Vue.filter("time-passed", function(date) {
  return moment(date).fromNow();
});

Vue.filter("pluralize", function(unit, num) {
  num = num.toString().replace('/1','');

  if (!unit.singular) unit.singular = unit.symbol;
  if (!unit.plural) unit.plural = unit.symbol;
  // console.log(num + `${parseInt(num) - 1 === 0 ? unit.plural : unit.plural }`);
  return `${parseInt(num) - 1 === 0 ? unit.singular : unit.plural }`
});