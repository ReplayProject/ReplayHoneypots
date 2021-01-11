<template>
    <!-- This page seeks to give general info about devices, filtered by tags -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'adminLogs',
            'w-75-l': $route.name != 'adminLogs',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>Admin Logs</template>
        </component-title>
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
                :columns="columns"
                :totalRows="totalAdminLogs"
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
                    No Admin Logs exist in system.
                </div>
            </vue-good-table>
        </div>
    </main>
</template>

<script>
import componentTitle from '../components/title'
import VueJsonPretty from 'vue-json-pretty'
import api from '../api.js'

export default {
    name: 'adminLogs',
    components: {
        componentTitle,
        VueJsonPretty,
    },
    data() {
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
                    hidden: 'true',
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
                    label: 'Changed By',
                    field: 'changedBy',
                    type: 'text',
                },
                {
                    label: 'Message',
                    field: 'message',
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
        '$route.params.tag': function () {
            this.loadItems()
            this.resetParams()
        },
    },
    methods: {
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.adminLogs === 0) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
        async loadItems() {
            this.$Progress.start()
            let fields = ''

            //Column filters not working
            Object.keys(this.serverParams.columnFilters).forEach(x => {
                selector[x] = { $eq: this.serverParams.columnFilters[x] }
            })

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

            let limit = searchTerm ? this.totalRecords : this.serverParams.perPage
            
            //Get the Admin Logs
            try {
                const results = await api.getAdminLogs(undefined, sort, skip, undefined, limit)
                const total = await api.getAdminLogs(undefined, undefined, 0, ['_id'], undefined)
                
                // Lets do something with this data
                this.data = results.data.docs
                this.totalAdminLogs = total.data.docs.length

                // Apply local filter or just throw it on the page
                let inc = x =>
                    JSON.stringify(x)
                        .toLocaleLowerCase()
                        .includes(searchTerm.toLocaleLowerCase())
                this.rows =
                    searchTerm != '' ? results.data.docs.filter(inc) : results.data.docs
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
    },
    beforeMount() {
        this.checkPageAccessPermissions()
        this.loadItems()
    },
}
</script>
