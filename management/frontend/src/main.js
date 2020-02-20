import '@babel/polyfill'
import Vue from 'vue'
import app from './app.vue'
import VueProgressBar from 'vue-progressbar'
import router from './router'

import PouchVue from 'pouch-vue'
import PouchDB from 'pouchdb-browser'
PouchDB.plugin(require('pouchdb-find'))
PouchDB.plugin(require('pouchdb-live-find'))
// PouchDB.plugin(require('pouchdb-authentication'));
// TODO: when we add auth

Vue.prototype.$db_url = 'https://sd-db.glitch.me'

// https://github.com/MDSLKTR/pouch-vue
Vue.use(PouchVue, {
  pouch: PouchDB, // optional if `PouchDB` is available on the global object
  defaultDB: Vue.prototype.$db_url + '/_all_dbs', // this is used as a default connect/disconnect database
  optionsDB: {
    // this is used to include a custom fetch() method (see TypeScript example)
    fetch: function (url, opts) {
      opts.credentials = 'omit'
      // omit: Never send or receive cookies.
      // same-origin: Send user credentials (cookies, basic http auth, etc..) if the URL is on the same origin as the calling script. This is the default value.
      // include: Always send user credentials (cookies, basic http auth, etc..), even for cross-origin calls.
      return PouchDB.fetch(url, opts)
    }
  }
  // debug: "*" // optional - See `https://pouchdb.com/api.html#debug_mode` for valid settings (will be a separate Plugin in PouchDB 7.0)
})

Vue.use(VueProgressBar, {
  color: 'rgb(143, 255, 199)',
  failedColor: 'red',
  thickness: '5px'
})

window.v = new Vue({
  el: '#app',
  router,
  render: h => h(app)
})
