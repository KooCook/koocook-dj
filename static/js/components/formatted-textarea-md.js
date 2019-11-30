Vue.component("formatted-textarea-md", {
  props: ["value", "placeholder", "required"],
  template: `
    <textarea ref="area" :placeholder="placeholder" required autofocus></textarea>
  `,
  mounted() {
    this.mde = new SimpleMDE({
      hideIcons: ["quote", "guide", "side-by-side", "fullscreen"],
      element: this.$refs.area,
      forceSync: true,
      spellChecker: true
    });
    this.mde.value(this.value);
    const self = this;
    this.mde.codemirror.on("change", function() {
      self.$emit("input", self.mde.value());
    });
  },
  watch: {
    value(newVal) {
      if (newVal !== this.mde.value()) {
        this.mde.value(newVal);
      }
    }
  },
  beforeDestroy() {
    this.mde.toTextArea();
  }
});
