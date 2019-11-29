Vue.component("star-rating", {
    props: { itemId: Number, initial: {
            type: [Number, String], default: 0
        },
        rateUrl: String,
        recipeName: String,
        readOnly: {
            type: Boolean, default: false
        } },
    data() {
        return {
            ratingScore: parseFloat(this.initial),
            max: 5,
            change: false
        }
    },
    template: `
    <b-rate v-model="ratingScore"
            
            icon="star"
            :max="max"
            :disabled="readOnly">
        </b-rate>
    `,
    watch: {
        ratingScore: async function (score) {
            const rateURL = this.rateUrl && this.itemId ? this.rateUrl : `/recipes/${this.itemId}/rate`;
            if (score < 1) return;
            const resp = await fetch(rateURL, {
                body: "rating_score=" + score,
                method: "POST", credentials: 'include', headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-CSRFToken': getCookie('csrftoken')
                }
              });
              if (resp.ok) {
                 this.ratingScore = parseInt((await resp.json()).current['rating_value']);
                this.$buefy.toast.open({
                  message: this.recipeName ? `Rated ${this.recipeName}!`: 'Rated!',
                  type: 'is-success'
                })
              } else {
                this.$buefy.toast.open({
                  message: this.recipeName ? `Failed to rate ${this.recipeName}! Try again`: 'Failed to rate! Try again',
                  type: 'is-danger'
                })
              }
        }
    }
});
