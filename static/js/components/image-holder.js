Vue.component("image-holder", {
    template: '<div><input type="hidden" name="image" id="id_image" v-model="JSON.stringify(images)">' +
        '<input type="hidden" name="video" id="id_video">' +
        '<form v-if="showAttach" class="holder-form" use-html5-validation @submit.prevent="addImage"> <span class="details"><a class="delete" @click="hideAttachDialog()"></a>\n' +
        '        <div class="content"><span v-for="(url,i) in attachmentUrls"> Image {{ i+1 }} URL:<b-field>\n' +
        '            <b-input v-model="url.src" placeholder="Enter the URL of an image"\n' +
        '                size="is-small"\n' +
        '                icon="link" type="url" required>\n' +
        '            </b-input></b-field>'+
        '        </span><button class="button add-url-row" type="button" @click="addUrl()">' +
        '             <b-icon   icon="plus"\n' +
        '                size="is-medium">\n' +
        '            </b-icon></button>' +
        '<button type="submit">Attach links</button></div>' +
        '        \n' +
        '    </span></form>' +
        '<b-carousel  v-if="carousels.length > 0"\n' +
        '            :indicator="true"\n' +
        '            :indicator-inside="indicatorInside"\n' +
        '            :indicator-mode="indicatorMode"\n' +
        '            :indicator-style="indicatorStyle">\n' +
        '<b-carousel-item v-for="(carousel, i) in carousels" :key="i">\n' +
        '<span v-if="carousel.src" class="image">\n' +
        '              <img class="recipe-image-carousel" :src="carousel.src">\n' +
        '            </span>' +
        '                <section v-else :class="`hero is-medium is-${carousel.color}`">\n' +
        '                    <div class="hero-body has-text-centered">\n' +
        '                        <h1 class="title">{{carousel.title}}</h1>\n' +
        '                    </div>' +
        '                </section>\n' +
        '            </b-carousel-item>' +
        '<button class="add-another-image-btn" type="button" @click="showAttachDialog()">Hi</button>' +
        '           \n' +
        '        </b-carousel><div @click="showAttachDialog()" :class="showAttach ? \'dashed-placeholder expanded\' : \'dashed-placeholder\'" v-else>' +
        '<div><div class="is-horizontal-center"><img src="https://image.flaticon.com/icons/svg/1515/1515601.svg" width="75px"></div>' +
        '<div>No image attached. Please attach at least one.</div>' +
        '        </div></div></div>',
    data() {
        return {
            email: '',
            images: [],
            showAttach: false,
            expandedClass: 'expanded',
            indicator: true,
            indicatorInside: true,
            indicatorMode: 'hover',
            indicatorStyle: 'is-dots',
            attachmentUrls: [
                { src: '' }
            ],
            carousels: [
                // { title: 'Slide 1', color: 'info' },
                // { title: 'Slide 2', color: 'success' },
                // { title: 'Slide 3', color: 'warning' },
                // { title: 'Slide 4', color: 'danger' }
            ]
        }
    },
    methods: {
        showAttachDialog() {
            this.showAttach = true;
            this.indicator = true;
        },
        hideAttachDialog() {
            this.showAttach = false;
            this.indicator = false;
        },
        addImage() {
            this.carousels = this.attachmentUrls;
            this.images = [];
            this.carousels.forEach(element => this.images.push(element.src));
            this.showAttach = false;

        },
        addUrl() {
            this.attachmentUrls.push({ src: '' });
        }
    },
    props: ['videos']
});