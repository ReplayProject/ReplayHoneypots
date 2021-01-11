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
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>User Management</template>
        </component-title>
        <hr class="o-20" />
        <section class="ph2 pt2" v-if="canAddUser">
            <div class="flex flex-auto justify-center pa2 mh2">
                <router-link
                    :to="'/users/new'"
                    class="w-20 fr tc f4 link blue hover-dark-gray hover-shadow"
                    >Add New User</router-link
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
                :totalRows="totalUsers"
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
                    No users exist in system.
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
                        field: 'username', // example: 'name'
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
                    label: 'Username',
                    field: 'username',
                    type: 'text',
                },
                {
                    label: 'First Name',
                    field: 'firstname',
                    type: 'text',
                },
                {
                    label: 'Last Name',
                    field: 'lastname',
                    type: 'text',
                },
                {
                    label: 'Role',
                    field: 'role',
                    type: 'text',
                },
                {
                    label: 'Local',
                    field: 'local',
                    type: 'boolean',
                },
                {
                    label: 'Enabled',
                    field: 'enabled',
                    type: 'boolean',
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
        canAddUser: function () {
            if (this.$store.state.permsData.users === 2) {
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
            if (this.$store.state.permsData.users === 0) {
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
            //Get the users
            try {
                const results = await api.getUsers(undefined, sort, skip, undefined, limit)
                const total = await api.getUsers(undefined, undefined, 0, ['_id'], undefined)
                // Lets do something with this data
                this.data = results.data.docs
                this.totalUsers = total.data.docs.length
                // Add button to the data rows
                for (let i = 0; i < results.data.docs.length; i++) {
                    const pageLink = '/users/' + results.data.docs[i]._id
                    results.data.docs[i].btn =
                        '<button onclick="window.location.href=\'' +
                        pageLink +
                        '\';">Edit</button>'
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
                        field: 'username', // example: 'name'
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
