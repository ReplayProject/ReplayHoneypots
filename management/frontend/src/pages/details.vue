<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>{{ $route.params.device | formatDBName }}</component-title>
    <hr class="o-20" />
    <div class="mt4">
      <div class="w-100 mb3 mb0-l">
        <div class="bt bl br b--black-10 br2">
          <div class="pa3 bb b--black-10">
            <h4 class="mv0">First {{ logs.length }} Logs</h4>
          </div>
          <metric-list-item
            v-for="(log, index) in logs"
            :key="index"
            :show-bar="false"
            :name="log.doc.sourceIPAddress + ':' + log.doc.sourcePortNumber"
            :value="
              log.doc.destIPAddress +
                ':' +
                log.doc.destPortNumber +
                '  -  ' +
                log.doc.timestamp
            "
          >
          </metric-list-item>
        </div>
        <a
          href="#"
          class="no-underline fw5 mt3 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
          >Load More</a
        >
      </div>
    </div>
  </main>
</template>

<script>
import componentTitle from '../components/title'
import metricListItem from '../components/metric-list-item'

export default {
  name: 'deviceDetails',
  components: {
    componentTitle,
    metricListItem
  },
  data () {
    return {
      logs: [],
      error: null,
      lastKey: ''
    }
  },
  async beforeRouteEnter (to, from, next) {
    next(async vm => {
      let url = process.env.DB_URL + '/' + vm.$route.params.device
      let res = await vm.$pouch.allDocs(
        { include_docs: true, conflicts: true, limit: 10 },
        url
      )
      vm.setData(undefined, res.rows)
    })
  },
  // // when route changes and this component is already rendered,
  // // the logic will be slightly different.
  async beforeRouteUpdate (to, from, next) {
    let url = process.env.DB_URL + '/' + this.$route.params.device
    let res = await this.$pouch.allDocs(
      { include_docs: true, conflicts: true, limit: 10 },
      url
    )
    this.setData(undefined, res.rows)
    next()
  },
  methods: {
    setData (err, logs) {
      if (err) {
        this.error = err.toString()
      } else {
        this.logs = logs
      }
    }
  }
}
</script>
