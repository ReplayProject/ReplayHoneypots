<template>
  <div class="mw8 center pv4 ph3 mt-3" id="dashboard">
    <div class="flex-m flex-l nl3-m nr3-m nl3-l nr3-l">
      <component-nav></component-nav>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import componentNav from './components/nav'
import Chart from 'chart.js'

export default {
  components: {
    componentNav
  },
  created () {
    Chart.defaults.global.legend.display = false
  },
  mounted () {}
}
</script>
