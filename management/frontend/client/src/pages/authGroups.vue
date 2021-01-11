<template>
    <!-- This page seeks to give general info about devices, filtered by tags -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'authGroups',
            'w-75-l': $route.name != 'authGroups',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>Auth Groups Management</template>
        </component-title>
        <hr class="o-20" />
        <section class="ph2 pt2" v-if="canAddAuthGroup">
            <div class="flex flex-auto justify-center pa2 mh2">
                <router-link
                    :to="'/authGroups/new'"
                    class="w-30 fr tc f4 link blue hover-dark-gray hover-shadow"
                    >Add New Auth Group</router-link
                >
            </div>
        </section>

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
                :totalRows="totalAuthGroups"
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
                <template slot="table-row" slot-scope="props">
                    <span v-if="props.column.field == 'btn'">
                        <button class="btn" @click="deleteAuthGroup(props.row._id)">Delete</button>
                    </span>
                    <span v-else>
                        {{props.formattedRow[props.column.field]}}
                    </span>
                </template>
                <div slot="emptystate">
                    No Auth Groups exist in system.
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
    name: 'authGroups',
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
                        field: '_id', // example: 'name'
                        type: 'asc', // 'asc' or 'desc'
                    },
                ],
                page: 1, // what page I want to show
                perPage: 10, // how many items I'm showing per page
            },
            columns: [
                {
                    label: 'Name of Auth Group',
                    field: '_id',
                    type: 'text',
                },
                {
                    label: 'Edit',
                    field: 'btn',
                    sortable: false,
                    html: true,
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
    computed: {
        canAddAuthGroup: function () {
            if (this.$store.state.permsData.authGroupsMgmt === 2) {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.authGroupsMgmt === 0) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
        /**
         * Deletes Auth Group from Database
         */
        deleteAuthGroup: async function(_id) {
            try {
                let deleteResponse = await api.deleteAuthGroup(_id)
                if (deleteResponse.status !== 200) {
                    console.log("deleteResponse code was not 200")
                    this.$toasted.show('Failed to delete Auth Group. Error: deleteResponse code was not 200')
                } else {
                    this.$toasted.show('Deleted Auth Group ' + _id)
                    this.loadItems()

                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Deleted Auth Group ' + _id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                }
            } catch (err) {
                console.log(err)
                this.$toasted.show('Failed to delete Auth Group. Error: ' + err.message)
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
            
            //Get the Auth Groups
            try {
                const results = await api.getAuthGroups(undefined, sort, skip, undefined, limit)
                const total = await api.getAuthGroups(undefined, undefined, 0, ['_id'], undefined)
                // Lets do something with this data
                this.data = results.data.docs
                this.totalAuthGroups = total.data.docs.length

                // Apply local filter or just throw it on the page
                let inc = x =>
                     JSON.stringify(x)
                         .toLocaleLowerCase()
                         .includes(searchTerm.toLocaleLowerCase())
                this.rows = searchTerm != '' ? results.data.docs.filter(inc) : results.data.docs
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
                        field: '_id', // example: 'name'
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
        this.checkPageAccessPermissions()
        this.loadItems()
    },
}
</script>
