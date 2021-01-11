<template>
    <!-- This page seeks to give general info about devices, filtered by tags -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Dashboards</template>
            <template v-slot:pageName>Device Metrics</template>
        </component-title>
        <hr class="o-20" />
        <div class="mv3 w-100"> Filter by Tag </div>
        <div class="mv3 w-100">
            <select class="form-control" @change="changeTag($event)">
                <option value="all"> All </option>
                <option v-for="tag in tags" :value="tag" :key="tag">{{tag}}</option>
            </select>
        </div>

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
                :columns="columns"
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
                    No Heartbeats found.
                </div>
                <template slot="table-row" slot-scope="props">
                    <span v-if="props.column.field == 'timestamp' && props.row.isExpired == 'True'">
                        <span style="font-weight: bold; color: red;">{{props.formattedRow[props.column.field]}}</span> 
                    </span>
                    <span v-else>
                        {{props.formattedRow[props.column.field]}}
                    </span>
                </template>
            </vue-good-table>
        </div>
    </main>
</template>

<script>
import componentTitle from '../components/title'
import VueJsonPretty from 'vue-json-pretty'
import api from '../api.js'

export default {
    name: 'metrics',
    components: {
        componentTitle,
        VueJsonPretty,
    },
    data() {
        return {
            dbInfo: {},
            isLoading: false,
            selectedTag: 'All',
            tags: [],
            totalRecords: 0,
            serverParams: {
                search: '',
                // a map of column filters example: {name: 'john', age: '20'}
                columnFilters: {},
                sort: [
                    {
                        field: 'hostname', // example: 'name'
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
                    label: 'Expired',
                    field: 'isExpired',
                    type: 'text',
                    hidden: true,
                },
                {
                    label: 'Hostname',
                    field: 'hostname',
                    type: 'text',
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
                    label: '% CPU Usage',
                    field: 'cpu',
                    type: 'text',
                },
                {
                    label: '% RAM Usage',
                    field: 'ram',
                    type: 'text',
                },
                {
                    label: 'Storage',
                    field: 'storage',
                    type: 'text',
                },
            ],
            rows: [],
        }
    },
    watch: {
        currentPage() {
            this.loadItems()
        },
        '$route.params.selectedTag': function () {
            this.loadItems()
            this.resetParams()
        },
    },
    methods: {
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.metrics === 0) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
        async loadItems() {
            this.$Progress.start()
            
            try {
                let results = await api.getAllTags()
                this.tags = results.data
            } catch (err) {
                console.log(err)
            }
            
            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
        async loadTable() {
            this.$Progress.start()
            try {
                var now = Date.now()
                var expiredThreshold = now - (15 * 60000)
                console.log(expiredThreshold)

                // console.log(this.selectedTag)
                // Devides on the values for tag and auth group filtering
                this.selectedAuth = 'All'
                let searchTag = this.selectedTag == 'All' ? undefined : this.selectedTag
                let searchAuth = this.selectedAuth == 'All' ? undefined : this.selectedAuth

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

                let limit = searchTerm ? undefined : this.serverParams.perPage

                // Get and process data
                this.rows = []
                let results = await api.getAllMetrics(searchTag, searchAuth, sort, skip, undefined, limit)
                let total = await api.getAllMetrics(searchTag, searchAuth, undefined, 0, ['_id'], undefined)
                // console.log(results)
                
                // Apply local filter or just throw it on the page
                let inc = x =>
                    JSON.stringify(x)
                        .toLocaleLowerCase()
                        .includes(searchTerm.toLocaleLowerCase())
                this.rows = searchTerm != '' ? results.data.docs.filter(inc) : results.data.docs
                this.totalRecords = searchTerm != '' ? this.rows.length : total.data.docs.length

                for (let i = 0; i < this.rows.length; i++) {
                    if (this.rows[i].timestamp < Math.floor(expiredThreshold / 1000)) {
                        this.rows[i].isExpired = "True"
                    } else {
                        this.rows[i].isExpired = "False"
                    }
                }
            
            } catch (err) {
                console.log(err)
            }

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
        updateParams(newProps) {
            this.serverParams = Object.assign({}, this.serverParams, newProps)
        },
        resetParams() {
            this.updateParams({
                search: '',
                // a map of column filters example: {name: 'john', age: '20'}
                columnFilters: {},
                sort: [
                    {
                        field: 'hostname', // example: 'name'
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
            this.loadTable()
        },
        onPerPageChange(params) {
            this.updateParams({ perPage: params.currentPerPage })
            this.loadTable()
        },
        onSortChange(params) {
            this.updateParams({
                sort: params,
            })
            this.loadTable()
        },
        onColumnFilter(params) {
            this.updateParams(params)
            this.loadTable()
        },
        onSearch(params) {
            this.updateParams({ search: params.searchTerm, page: 1 })
            this.loadTable()
        },
        changeTag(event) {
            this.selectedTag = event.target.options[event.target.options.selectedIndex].text
            this.loadTable()
        },
    },
    beforeMount() {
        this.checkPageAccessPermissions()
        this.loadItems()
        this.loadTable()
    },
}
</script>
