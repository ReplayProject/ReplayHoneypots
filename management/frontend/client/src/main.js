import '@babel/polyfill'
import Vue from 'vue'
import app from './app.vue'
import store from './store.js'
import VueProgressBar from 'vue-progressbar'
import router from './router'
import Toasted from 'vue-toasted'

import 'tachyons/css/tachyons.min.css'
import VueGoodTablePlugin from 'vue-good-table'
import 'vue-good-table/dist/vue-good-table.css'
Vue.use(VueGoodTablePlugin)

Vue.use(Toasted, {
    theme: 'toasted-primary',
    position: 'bottom-center',
    duration: 5000,
})

import axios from 'axios'
import VueAxios from 'vue-axios'
Vue.use(VueAxios, axios)

Vue.use(VueProgressBar, {
    color: 'rgb(143, 255, 199)',
    failedColor: 'red',
    thickness: '8px',
})

Vue.filter('formatDBName', value => {
    if (!value) return ''
    value = value.toString()
    return (
        value
            .split('_')
            .map(x => x.replace(/^\w/, c => c.toUpperCase()))
            .join(' ') + ' Logs'
    )
})

Vue.filter('capitalize', function (value) {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
})

// Setup for how dates work on the app
let dateType = x =>
    new Date(x * 1000).toLocaleString().replace('/' + new Date().getFullYear(), '')
// Get date value
Vue.prototype.$date = () => Date.now()
// Parse regular date to string
Vue.prototype.$parseDate = x => {
    let s = dateType(x)
    return s.slice(0, s.indexOf(':', 9)) + ' ' + s.split(' ')[2]
}
// Parse regular date to string with time too
Vue.prototype.$parseDateWithTime = x => {
    let s = dateType(x)
    return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
}

Vue.prototype.dbURI = process.env.DB_URL + '/' + 'aggregate_logs'
Vue.prototype.alertsURI = process.env.DB_URL + '/' + 'alerts'

window.v = new Vue({
    el: '#app',
    router,
    store,
    render: h => h(app),
})
