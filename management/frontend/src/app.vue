<template>
  <div class="mw8 center pv4 ph3 mt-3" id="dashboard">
    <div class="flex-m flex-l nl3-m nr3-m nl3-l nr3-l">
      <component-nav></component-nav>
      <router-view></router-view>
    </div>
    <vue-progress-bar></vue-progress-bar>
  </div>
</template>

<script>
import componentNav from './components/nav'
import Chart from 'chart.js'

export default {
  name: 'App',
  components: {
    componentNav
  },
  mounted () {
    //  [App.vue specific] When App.vue is finish loading finish the progress bar
    this.$Progress.finish()
  },
  created () {
    Chart.defaults.global.legend.display = false
    //  [App.vue specific] When App.vue is first loaded start the progress bar
    this.$Progress.start()
    //  hook the progress bar to start before we move router-view
    this.$router.beforeEach((to, from, next) => {
      //  start the progress bar
      this.$Progress.start()
      //  continue to next page
      next()
    })
    //  hook the progress bar to finish after we've finished moving router-view
    this.$router.afterEach((to, from) => {
      //  finish the progress bar
      this.$Progress.finish()
    })
  }
}
</script>
