/**
 * A Vue component
 * Comments widget
 *
 * @param {item-id} - An item id (required)
 * @param {item-name} - An item name
 *
 * @requires {COMMENTS_ENDPOINTS} - URL endpoints for each HTTP verbs, namely GET, POST, and PATCH.
 *
 */

const REPLIES_ENDPOINTS = {
    GET: `/comments/{0}`,
    POST: `/comments/`,
    PATCH: `/comments/{0}`,
};

Vue.component("comments-widget", {
  data: function() {
    return {
      comment_endpoints: COMMENTS_ENDPOINTS,
      replies: 0,
      comments: [],
      comment: {
        body: ''
      },
      pending: false,
    };
  },
  props: ["itemId", "itemName", "isReply", "customUrl"],
  template: '<div style="display: block;"><article class="media" v-for="(comment, index) in comments" :key="index">\n' +
      '          <figure class="media-left">\n' +
      '            <p class="image is-64x64">\n' +
      '              <img src="../assets/img/placeholders/128x128.png">\n' +
      '            </p>\n' +
      '          </figure>\n' +
      '          <div class="media-content">\n' +
      '            <div class="content">\n' +
      '              <p>\n' +
      '                <strong>{{ comment.author.qualified_name }}</strong>\n' +
      '                <br>{{ comment.body }}\n' +
      '                <br>\n' +
      '                <small><!--<a>Like</a> ·--> <a @click="comment.showReplies = !comment.showReplies"><span v-if="!comment.showReplies"><span v-if="comment.replies">{{ comment.replies }} </span>Reply</span><span v-else>Hide replies</span></a> · {{ comment.date_published|time-passed }}</small>\n' +
      '              </p>\n' +
      '             </div>' +
      '           <comments-widget @declare_replies="comment.replies = $event" v-show="comment.showReplies" is-reply="true" :item-id="comment.id" item-name="this comment"></comments-widget>\n' +
      '          </div>\n' +
      '        </article>' +
      '       <article class="media">\n' +
      '          <figure class="media-left">\n' +
      '            <p class="image is-64x64">\n' +
      '              <img src="../assets/img/placeholders/128x128.png">\n' +
      '            </p>\n' +
      '          </figure>\n' +
      '          <div class="media-content" id="comments">\n' +
      '              <form method="post" novalidate @submit.prevent="postComment()">\n' +
      '                  \n' +
      '                  <strong>What do you think about {{ itemName }}?</strong>\n' +
      '                <div class="field">\n' +
      '                  <p class="control">\n' +
      '                      <textarea v-model="comment.body" placeholder="Add a comment..." required="required" class="textarea"></textarea>\n' +
      '                  </p>' +
      '<b-loading :is-full-page="false" :active.sync="pending"></b-loading>' +
      '                       \n' +
      '                </div>\n' +
      '                <div class="field">\n' +
      '                  <p class="control">\n' +
      '                    <button class="button is-primary" type="submit"> Post comment</button>\n' +
      '                  </p>\n' +
      '                </div>\n' +
      '              </form>\n' +
      '          </div>\n' +
      '        </article>' +
      '</div>\n',
  mounted: async function () {
    let comments = await this.prefetchData();
    comments.forEach(function(v){ v.showReplies = false; v.replies = 0; });
    if (this.isReply) this.$emit('declare_replies', comments.length);
    this.comments = comments
  },
  methods: {
    async prefetchData() {
      this.comment_endpoints = this.isReply ? REPLIES_ENDPOINTS : COMMENTS_ENDPOINTS;
      const endpoint = this.isReply || this.customUrl ? this.comment_endpoints.GET.format(this.itemId) : this.comment_endpoints.GET
      return JSON.parse((await (await fetch(endpoint)).json()).current);
    },
    async postComment() {
      if (this.pending) return;
      this.pending = true;
      const endpoint =this.customUrl ?  this.comment_endpoints.POST.format(this.itemId) : this.comment_endpoints.POST
       const resp = await fetch(endpoint, {
        body: "body=" + this.comment.body + "&item_id=" + this.itemId,
        method: "POST", credentials: 'include', headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-CSRFToken': getCookie('csrftoken')
        }
      });
      if (resp.ok) {
        this.pending = false;
        this.$buefy.toast.open({
          message: 'Successfully commented!',
          type: 'is-success'
        }); this.comments.push(JSON.parse((await resp.json()).current))
      } else {
        this.pending = false;
        this.$buefy.toast.open({
          message: 'Commenting failed! Try again',
          type: 'is-danger'
        })
      }
    }
  }
});