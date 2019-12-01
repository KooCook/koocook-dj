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

const CONVERSION_FUNCTIONS = {};

const CONVERSION_UNITS = {
  tbsp: "US tablespoon",
  mL: "millilitre",
  g: "gram",
  kg: "kilogram",
  mg: "milligram"
};

const GLOBAL_DATA = {
  searchName: '',
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

Vue.filter("time-passed", function(date) {
  return moment(date).fromNow();
});
