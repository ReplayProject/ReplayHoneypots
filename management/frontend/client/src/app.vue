<template>
  <div class="mw8 center pv4 ph3 mt-3" id="dashboard">
    <div class="flex-m flex-l nl3-m nr3-m nl3-l nr3-l">
      <component-nav></component-nav>
      <!-- Waits to load views till we have hosts info -->
      <router-view v-if="Object.keys(hostsInfo).length != 0"></router-view>
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
  data () {
    return {
      aggInfo: {},
      hostsInfo: []
    }
  },
  async mounted () {
    console.log('Setting up DB')
    let db_url = process.env.DB_URL + '/' + 'aggregate_logs'

    let info = await this.$pouch.info(db_url)
    this.aggInfo = info

    // create a design doc
    var ddoc = {
      _id: '_design/hostname',
      views: {
        hostname: {
          map: function (doc) {
            emit(doc.hostname, 1)
          }.toString(),
          reduce: '_sum'
        }
      }
    }

    // save the design doc
    try {
      await this.$databases[db_url].put(ddoc)
    } catch (err) {
      if (err.name !== 'conflict')
        console.log('Design Document already exists: ', err.messge)
    }
    try {
      let result = await this.$databases[db_url].query('hostname', {
        include_docs: false,
        reduce: true,
        group: true
      })

      this.hostsInfo = result.rows
    } catch (err) {
      console.log('Something went wrong with fetching DB info: ', err)
    }

    //  [App.vue specific] When App.vue is finish loading finish the progress bar
    this.$Progress.finish()
  },
  computed: {
    totalLogs () {
      return this.hostsInfo.reduce((a, x) => (a += x.value), 0)
    }
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
