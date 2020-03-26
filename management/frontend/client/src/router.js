import Vue from 'vue'
import Router from 'vue-router'

import PageIndex from './pages/index.vue'
import PageAbout from './pages/about.vue'
import PageEdit from './pages/edit.vue'
import PageOverview from './pages/overview.vue'
import PageDetails from './pages/details.vue'
import PageTerminal from './pages/terminal.vue'
import PageLogin from './pages/login.vue'

import axios from 'axios'

Vue.use(Router)

let routes = [
  {
    path: '/',
    name: 'index',
    component: PageIndex
  },
  {
    path: '/login',
    name: 'login',
    component: PageLogin
  },
  {
    path: '/about',
    name: 'about',
    component: PageAbout
  },
  {
    path: '/details/:device',
    name: 'details',
    component: PageDetails
  },
  {
    path: '/terminal',
    name: 'terminal',
    component: PageTerminal
  },
  {
    path: '/overview',
    name: 'overview',
    component: PageOverview
  },
  {
    path: '/edit',
    name: 'edit',
    component: PageEdit
  },
  {
    path: '*',
    redirect: '/'
  }
]

const router = new Router({
  mode: 'history',
  base: '/',
  routes
})

/**
 * Perform an authentication check on all routes except 'login'
 */
router.beforeEach(async (to, from, next) => {
  let shouldBeAuthed = to.name !== 'login'

  if (shouldBeAuthed) {
    try {
      let res = await axios.get('/user')
      // console.log(res.data) // TODO: maybe save this in app internals
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
