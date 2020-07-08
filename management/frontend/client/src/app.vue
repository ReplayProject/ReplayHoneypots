<template>
    <div class="mw8 center pt2 ph2 mt-3" id="dashboard">
        <div class="flex-m flex-l nl3-m nr3-m nl3-l nr3-l">
            <component-nav></component-nav>
            <!-- Waits to load views till we have hosts info -->
            <router-view></router-view>
        </div>
        <vue-progress-bar></vue-progress-bar>
    </div>
</template>

<script>
import componentNav from './components/nav'
import Chart from 'chart.js'

export default {
    name: 'App',
    components: {
        componentNav,
    },
    methods: {
        /**
         * Create design documents in the DB for various things
         */
        async designDocs() {
            let design_documents = [
                {
                    //  design doc for summary of hosts data, and a time grouping of logs
                    _id: `_design/timespans`,
                    views: {
                        hosttime: {
                            map: function (doc) {
                                emit(
                                    [
                                        doc.hostname,
                                        // This precision allows for different group by criteria on query
                                        Math.floor(doc.timestamp / 1000),
                                        Math.floor(doc.timestamp / 100),
                                        Math.floor(doc.timestamp / 10),
                                        Math.floor(doc.timestamp / 1),
                                    ],
                                    null
                                )
                            }.toString(),
                            reduce: '_count',
                        },
                    },
                },
            ]

            // save the various design docs
            try {
                let res = await this.$pouch.bulkDocs(design_documents, {}, this.dbURI)
                console.log('Design Doc Results: ', res)
            } catch (err) {
                if (err.error !== 'conflict')
                    console.log('Design Document already exists: ', err.messge)
            }

            // Query index for hostname & timestamp combinations
            let fields = ['hostname', 'timestamp']
            let idx = await this.$pouch.createIndex(
                {
                    index: { fields, name: 'hostname-timestamp' },
                },
                this.dbURI
            )

            // Only log index creation if it was new
            if (idx.result != 'exists') {
                console.log('New Index created: ', idx)
                this.$toasted.show('New query index created')
            }

            // Query index for alerts based on timestamp
            let fields2 = ['timestamp']
            let idx2 = await this.$pouch.createIndex(
                {
                    index: { fields: fields2 },
                },
                this.alertsURI
            )
            // Only log index creation if it was new
            if (idx2.result != 'exists') {
                console.log('New Index created: ', idx2)
                this.$toasted.show('New query index created')
            }
        },
        /**
         * Fetch alerts and save them to the store
         */
        async loadAlerts() {
            this.$Progress.start()

            let options = {
                selector: {},
                sort: [{ timestamp: 'desc' }],
                skip: 0,
                fields: [],
            }

            if (this.numAlerts > 0) options.limit = this.numAlerts

            // Actually do a query
            let results = await this.$pouch.find(options, this.alertsURI)
            this.$store.commit('setAlerts', results.docs)
            this.$Progress.finish()
        },
        /**
         * Bind event listeners to the CouchDB changed feed
         */
        async watchAlertsDB() {
            this.loadAlerts()

            var changes = this.$pouch.changes(
                {
                    since: 'now',
                    live: true,
                    include_docs: true,
                },
                this.alertsURI
            )

            changes.on('change', change => {
                if (!change.deleted) {
                    this.$store.commit('unshiftList', change.doc)
                    this.$store.commit('popAlerts') // remove element to keep number the same
                    this.$toasted.show('New alert from ' + change.doc.hostname)
                }
            })

            changes.on('complete', info => {
                console.log('complete', info)
            })

            changes.on('error', err => {
                console.log(err)
            })
        },
    },
    async mounted() {
        // Check for connection in a few seconds and alert user
        setTimeout(() => {
            if (this.$store.state.hostsInfo.length === 0) {
                console.warn(
                    'Database has no logs, or connection is being very slow.\n',
                    this.dbURI
                )
                this.$toasted.show('No management data found')
            }
        }, 5000)
        // Retrieve basic info about the DB
        console.log('Setting up DB')
        let info = await this.$pouch.info(this.dbURI)
        this.$store.commit('setAggInfo', info)
        // Attempt creation of indexes
        await this.designDocs()
        // Setup Alerts listeners
        await this.watchAlertsDB()
        // Fetch data about hosts in the DB and save to the store
        try {
            let result = await this.$pouch.query(
                `timespans/hosttime`,
                {
                    include_docs: false,
                    reduce: true,
                    group: true,
                    group_level: 1,
                },
                this.dbURI
            )
            this.$store.commit(
                'setHostsInfo',
                result.rows.map(x => ({ key: x.key[0], value: x.value }))
            )
        } catch (err) {
            console.log('Something went wrong with fetching DB info: ', err)
        }
        //  [App.vue specific] When App.vue is finish loading finish the progress bar
        this.$Progress.finish()
    },
    created() {
        Chart.defaults.global.legend.display = false
        //  [App.vue specific] When App.vue is first loaded start the progress bar
        this.$Progress.start()
        //  hook the progress bar to start before we move router-view
        this.$router.beforeEach((to, from, next) => {
            //  start the progress bar
            this.$Progress.start()
            //  continue to next page
            next()
        })
        //  hook the progress bar to finish after we've finished moving router-view
        this.$router.afterEach((to, from) => {
            //  finish the progress bar
            this.$Progress.finish()
        })
    },
}
</script>
