// Set up JSDom.
require('jsdom-global')()

// Fix the Date object, see <https://github.com/vuejs/vue-test-utils/issues/936#issuecomment-415386167>.
window.Date = Date

// Setup browser environment
const hooks = require('require-extension-hooks')
const Vue = require('vue')

// Setup Vue.js to remove production tip
Vue.config.productionTip = false

// Give prototype mods used in, fillers

Vue.filter('capitalize', function (value) {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
})

Vue.prototype.$pickColor = (s, extras) => {
    let colors = ['bg-green', 'bg-red', 'bg-purple', 'bg-blue', 'bg-orange']
    if (extras) {
        colors.push('bg-gray')
        colors.push('bg-silver')
    }
    let idx = s.split('').reduce((a, x) => a + x.charCodeAt(0), 0) + s.length
    return colors[idx % colors.length]
}

let Datetime = require('vue-datetime')
// import 'vue-datetime/dist/vue-datetime.css'
Vue.use(Datetime)
Vue.component('datetime', Datetime)

// Setup vue files to be processed by `require-extension-hooks-vue`
hooks('vue').plugin('vue').push()
// Setup vue and js files to be processed by `require-extension-hooks-babel`
hooks(['vue', 'js'])
    .exclude(({ filename }) => filename.match(/\/node_modules\//))
    .plugin('babel')
    .push()
