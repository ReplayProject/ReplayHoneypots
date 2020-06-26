<template>
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>Traffic At a Glance</component-title>
        <hr class="o-20 mt2" />
        <section
            v-if="Object.keys($store.state.hostsInfo).length == 0"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <div
                @click="entryLimit > 0 ? (entryLimit = -1) : (entryLimit = 5)"
                :class="{
                    'bg-blue': entryLimit < 0,
                    white: entryLimit < 0,
                    'bg-white': entryLimit > 0,
                    blue: entryLimit > 0,
                }"
                class="dib b mv3 br2 ph4 pv2 mh2 ba b--blue pointer shadow-hover"
            >
                Toggle All Data Points
            </div>
            <hr class="o-20 mt2" />
            <div class="flex flex-wrap justify-center">
                <div
                    @click="host = ''"
                    class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue hover-bg-blue hover-white shadow-hover"
                    :class="{
                        'bg-blue': host == '',
                        white: host == '',
                        blue: host != '',
                    }"
                >
                    All
                </div>
                <div
                    v-for="n in $store.state.hostsInfo"
                    :key="n.key"
                    @click="host = n.key"
                    class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue hover-bg-blue hover-white shadow-hover"
                    :class="{
                        'bg-blue': host == n.key,
                        white: host == n.key,
                        blue: host != n.key,
                    }"
                >
                    {{ n.key | capitalize }}
                </div>
            </div>

            <hr class="o-20 mt2" />
            <div class="flex flex-wrap justify-center">
                <div
                    v-for="n in [300, 500, 1000, 2000]"
                    :key="n"
                    @click="numLogs = n"
                    class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue hover-bg-blue hover-white shadow-hover"
                    :class="{
                        'bg-blue': numLogs == n,
                        white: numLogs == n,
                        blue: numLogs != n,
                    }"
                >
                    Last {{ n }}
                </div>
            </div>
            <div class="flex flex-wrap pt3 nl3 nr3">
                <div
                    v-for="(data, idx) in formatNames([
                        'sourceIPData',
                        'destinationIPData',
                        'sourcePortData',
                        'destinationPortData',
                        'trafficData',
                        'lengthData',
                    ])"
                    :key="idx"
                    class="w-100 w-50-l ph3 mb3 mb0-l"
                >
                    <div class="bt bl br b--black-10 br2 mb3">
                        <div class="pa3 bb b--black-10">
                            <h4 class="mv0">{{ data.name }} Frequency</h4>
                        </div>
                        <metric-list-item
                            v-for="(entry, index) in data.source"
                            :key="index"
                            :show-bar="entry.showBar"
                            :name="entry.name"
                            :value="entry.value"
                            :percent="entry.percent"
                        >
                        </metric-list-item>
                    </div>
                </div>
            </div>
        </section>
    </main>
</template>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import metricListItem from '../components/metric-list-item'

export default {
    name: 'about',
    components: {
        componentTitle,
        PropagateLoader,
        metricListItem,
    },
    data() {
        return {
            data: null,
            logs: null,
            error: null,
            entryLimit: 5,
            numLogs: 300,
            host: '',
        }
    },
    watch: {
        numLogs() {
            this.loadData()
        },
        host() {
            this.loadData()
        },
    },
    computed: {
        sourceIPData() {
            return this.frequencyField('sourceIPAddress')
        },
        destinationIPData() {
            return this.frequencyField('destIPAddress')
        },
        sourcePortData() {
            return this.frequencyField('sourcePortNumber')
        },
        destinationPortData() {
            return this.frequencyField('destPortNumber')
        },
        trafficData() {
            return this.frequencyField('trafficType')
        },
        lengthData() {
            return this.frequencyField('length')
        },
    },
    methods: {
        formatNames(names) {
            return names.map(x => {
                let name = x.slice(0, -4)
                name = name.charAt(0).toUpperCase() + name.slice(1)

                return {
                    name,
                    source: this[x],
                }
            })
        },
        frequencyField(field) {
            if (!this.data) return []

            var groupBy = (xs, key) =>
                xs.reduce((rv, x) => {
                    ;(rv[x[key]] = rv[x[key]] || []).push(x)
                    return rv
                }, {})

            let stats = groupBy(this.data, field)

            let displayObj = Object.keys(stats).map(x => {
                return {
                    name: x,
                    value: stats[x].length,
                    percent: (stats[x].length / this.totalLogs) * 100,
                    showBar: true,
                }
            })

            displayObj.sort((a, b) => b.value - a.value)

            return displayObj.slice(0, this.entryLimit)
        },
        async loadData() {
            this.$Progress.start()
            let fields = ['hostname', 'timestamp']
            // Query index
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

            let selector = { timestamp: { $exists: true } }
            selector.hostname = this.host == '' ? { $exists: true } : { $eq: this.host }
            // Actually do a query
            let results = await this.$pouch.find(
                {
                    selector,
                    fields: [
                        'sourcePortNumber',
                        'sourceIPAddress',
                        'destPortNumber',
                        'destIPAddress',
                        'trafficType',
                        'length',
                    ],
                    limit: this.numLogs,
                },
                this.dbURI
            )
            // Lets do something with this data
            this.data = results.docs
            this.totalLogs = results.docs.length
            // Mark everything as done loading
            this.$Progress.finish()
        },
        setData(err, logs) {
            if (err) {
                this.error = err.toString()
            } else {
                this.logs = logs
            }
        },
    },
    async mounted() {
        try {
            await this.loadData(86400)
        } catch (error) {
            console.log(error)
        }
    },
}
</script>
