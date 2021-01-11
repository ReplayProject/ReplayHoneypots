import Vue from 'vue'
import Router from 'vue-router'

import PageIndex from './pages/index.vue'
import PageAbout from './pages/about.vue'
import PageAlerts from './pages/alerts.vue'
import PageEdit from './pages/edit.vue'
import PageOverview from './pages/overview.vue'
import PageLogin from './pages/login.vue'
import PageMetrics from './pages/metrics.vue'
import PageUsers from './pages/users.vue'
import PageAddUser from './pages/userAdd.vue'
import PageUserDetails from './pages/userDetails.vue'
import PageConfigs from './pages/configs.vue'
import PageAddConfig from './pages/configAdd.vue'
import PageConfigDetails from './pages/configDetails.vue'
import PageHoneypots from './pages/honeypots.vue'
import PageHoneypotDetails from './pages/honeypotDetails.vue'
import PageAuthGroups from './pages/authGroups.vue'
import PageAuthGroupsAdd from './pages/authGroupsAdd.vue'
import PageRoles from './pages/roles.vue'
import PageAddRole from './pages/roleAdd.vue'
import PageEditRole from './pages/roleDetails.vue'
import PagePasswordExpired from './pages/passwordExp.vue'
import PageAdminLogs from './pages/adminLogs.vue'

import api from './api.js'

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
        path: '/honeypots',
        name: 'honeypots',
        component: PageHoneypots,
    },
    {
        path: '/honeypots/:device',
        name: 'honeypotDetails',
        component: PageHoneypotDetails,
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
        path: '/metrics',
        name: 'metrics',
        component: PageMetrics,
    },
    {
        path: '/users',
        name: 'users',
        component: PageUsers,
    },
    {
        path: '/users/new',
        name: 'userAdd',
        component: PageAddUser,
    },
    {
        path: '/users/:user',
        name: 'userDetails',
        component: PageUserDetails,
    },
    {
        path: '/configs',
        name: 'configs',
        component: PageConfigs,
    },
    {
        path: '/configs/new',
        name: 'configAdd',
        component: PageAddConfig,
    },
    {
        path: '/configs/:config',
        name: 'configDetails',
        component: PageConfigDetails,
    },
    {
        path: '/authGroups',
        name: 'authGroups',
        component: PageAuthGroups,
    },
    {
        path: '/authGroups/new',
        name: 'authGroupsAdd',
        component: PageAuthGroupsAdd,
    },
    {
        path: '/roles',
        name: 'roles',
        component: PageRoles,
    },
    {
        path: '/roles/new',
        name: 'rolesAdd',
        component: PageAddRole,
    },
    {
        path: '/roles/:role',
        name: 'editRole',
        component: PageEditRole,
    },
    {
        path: '/passwordexpired',
        name: 'passwordExpired',
        component: PagePasswordExpired
    },
    {
        path: '/adminLogs',
        name: 'adminLogs',
        component: PageAdminLogs
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
    if (to.name !== 'login') {
        try {
            let response = await api.getSessionData()
            v.$store.commit('setUserData', response.data[0])
            v.$store.commit('setPermsData', response.data[1])
            if (v.$store.state.userData.otp === true && to.name !== 'passwordExpired') {
                v.$toasted.show('Password Expired. Reset your password.')
                next({ name: 'passwordExpired' })
            } else {
                next()
            }
        } catch (err) {
            v.$toasted.show('Please log in.')
            v.$store.commit('setUserData', undefined)
            v.$store.commit('setPermsData', undefined)
            next({ name: 'login' })
            return
        }
    }
    next()
})

export default router
