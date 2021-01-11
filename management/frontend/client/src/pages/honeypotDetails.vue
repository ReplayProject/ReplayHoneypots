<template>
    <!-- This page shows a graph that lets you drill down into log distributions,
    and a datatable for looking at logs. The searches are really slow due to full-text

    The datatable component adds most of the complexity found in this file -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <section
            v-if="!honeypotData"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <component-title>
                <template v-slot:pageCategory>Dashboards</template>
                <template v-slot:pageName>{{ honeypotData.hostname | formatDBName }}</template>
            </component-title>
            <hr class="o-20" />
            <article data-name="slab-stat">
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Update Honeypot"
                    v-on:click="updateHoneypot()"
                    :disabled="!canModifyHoneypot"
                />
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Delete Honeypot"
                    v-on:click="deleteHoneypot()"
                    :disabled="!canModifyHoneypot"
                />
            </article>
            <hr class="o-20" />
            <article data-name="slab-stat">
                <dl class="dib mr5">
                    <dd class="f6 f5-ns b ml0">Config Assignment</dd>
                    <select name="configs" id="configs" v-model="honeypotData.config_id" :value="honeypotData.config_id" required>
                        <option v-for="item in configsData" v-bind:value="item._id" v-bind:key="item._id">
                            {{item._id}}
                        </option>
                    </select>
                </dl>
                <dl class="dib mr5">
                    <dd class="f6 f5-ns b ml0">Authorization Group Assignment</dd>
                    <select name="configs" id="configs" v-model="honeypotData.auth_group_id" :value="honeypotData.auth_group_id" required>
                        <option v-for="item in authGroupsData" v-bind:value="item._id" v-bind:key="item._id">
                            {{item._id}}
                        </option>
                    </select>
                </dl>
            </article>
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
                    :title="honeypotData.hostname"
                    :dataIdentifier="$route.params.device"
                    :chartstyles="'height:25rem;'"
                    :class="
                        $pickColor(
                            $route.params.device,
                            false
                        )
                    "
                    :timediff="datepickstart"
                    :endtimespan="datepickend"
                    :specificity="specificity"
                ></sparkline>
            </article>

            <div class="cf pa2 tc b">
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
                        No Logs have been loaded or recorded yet.
                    </div>
                </vue-good-table>
            </div>
        </section>
    </main>
</template>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import { mapState } from 'vuex'
import sparkline from '../components/sparkline'
import api from '../api.js'

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
            honeypotData: null,
            hostData: null,
            configsData: null,
            authGroupsData: null,
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
                    label: 'Protocol',
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
    /**
     * Update component when certain data changes
     */
    watch: {
        '$route.params.device': function () {
            this.loadMainItems()
            this.resetParams()
        },
        currentPage() {
            this.loadMainItems()
        },
    },
    computed: {
        canModifyHoneypot: function () {
            var specificAccess = this.$store.state.permsData.devices
            let authGroupAccesses = this.$store.state.permsData.authGroupsList
            for (let i = 0; i < authGroupAccesses.length; i++) {
                if (authGroupAccesses[i]._id === this.honeypotData.auth_group_id) {
                    specificAccess = authGroupAccesses[i].value
                }
            }

            if (specificAccess === 2) {
                return true
            } else {
                return false
            }
        },
    },
    methods: {
        /**
         * Updates the honeypot object in the database with the contents of the form
         */
        async updateHoneypot() {
            this.$Progress.start()
            try {
                let updateResponse = await api.updateHoneypot(this.$route.params.device, this.honeypotData)
                if (updateResponse.status !== 200) {
                    console.log("updateResponse code was not 200")
                    this.$toasted.show('Failed to update honeypot. Error: updateResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Updated Honeypot ' + this.honeypotData.hostname,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                    this.$toasted.show('Updated Honeypot ' + this.$route.params.device)
                    this.loadMainItems()
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update honeypot. Error: ' + updateError.message)
                this.loadMainItems()
            }
            this.$Progress.finish()
        },
        /**
         * Marks the honeypot as deleted in the database
         */
        async deleteHoneypot() {
            // Deleting honeypots in this system is not a true delete - we keep their records to be able to recover honeypots if they
            // are deleted in the system but not decommisioned. A running honeypot automatically 'undeletes' itself in the system if it
            // detects that its record was deleted.
            try {
                this.honeypotData.deleted = true
                let deleteResponse = await api.updateHoneypot(this.$route.params.device, this.honeypotData)
                if (deleteResponse.status !== 200) {
                    console.log("deleteResponse code was not 200")
                    this.$toasted.show('Failed to delete honeypot. Error: deleteResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Deleted Honeypot ' + this.honeypotData.hostname,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                    this.$toasted.show('Deleted Honeypot ' + this.$route.params.device)
                    this.$router.push('/honeypots')
                }
            } catch (deleteError) {
                console.log(deleteError)
                this.$toasted.show('Failed to delete honeypot. Error: ' + deleteError.message)
            }
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        async checkPageAccessPermissions() {
            // Load only enough data to check auth group
            var honeypotAuthID
            try {
                honeypotAuthID = await api.getHoneypots(this.$route.params.device, undefined, 0, ['auth_group_id'], 1)
            } catch (error) {
                console.log(error)
            }

            var specificAccess = this.$store.state.permsData.devices

            let authGroupAccesses = this.$store.state.permsData.authGroupsList
            for (let i = 0; i < authGroupAccesses.length; i++) {
                if (authGroupAccesses[i]._id === honeypotAuthID) {
                    specificAccess = authGroupAccesses[i].value
                }
            }

            if (specificAccess === 0) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
        // Format Datetime
        formatDate(x) {
            return $this.parseDateWithTime(x)
        },
        // DOCS: https://xaksis.github.io/vue-good-table/guide/advanced/remote-workflow.html#provide-handlers-for-user-events
        // Handlers for DB TABLE
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
            this.loadMainItems()
        },
        onPerPageChange(params) {
            this.updateParams({ perPage: params.currentPerPage })
            this.loadMainItems()
        },
        onSortChange(params) {
            this.updateParams({
                sort: params,
            })
            this.loadMainItems()
        },
        onColumnFilter(params) {
            this.updateParams(params)
            this.loadMainItems()
        },
        onSearch(params) {
            this.updateParams({ search: params.searchTerm, page: 1 })
            this.loadMainItems()
        },
        async loadOptionsLists() {
            this.$Progress.start()
            this.isLoading = true

            // Get list of configs for assignment
            try {
                // Get configs data
                let configsResponse = await api.getConfigs()
                this.configsData = configsResponse.data.docs
                // Get auth groups data
                let groupsResponse = await api.getAuthGroups()
                this.authGroupsData = groupsResponse.data.docs
            } catch (err) {
                console.log(err)
            }

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
        /**
         * load items is what brings back the rows from server
         */
        async loadMainItems() {
            this.$Progress.start()
            this.isLoading = true

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

            // Get all data needed for the page
            var results = []
            try {
                // Get host data
                let startkey = [this.$route.params.device]
                let endkey = ["ZZZ"] // Acts as a filler endkey
                let hostResponse = await api.getHostsInfoBy(startkey, endkey, 1)

                if (hostResponse.data.rows == undefined || hostResponse.data.rows.length === 0) {
                    this.totalRecords = 0
                } else {
                    this.totalRecords = hostResponse.data.rows[0].value
                }
                // Get Log data
                results = await api.getLogs(
                    this.$route.params.device,
                    sort,
                    skip,
                    undefined,
                    limit
                )
                // Get honeypot data
                let serverResponse = await api.getHoneypots(this.$route.params.device)
                this.honeypotData = serverResponse.data.docs[0]
                this.loadOptionsLists()
            } catch (err) {
                console.log(err)
            }
            // Apply local filter or just throw it on the page
            let inc = x =>
                JSON.stringify(x)
                    .toLocaleLowerCase()
                    .includes(searchTerm.toLocaleLowerCase())
            
            if (results.data == undefined || results.data.length === 0) {
                this.rows = []
            } else {
                this.rows = searchTerm != '' ? results.data.docs.filter(inc) : results.data.docs
            }

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
    },
    beforeMount() {
        this.checkPageAccessPermissions().then( () => {
            this.loadMainItems()
        })
    },
}
</script>
