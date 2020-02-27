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
      <div class="overflow-auto">
        <table class="f6 w-100 mw8 center" cellspacing="0">
          <thead>
            <tr class="stripe-dark">
              <th class="fw6 tl pa3 bg-pink">timestamp</th>
              <th class="fw6 tl pa3 bg-pink">traffictype</th>
              <th class="fw6 tl pa3 bg-pink">sourcePort</th>
              <th class="fw6 tl pa3 bg-pink">sourceIP</th>
              <th class="fw6 tl pa3 bg-pink">destPort</th>
              <th class="fw6 tl pa3 bg-pink">destIP</th>
            </tr>
          </thead>
          <tbody class="lh-copy">
            <tr v-for="entry in logs" :key="entry.id" class="stripe-dark">
              <td class="pa3">{{ $parseDateWithTime(entry.timestamp) }}</td>
              <td class="pa3">{{ entry.trafficType }}</td>
              <td class="pa3">{{ entry.sourcePortNumber }}</td>
              <td class="pa3">{{ entry.sourceIPAddress }}</td>
              <td class="pa3">{{ entry.destPortNumber }}</td>
              <td class="pa3">{{ entry.destIPAddress }}</td>
            </tr>
          </tbody>
        </table>
        <button
          @click="loadMore"
          class="no-underline fw5 mt3 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
        >
          Load More
        </button>
      </div>
    </div>
  </main>
</template>

<script>
import componentTitle from '../components/title'
import logEntry from '../components/log-entry'

export default {
  name: 'deviceDetails',
  components: {
    componentTitle,
    logEntry
  },
  data () {
    return {
      logs: [],
      error: null,
      lastKey: '',
      limit: 25
    }
  },
  //TODO: THIS IS FOR PRE_Navigation data loading (not required)
  beforeRouteEnter (to, from, next) {

    // debugger
    next()

    // next(vm => {
    //   vm.setData(undefined, results.docs)
    // })

    // next(async vm => {
    //   let url = process.env.DB_URL + '/' + vm.$route.params.device
    //   let res = await vm.$pouch.allDocs(
    //     { include_docs: true, conflicts: true, limit: vm.limit },
    //     url
    //   )
    //   vm.setData(undefined, res.rows)
    // })
  },
  // // // when route changes and this component is already rendered,
  // // // the logic will be slightly different.
  async beforeRouteUpdate (to, from, next) {
    // let url = process.env.DB_URL + '/' + this.$route.params.device
    // let res = await this.logs.$pouch.allDocs(
    //   { include_docs: true, conflicts: true, limit: this.limit },
    //   url
    // )
    // this.setData(undefined, res.rows)
    this.logs = []
    this.loadMore()
    next()
  },
  created () {
    this.loadMore()
  },
  methods: {
    async loadMore () {
      this.$Progress.start()
      let idx = await this.$pouch.createIndex(
        {
          index: {
            fields: ['timestamp']
          }
        },
        process.env.DB_URL + '/' + this.$route.params.device
      )

      // Only log index creation if it was new
      if (idx.result != 'exists') console.log(idx)

      // Actually do a query
      let results = await this.$pouch.find(
        {
          selector: { timestamp: { $exists: true } },
          sort: [{ timestamp: 'desc' }],
          limit: this.limit,
          skip: this.logs.length
        },
        process.env.DB_URL + '/' + this.$route.params.device
      )

      this.logs.push.apply(this.logs, results.docs)

      this.$Progress.finish()
    },
    setData (err, results) {
      if (err) {
        this.error = err.toString()
      } else {
        this.logs.push.apply(this.logs, results.docs)
      }
    }
  }
}
</script>
