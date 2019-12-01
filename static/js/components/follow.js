
Object.assign(GLOBAL_DATA, { followees: [] });
Vue.component("follow-widget", {
  computed: {
    following: function() {
      return this.followees.findIndex(obj => obj.id === this.followeeId) !== -1;
      }
  },
  methods: {
    async follow() {
      const resp = await fetch(`/profile/follow/`, {
        body: "followee_id=" + this.followeeId,
        method: "POST", credentials: 'include', headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-CSRFToken': getCookie('csrftoken')
        }
      });
      if (resp.ok) {
        this.followees.push((await resp.json()).current);
      } else {
        this.$buefy.toast.open({
          message: 'Failed to follow! Try again',
          type: 'is-danger'
        })
      }
    },
    async unfollow() {
      const resp = await fetch(`/profile/unfollow/`, {
        body: "followee_id=" + this.followeeId,
        method: "POST", credentials: 'include', headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-CSRFToken': getCookie('csrftoken')
        }
      });
      if (resp.ok) {
        const idx = this.followees.findIndex(obj => obj.id === this.followeeId);
        this.followees.splice(idx, 1);
      } else {
        this.$buefy.toast.open({
          message: 'Failed to follow! Try again',
          type: 'is-danger'
        })
      }
    },

  },
  data: function() {
    return {
      followee: {}
    };
  },
  props: ["followeeId", "followees"],
  template:
    '<button v-if="!following" @click="follow">Follow</button>' +
      '<button v-else @click="unfollow">Unfollow</button>',
      mounted: async () => {

          const resp = await fetch(`/profile/follow/`, {
              method: "GET", credentials: 'include', headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-CSRFToken': getCookie('csrftoken')
              }
             });
            if (resp.ok) {
              if (typeof (await resp.clone().json()).current == "undefined") this.app.$data.followees = [];
              else this.app.$data.followees = (await resp.clone().json()).current;
              this.app.$forceUpdate();
            } else {
              this.$buefy.toast.open({
                message: 'Failed to follow! Try again',
                type: 'is-danger'
              })
            }
    }
});
