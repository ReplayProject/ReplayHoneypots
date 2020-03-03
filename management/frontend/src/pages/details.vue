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
    <article v-if="dbInfo.host" data-name="slab-stat">
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Adapter</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.adapter }}</dd>
      </dl>
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Disk Size</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.disk_size / 1000000 }} mb</dd>
      </dl>
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Total Logs</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.doc_count }}</dd>
      </dl>
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Location</dd>
        <dd class="f4 f3-ns b ml0">{{ dbInfo.host }}</dd>
      </dl>
    </article>
    <article v-if="dbInfo.db_name == 'aggregate'">
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Adapter</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.adapter }}</dd>
      </dl>
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Total Logs</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.doc_count }}</dd>
      </dl>
      <dl class="dib mr5">
        <dd class="f6 f5-ns b ml0">Document Updates</dd>
        <dd class="f3 f2-ns b ml0">{{ dbInfo.update_seq }}</dd>
      </dl>
    </article>
    <hr class="o-20" />
    <div class="mt4">
      <div class="overflow-auto">
        <table class="f6 w-100 mw8 center mb3" cellspacing="0">
          <thead>
            <tr class="stripe-dark tc">
              <th class="fw6 tl pa3 tc bg-pink dim pointer">
                index
              </th>

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
            <tr
              v-for="(entry, idx) in sortedLogs"
              :key="entry.id"
              class="stripe-dark"
            >
              <!-- TODO: make this index be bound to the entry or some other unique identifier -->
              <td class="pa3 tc">{{ idx }}</td>
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
        <p class="w-100 f4 tc">Showing logs {{ lower }} - {{ upper }}</p>
        <br />
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
      dbInfo: {},
      logs: [],
      error: null,
      // Used for sorting on the frontend
      limit: 10,
      currentPage: 1,
      currentSort: 'name',
      currentSortDir: 'asc',
      startKey: ''
    }
  },
  computed: {
    upper () {
      return (this.currentPage - 1) * this.limit + this.limit - 1
    },
    lower () {
      return (this.currentPage - 1) * this.limit
    },
    dbURI () {
      return (
        (this.$route.params.device == 'aggregate'
          ? ''
          : process.env.DB_URL + '/') + this.$route.params.device
      )
    },
    sortedLogs () {
      return this.logs.sort((a, b) => {
        let modifier = 1
        if (this.currentSortDir === 'desc') modifier = -1
        if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier
        if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier
        return 0
      })
    }
  },
  async created () {
    this.init()
  },
  watch: {
    '$route.params.device': function (device) {
      this.init()
    },
    currentPage () {
      this.loadDocs()
    }
  },
  methods: {
    async init () {
      this.dbInfo = {}
      this.logs = []
      this.error = null
      this.startKey = ''
      this.loadDocs()
      this.dbInfo = await this.$databases[this.dbURI].info()
      console.log(await this.$databases[this.dbURI].info())
    },
    sort (s) {
      //if s == current sort, reverse
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc'
      }
      this.currentSort = s
    },
    async nextPage () {
      this.currentPage++
    },
    async prevPage () {
      if (this.currentPage > 1) this.currentPage--
    },
    async loadDocs () {
      this.$Progress.start()
      let idx = await this.$pouch.createIndex(
        {
          index: {
            fields: ['timestamp']
          }
        },
        this.dbURI
      )

      // Only log index creation if it was new
      if (idx.result != 'exists') console.log('New Index created: ', idx)

      // Actually do a query
      let results = await this.$pouch.find(
        {
          selector: { timestamp: { $exists: true } },
          sort: [{ timestamp: 'desc' }],
          skip: this.lower,
          limit: this.limit
        },
        this.dbURI
      )
      this.logs = results.docs
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
