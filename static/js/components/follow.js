Vue.component("follow-widget", {
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
        this.following = true;
        this.$buefy.toast.open({
          message: 'Successfully followed !',
          type: 'is-success'
        });
      } else {
        this.$buefy.toast.open({
          message: 'Failed to follow! Try again',
          type: 'is-danger'
        })
      }
    }, async unfollow() {
      const resp = await fetch(`/profile/unfollow/`, {
        body: "followee_id=" + this.followeeId,
        method: "POST", credentials: 'include', headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-CSRFToken': getCookie('csrftoken')
        }
      });
      if (resp.ok) {
        this.following = false;
        this.$buefy.toast.open({
          message: 'Successfully followed !',
          type: 'is-success'
        });
      } else {
        this.$buefy.toast.open({
          message: 'Failed to follow! Try again',
          type: 'is-danger'
        })
      }
    }
  },
  data: function() {
    return {
      following: false
    };
  },
  props: ["followeeId"],
  template:
    '<button v-if="!following" @click="follow">Follow</button>' +
      '<button v-else @click="unfollow">Unfollow</button>'
});
