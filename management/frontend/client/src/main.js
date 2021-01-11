import '@babel/polyfill'
import Vue from 'vue'
import app from './app.vue'
import store from './store.js'
import VueProgressBar from 'vue-progressbar'
import router from './router'
import Toasted from 'vue-toasted'

/**
 * Library for styling and all look & feel
 * https://tachyons.io/
 */
import 'tachyons/css/tachyons.min.css'

/**
 * Library for our datatables
 * https://xaksis.github.io/vue-good-table/
 */
import VueGoodTablePlugin from 'vue-good-table'
import 'vue-good-table/dist/vue-good-table.css'
Vue.use(VueGoodTablePlugin)

/**
 * Library for popups and alerts
 * https://shakee93.github.io/vue-toasted/
 */
Vue.use(Toasted, {
    theme: 'toasted-primary',
    position: 'bottom-center',
    duration: 5000,
})

/**
 * Library for general use HTTP request
 */
import axios from 'axios'
import VueAxios from 'vue-axios'
Vue.use(VueAxios, axios)

/**
 * The top progress bar
 * (lovingly named Kevin)
 */
Vue.use(VueProgressBar, {
    color: 'rgb(143, 255, 199)',
    failedColor: 'red',
    thickness: '8px',
})

/**
 * Library for datetime pickers
 */
import { Datetime } from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'
Vue.use(Datetime)
Vue.component('datetime', Datetime)

/**
 * Filter to make the DB name look prettier
 */
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

/**
 * Section for helper functions, and global variables we need all over the application
 */

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
// How to pick colors for hosts on the sparklines and piechart
Vue.prototype.$pickColor = (s, extras) => {
    // Ensure hostname is string (avoids split error)
    s = String(s)
    let colors = [
        'bg-green',
        'bg-red',
        'bg-purple',
        'bg-blue',
        'bg-orange',
        'bg-navy',
        'bg-teal',
        'bg-olive',
        'bg-yellow',
        'bg-maroon'
    ]
    if (extras) {
        colors.push('bg-gray')
        colors.push('bg-silver')
    }
    let idx = s.split('').reduce((a, x) => a + x.charCodeAt(0), 0) + s.length
    return colors[idx % colors.length]
}

/**
 * Create the Vue instance and bind to global variable
 */
window.v = new Vue({
    el: '#app',
    router,
    store,
    render: h => h(app),
})
