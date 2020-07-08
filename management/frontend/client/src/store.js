import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

// Setup PouchDB Client for talking with the CouchDB database

import PouchVue from 'pouch-vue'
import PouchDB from 'pouchdb-browser'
import PouchdbFind from 'pouchdb-find'
PouchDB.plugin(PouchdbFind)
PouchDB.plugin(require('pouchdb-live-find'))
// PouchDB.plugin(require('pouchdb-authentication'));
// TODO: when we add database authentication and RBAC
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
        },
    },
    // debug: "*" // optional - See `https://pouchdb.com/api.html#debug_mode` for valid settings (will be a separate Plugin in PouchDB 7.0)
})

/**
 * Setup the store
 * This will be used for any data that should be:
 * persistant between reloads,
 * chared between components,
 * tracked when changed
 */
let store = new Vuex.Store({
    state: {
        hostsInfo: [], // info on the different honeypots we are loading up
        aggInfo: {}, // aggregate info about the hosts
        alerts: [], // storage for alerts coming from CouchDB
    },
    mutations: {
        setHostsInfo(state, hostsInfo) {
            state.hostsInfo = hostsInfo
        },
        setAggInfo(state, aggInfo) {
            state.aggInfo = aggInfo
        },
        setAlerts(state, alerts) {
            state.alerts = alerts
        },
        unshiftList(state, doc) {
            state.alerts.unshift(doc)
        },
        popAlerts(state) {
            state.alerts.pop()
        },
    },
    actions: {},
    getters: {
        /**
         * Compute and return the total number of logs from out hosts
         */
        totalLogs: state => {
            return state.hostsInfo.reduce((a, x) => (a += x.value), 0)
        },
    },
})

export default store
