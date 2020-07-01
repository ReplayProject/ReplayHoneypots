<template>
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>{{ $route.params.device | formatDBName }}</component-title>
        <hr class="o-20" />
        <article data-name="slab-stat">
            <dl class="dib mr5">
                <dd class="f6 f5-ns b ml0">Total Logs</dd>
                <dd class="f3 f2-ns b ml0">
                    {{ totalRecords }}
                </dd>
            </dl>
            <dl class="dib mr5">
                <dd class="f6 f5-ns b ml0">Location</dd>
                <dd class="f4 f3-ns b ml0">/{{ $route.params.device }}</dd>
            </dl>

            <sparkline
                v-if="!isAggregate"
                :title="$route.params.device"
                :chartstyles="'height:25rem;'"
                :class="$pickColor($route.params.device, hostsInfo.length > 4)"
                :timediff="datepickstart"
                :endtimespan="datepickend"
                :specificity="specificity"
            ></sparkline>
        </article>

        <div class="cf pa2 tc b" v-if="!isAggregate">
            <div class="fl dib w-100 w-33-l mv2">
                Start Time
                <datetime
                    v-model="datepickstart"
                    type="datetime"
                    use12-hour
                    title="Query Start Time"
                    auto
                ></datetime>
            </div>
            <div class="dib w-100 w-33-l mv2">
                <label for="days">Specificity</label>
                <br />
                <input
                    v-model.lazy.number="specificity"
                    type="number"
                    name="specificity"
                    min="1"
                    max="4"
                />
            </div>
            <div class="fr dib w-100 w-33-l mv2">
                End Time
                <datetime
                    v-model="datepickend"
                    type="datetime"
                    use12-hour
                    title="Query End Time"
                    auto
                ></datetime>
            </div>
        </div>
        <hr class="o-20" />
        <div class="mv3 w-100">
            <vue-good-table
                ref="datatable"
                mode="remote"
                @on-page-change="onPageChange"
                @on-sort-change="onSortChange"
                @on-column-filter="onColumnFilter"
                @on-per-page-change="onPerPageChange"
                @on-search="onSearch"
                :isLoading.sync="isLoading"
                :columns="fancyColumns"
                :totalRows="totalRecords"
                :rows="rows"
                :fixed-header="false"
                :line-numbers="false"
                theme="default"
                :pagination-options="{
                    enabled: true,
                }"
                :search-options="{
                    enabled: true,
                    trigger: 'enter',
                    skipDiacritics: true,
                    placeholder: 'Search this table',
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
import { mapState } from 'vuex'
import sparkline from '../components/sparkline'

export default {
    name: 'deviceDetails',
    components: {
        componentTitle,
        sparkline,
    },
    data() {
        return {
            // Give last day as default
            datepickstart: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            datepickend: new Date().toISOString(),
            specificity: 2,
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
                        type: 'desc', // 'asc' or 'desc'
                    },
                ],
                page: 1, // what page I want to show
                perPage: 10, // how many items I'm showing per page
            },
            columns: [
                {
                    label: 'Unique ID',
                    field: '_id',
                    type: 'text',
                    hidden: true,
                },
                {
                    label: 'Timestamp',
                    field: 'timestamp',
                    formatFn: x => {
                        let s = new Date(x * 1000)
                            .toLocaleString()
                            .replace('/' + new Date().getFullYear(), '')
                        return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
                    },
                    type: 'text',
                    width: '117px',
                },
                {
                    label: 'Proto',
                    field: 'trafficType',
                    type: 'text',
                    sortable: false,
                },
                {
                    label: 'sPort',
                    field: 'sourcePortNumber',
                    type: 'text',
                    width: '77px',
                },
                {
                    label: 'sourceIP',
                    field: 'sourceIPAddress',
                    type: 'text',
                },
                {
                    label: 'destPort',
                    field: 'destPortNumber',
                    type: 'text',
                },
                {
                    label: 'destIP',
                    field: 'destIPAddress',
                    type: 'text',
                },
            ],
            rows: [],
        }
    },
    watch: {
        hostsInfo() {
            this.updateTotal()
        },
        '$route.params.device': function () {
            this.loadItems()
            this.resetParams()
        },
        currentPage() {
            this.loadItems()
        },
    },
    computed: {
        isAggregate() {
            return this.$route.params.device === 'aggregate'
        },
        fancyColumns() {
            return [
                {
                    label: 'Host',
                    field: 'hostname',
                    type: 'text',
                    hidden: !this.isAggregate,
                },
                ...this.columns,
            ]
        },
        ...mapState(['hostsInfo']),
    },
    methods: {
        // Format Datetime
        formatDate(x) {
            return $this.parseDateWithTime(x)
        },
        updateTotal() {
            let h = this.$store.state.hostsInfo
            let d = this.$route.params.device

            if (this.isAggregate) {
                this.totalRecords = this.$store.getters.totalLogs
                return
            }

            if (h && h.length != 0) this.totalRecords = h.find(x => x.key === d).value
        },
        // DOCS: https://xaksis.github.io/vue-good-table/guide/advanced/remote-workflow.html#provide-handlers-for-user-events
        // Handlers for DB TABLE
        updateParams(newProps) {
            this.updateTotal()
            this.serverParams = Object.assign({}, this.serverParams, newProps)
        },
        resetParams() {
            this.updateParams({
                search: '',
                // a map of column filters example: {name: 'john', age: '20'}
                columnFilters: {},
                sort: [
                    {
                        field: 'timestamp', // example: 'name'
                        type: 'desc', // 'asc' or 'desc'
                    },
                ],

                page: 1, // what page I want to show
                perPage: 10, // how many items I'm showing per page
            })
            // Clear search
            this.$refs['datatable'].globalSearchTerm = ''
        },
        onPageChange(params) {
            this.updateParams({ page: params.currentPage })
            this.loadItems()
        },
        onPerPageChange(params) {
            this.updateParams({ perPage: params.currentPerPage })
            this.loadItems()
        },
        onSortChange(params) {
            this.updateParams({
                sort: params,
            })
            this.loadItems()
        },
        onColumnFilter(params) {
            this.updateParams(params)
            this.loadItems()
        },
        onSearch(params) {
            this.updateParams({ search: params.searchTerm, page: 1 })
            this.loadItems()
        },
        // load items is what brings back the rows from server
        async loadItems() {
            this.$Progress.start()
            this.isLoading = true

            let fields = [
                ...Object.keys(this.serverParams.columnFilters),
                ...this.serverParams.sort.map(x => x.field),
            ]

            if (!this.isAggregate) fields.push('hostname')

            fields.sort()

            // Query index
            if (fields.length != 0) {
                let idx = await this.$pouch.createIndex(
                    {
                        index: { fields },
                    },
                    this.dbURI
                )
                // Only log index creation if it was new
                if (idx.result != 'exists') {
                    console.log('New Index created: ', idx)
                    this.$toasted.show('New query index created')
                }
            }

            let selector = this.isAggregate
                ? {}
                : {
                      hostname: { $eq: this.$route.params.device },
                  }

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
            let skip = searchTerm
                ? 0
                : (this.serverParams.page - 1) * this.serverParams.perPage

            this.updateTotal()

            // Actually do a query
            let results = await this.$pouch.find(
                {
                    selector,
                    sort,
                    skip,
                    limit: searchTerm ? this.totalRecords : this.serverParams.perPage,
                },
                this.dbURI
            )

            // Apply local filter or just throw it on the page
            let inc = x =>
                JSON.stringify(x)
                    .toLocaleLowerCase()
                    .includes(searchTerm.toLocaleLowerCase())
            this.rows = searchTerm != '' ? results.docs.filter(inc) : results.docs

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
    },
    async created() {
        this.loadItems()
    },
}
</script>
