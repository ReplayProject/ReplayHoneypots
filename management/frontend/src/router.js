import Vue from 'vue'
import Router from 'vue-router'

import PageIndex from './pages/index.vue'
import PageAbout from './pages/about.vue'
import PageEdit from './pages/edit.vue'
import PageOverview from './pages/overview.vue'

Vue.use(Router)

let routes =  [
    {
      path: '/',
      name: 'index',
      component: PageIndex
    },
    {
      path: '/about',
      name: 'about',
      component: PageAbout
    },
    {
      path: '/edit',
      name: 'edit',
      component: PageEdit
    },
    {
      path: '/overview',
      name: 'overview',
      component: PageOverview
    },
    {
      path: '*',
      redirect: '/'
    }
  ]

const router = new Router({
  mode: "history",
  base: "/",
  routes
});

export default router
