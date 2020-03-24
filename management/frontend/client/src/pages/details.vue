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

    <div class="mt4 w-100">
      <vue-good-table
        ref="datatable"
        mode="remote"
        @on-page-change="onPageChange"
        @on-sort-change="onSortChange"
        @on-column-filter="onColumnFilter"
        @on-per-page-change="onPerPageChange"
        @on-search="onSearch"
        :isLoading.sync="isLoading"
        :columns="columns"
        :totalRows="totalRecords"
        :rows="rows"
        :fixed-header="true"
        :line-numbers="false"
        theme="default"
        :pagination-options="{
          enabled: true
        }"
        :search-options="{
          enabled: true,
          trigger: 'enter',
          skipDiacritics: true,
          placeholder: 'Search this table'
        }"
      >
        <div slot="emptystate">
          No Logs have been loaded or recorded yet.
        </div>
      </vue-good-table>
    </div>
  </main>
</template>

<script>
import componentTitle from '../components/title'

export default {
  name: 'deviceDetails',
  components: {
    componentTitle
  },
  data () {
    return {
      dbInfo: {},
      isLoading: false,
      totalRecords: 0,
      serverParams: {
        search: '',
        // a map of column filters example: {name: 'john', age: '20'}
        columnFilters: {},
        sort: [
          {
            field: 'timestamp', // example: 'name'
            type: 'desc' // 'asc' or 'desc'
          }
        ],
        page: 1, // what page I want to show
        perPage: 10 // how many items I'm showing per page
      },
      columns: [
        {
          label: 'Unique ID',
          field: '_id',
          type: 'text'
        },
        {
          label: 'time',
          field: 'timestamp',
          formatFn: x => {
            let s = new Date(x * 1000)
              .toLocaleString()
              .replace('/' + new Date().getFullYear(), '')
            return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
          },
          type: 'text'
        },
        {
          label: 'proto',
          field: 'trafficType',
          type: 'text'
        },
        {
          label: 'sPort',
          field: 'sourcePortNumber',
          type: 'text'
        },
        {
          label: 'sIP',
          field: 'sourceIPAddress',
          type: 'text'
        },
        {
          label: 'dPort',
          field: 'destPortNumber',
          type: 'text'
        },
        {
          label: 'dIP',
          field: 'destIPAddress',
          type: 'text'
        }
      ],
      rows: []
    }
  },
  computed: {
    dbURI () {
      return (
        (this.$route.params.device == 'aggregate'
          ? ''
          : process.env.DB_URL + '/') + this.$route.params.device
      )
    }
  },
  async created () {
    this.loadItems()
    this.dbInfo = await this.$databases[this.dbURI].info()
  },
  watch: {
    '$route.params.device': async function (device) {
      this.loadItems()
      this.dbInfo = await this.$databases[this.dbURI].info()
      this.resetParams()
    },
    currentPage () {
      this.loadItems()
    }
  },
  methods: {
    // Format Datetime
    formatDate (x) {
      return $this.parseDateWithTime(x)
    },
    // DOCS: https://xaksis.github.io/vue-good-table/guide/advanced/remote-workflow.html#provide-handlers-for-user-events
    // Handlers for DB TABLE
    updateParams (newProps) {
      this.serverParams = Object.assign({}, this.serverParams, newProps)
    },
    resetParams () {
      this.updateParams({
        search: '',
        // a map of column filters example: {name: 'john', age: '20'}
        columnFilters: {},
        sort: [
          {
            field: 'timestamp', // example: 'name'
            type: 'desc' // 'asc' or 'desc'
          }
        ],

        page: 1, // what page I want to show
        perPage: 10 // how many items I'm showing per page
      })
      // Clear search
      this.$refs['datatable'].globalSearchTerm = ''
    },
    onPageChange (params) {
      this.updateParams({ page: params.currentPage })
      this.loadItems()
    },
    onPerPageChange (params) {
      this.updateParams({ perPage: params.currentPerPage })
      this.loadItems()
    },
    onSortChange (params) {
      this.updateParams({
        sort: params
      })
      this.loadItems()
    },
    onColumnFilter (params) {
      this.updateParams(params)
      this.loadItems()
    },
    onSearch (params) {
      this.updateParams({ search: params.searchTerm, page: 1 })
      this.loadItems()
    },
    // load items is what brings back the rows from server
    async loadItems () {
      this.$Progress.start()
      this.isLoading = true

      let fields = [
        ...Object.keys(this.serverParams.columnFilters),
        ...this.serverParams.sort.map(x => x.field)
      ]
      fields.sort()

      if (fields.length != 0) {
        let idx = await this.$pouch.createIndex(
          {
            index: { fields }
          },
          this.dbURI
        )
        // Only log index creation if it was new
        if (idx.result != 'exists') console.log('New Index created: ', idx)
      }

      let selector = {}

      // Column filters not working
      // Object.keys(this.serverParams.columnFilters).forEach(x => {
      //   selector[x] = { $eq: this.serverParams.columnFilters[x] }
      // })

      let sort = this.serverParams.sort.map(x => {
        let s = {}
        s[x.field] = x.type
        return s
      })

      // See if we are searching or filtering & setup params
      let searchTerm = this.serverParams.search.trim()
      let skip = (this.serverParams.page - 1) * this.serverParams.perPage
      let limit = this.serverParams.perPage

      // Actually do a query
      let results =
        searchTerm === ''
          ? await this.$pouch.find(
              {
                selector,
                sort,
                skip,
                limit,
                execution_stats: true
              },
              this.dbURI
            )
          : await this.$pouch.query(
              {
                map: new Function(
                  'doc',
                  `
                  let s = JSON.stringify(doc)
                    .toLocaleLowerCase()
                    .includes('${searchTerm}'.toLocaleLowerCase())
                  if (s) {
                    emit(doc._id, doc)
                  }
                `
                )
              },
              {
                skip,
                limit
              },
              this.dbURI
            )
      // TODO: Get total count of matching documents when not "searching"

      // Access responses from data
      this.rows =
        searchTerm === ''
          ? results.docs
          : results.total_rows != 0
          ? results.rows.map(x => x.value)
          : []
      this.totalRecords =
        searchTerm === '' ? this.dbInfo.doc_count : results.total_rows

      // Mark everything as done loading
      this.$Progress.finish()
      this.isLoading = false
    }
  }
}
</script>
