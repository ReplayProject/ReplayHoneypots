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
        <table class="f6 w-100 mw8 center mb3" cellspacing="0">
          <thead>
            <tr class="stripe-dark tc">
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('timestamp')"
              >
                timestamp
              </th>
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('trafficType')"
              >
                traffictype
              </th>
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('sourcePortNumber')"
              >
                sourcePort
              </th>
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('sourceIPAddress')"
              >
                sourceIP
              </th>
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('destPortNumber')"
              >
                destPort
              </th>
              <th
                class="fw6 tl pa3 tc bg-pink dim pointer"
                @click="sort('destIPAddress')"
              >
                destIP
              </th>
            </tr>
          </thead>
          <tbody class="lh-copy">
            <tr v-for="entry in sortedLogs" :key="entry.id" class="stripe-dark">
              <td class="pa3 tc">{{ $parseDateWithTime(entry.timestamp) }}</td>
              <td class="pa3 tc">{{ entry.trafficType }}</td>
              <td class="pa3 tc">{{ entry.sourcePortNumber }}</td>
              <td class="pa3 tc">{{ entry.sourceIPAddress }}</td>
              <td class="pa3 tc">{{ entry.destPortNumber }}</td>
              <td class="pa3 tc">{{ entry.destIPAddress }}</td>
            </tr>
          </tbody>
        </table>
        <div class="cf tc">
          <button
            @click="prevPage"
            class="no-underline fw5 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white fl"
          >
            Previous Page
          </button>
          <span class="f3">{{ currentPage }}</span>
          <button
            @click="nextPage"
            class="no-underline fw5 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white fr"
          >
            Next Page
          </button>
        </div>
        <br />
        <button
          @click="loadMore"
          class="no-underline fw5 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
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
      limit: 25,
      pageSize: 5,
      currentPage: 1,
      // Used for sorting on the frontend
      currentSort: 'name',
      currentSortDir: 'asc'
    }
  },
  computed: {
    sortedLogs () {
      return this.logs
        .sort((a, b) => {
          let modifier = 1
          if (this.currentSortDir === 'desc') modifier = -1
          if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier
          if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier
          return 0
        })
        .filter((row, index) => {
          let start = (this.currentPage - 1) * this.pageSize
          let end = this.currentPage * this.pageSize
          if (index >= start && index < end) return true
        })
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
    sort (s) {
      //if s == current sort, reverse
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc'
      }
      this.currentSort = s
    },
    nextPage () {
      if (this.currentPage * this.pageSize < this.logs.length)
        this.currentPage++
    },
    prevPage () {
      if (this.currentPage > 1) this.currentPage--
    },
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
