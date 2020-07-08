import Vue from 'vue'
import Router from 'vue-router'

import PageIndex from './pages/index.vue'
import PageAbout from './pages/about.vue'
import PageAlerts from './pages/alerts.vue'
import PageEdit from './pages/edit.vue'
import PageOverview from './pages/overview.vue'
import PageDetails from './pages/details.vue'
import PageLogin from './pages/login.vue'

import axios from 'axios'
/**
 * Setup how we server, authenticate, and structure our application
 */
Vue.use(Router)

let routes = [
    {
        path: '/',
        name: 'index',
        component: PageIndex,
    },
    {
        path: '/login',
        name: 'login',
        component: PageLogin,
    },
    {
        path: '/about',
        name: 'about',
        component: PageAbout,
    },
    {
        path: '/details/:device',
        name: 'details',
        component: PageDetails,
    },
    {
        path: '/alerts',
        name: 'alerts',
        component: PageAlerts,
    },
    {
        path: '/overview',
        name: 'overview',
        component: PageOverview,
    },
    {
        path: '/edit',
        name: 'edit',
        component: PageEdit,
    },
    {
        path: '*',
        redirect: '/',
    },
]

const router = new Router({
    mode: 'history',
    base: '/',
    routes,
})

/**
 * Perform an authentication check on all routes except 'login'
 */
router.beforeEach(async (to, from, next) => {
    let shouldBeAuthed = to.name !== 'login'

    if (shouldBeAuthed) {
        try {
            let res = await axios.get('/user')
            // TODO: maybe save this in app internals,
            //  if we need user data from Passport JS
            // console.log(res.data)
            next()
        } catch (err) {
            v.$toasted.show('Please log in.')
            next({ name: 'login' })
            return
        }
    }
    next()
})

export default router
