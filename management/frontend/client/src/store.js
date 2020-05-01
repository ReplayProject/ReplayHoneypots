import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

// Setup PouchDB Client

import PouchVue from 'pouch-vue'
import PouchDB from 'pouchdb-browser'
import PouchdbFind from 'pouchdb-find'
PouchDB.plugin(PouchdbFind)
PouchDB.plugin(require('pouchdb-live-find'))
// PouchDB.plugin(require('pouchdb-authentication'));
// TODO: when we add database auth
// https://github.com/MDSLKTR/pouch-vue
Vue.use(PouchVue, {
  pouch: PouchDB, // optional if `PouchDB` is available on the global object
  defaultDB: process.env.DB_URL + '/_all_dbs', // this is used as a default connect/disconnect database
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

// Setup the store

let store = new Vuex.Store({
  state: {
    hostsInfo: [],
    aggInfo: {},
    alerts: [],
    count: 0
  },
  mutations: {
    setHostsInfo (state, hostsInfo) {
      state.hostsInfo = hostsInfo
    },
    setAggInfo (state, aggInfo) {
      state.aggInfo = aggInfo
    },
    setAlerts (state, alerts) {
      state.alerts = alerts
    },
    increment (state) {
      state.count++
    },
    unshiftList (state, doc) {
      state.alerts.unshift(doc)
    },
    popAlerts (state) {
      state.alerts.pop()
    }
  },
  actions: {
    loadAlerts ({ commit }) {
      console.log(Vue)
      console.log(vue)
    }
  },
  getters: {
    totalLogs: state => {
      return state.hostsInfo.reduce((a, x) => (a += x.value), 0)
    }
  }
})

export default store
