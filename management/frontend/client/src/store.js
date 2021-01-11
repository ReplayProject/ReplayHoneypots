import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

/**
 * Setup the store
 * This will be used for any data that should be:
 * persistant between reloads,
 * chared between components,
 * tracked when changed
 */
let store = new Vuex.Store({
    plugins: [
        createPersistedState({
            storage: window.sessionStorage,
        }),
    ],
    state: {
        hostsInfo: [], // info on the different honeypots we are loading up
        logsInfo: {}, // aggregate info about the hosts
        alertsInfo: [], // storage for alerts coming from CouchDB
        configsInfo: [], // storage for configs coming from CouchDB
        authStatus: {},
    },
    mutations: {
        setHostsInfo(state, hostsInfo) {
            state.hostsInfo = hostsInfo
        },
        setLogInfo(state, logsInfo) {
            state.logsInfo = logsInfo
        },
        setAlerts(state, alertsInfo) {
            state.alertsInfo = alertsInfo
        },
        setConfigs(state, configsInfo) {
            state.configsInfo = configsInfo
        },
        unshiftAlerts(state, doc) {
            state.alertsInfo.unshift(doc)
        },
        popAlerts(state) {
            state.alertsInfo.pop()
        },
        sortAlertsDesc(state) {
            state.alertsInfo.sort((a, b) => b.timestamp - a.timestamp)
        },
        setUserData(state, userData) {
            state.userData = userData
        },
        setPermsData(state, permsData) {
            state.permsData = permsData
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
