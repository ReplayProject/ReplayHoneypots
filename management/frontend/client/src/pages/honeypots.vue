<template>
    <!-- This page seeks to give general info about devices, filtered by tags -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'users',
            'w-75-l': $route.name != 'users',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Dashboards</template>
            <template v-slot:pageName>Honeypots</template>
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
                    No honeypots exist in system.
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
    name: 'users',
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
                        field: 'hostname', // example: 'name'
                        type: 'asc', // 'asc' or 'desc'
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
                    label: 'Hostname',
                    field: 'hostname',
                    type: 'text',
                },
                {
                    label: 'IP Address',
                    field: 'ip_addr',
                    type: 'text',
                },
                {
                    label: 'Config',
                    field: 'config_id',
                    type: 'text',
                },
                {
                    label: 'Auth Group',
                    field: 'auth_group_id',
                    type: 'text',
                },
                {
                    label: 'Details',
                    field: 'btn',
                    html: true,
                    sortable: false,
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
            //Get the users
            try {
                const results = await api.getHoneypots(undefined, sort, skip, undefined, limit)
                const total = await api.getHoneypots(undefined, undefined, 0, ['_id'], undefined)
                // Lets do something with this data
                this.data = results.data.docs
                this.totalRecords = total.data.docs.length
                // Add button to the data rows
                for (let i = 0; i < results.data.docs.length; i++) {
                    const pageLink = '/honeypots/' + results.data.docs[i]._id
                    results.data.docs[i].btn =
                        '<button onclick="window.location.href=\'' +
                        pageLink +
                        '\';">Details</button>'
                }
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
                        field: 'hostname', // example: 'name'
                        type: 'asc', // 'asc' or 'desc'
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
        this.loadItems()
    },
}
</script>
