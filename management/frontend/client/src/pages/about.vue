<template>
    <!-- This page seeks to give general info about recent logs, with summaries of data and log fields -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Dashboards</template>
            <template v-slot:pageName>Traffic at a Glance</template>
        </component-title>
        <hr class="o-20" />
        <section
            v-if="!this.data"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <div
                @click="entryLimit > 0 ? (entryLimit = 0) : (entryLimit = 300)"
                :class="{
                    'bg-blue': entryLimit < 1,
                    white: entryLimit < 1,
                    'bg-white': entryLimit > 0,
                    blue: entryLimit > 0,
                }"
                class="dib b mv3 br2 ph4 pv2 mh2 ba b--blue pointer shadow-hover"
            >
                Toggle All Data Points
            </div>
            <hr class="o-20" />
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
                    v-for="n in this.honeypotIDs"
                    :key="n"
                    @click="host = n"
                    class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue hover-bg-blue hover-white shadow-hover"
                    :class="{
                        'bg-blue': host == n,
                        white: host == n,
                        blue: host != n,
                    }"
                >
                    {{ n }}
                </div>
            </div>

            <hr class="o-20" />
            <div class="flex flex-wrap justify-center">
                <div
                    v-for="n in [300, 500, 1000, 2000]"
                    :key="n"
                    @click="entryLimit = n"
                    class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue hover-bg-blue hover-white shadow-hover"
                    :class="{
                        'bg-blue': entryLimit == n,
                        white: entryLimit == n,
                        blue: entryLimit != n,
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
import api from '../api.js'

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
            entryLimit: 300,
            totalLogs: 0,
            honeypotIDs: [],
            host: '',
        }
    },
    /**
     * Reload when logs and host change
     */
    watch: {
        entryLimit() {
            this.loadData()
        },
        totalLogs() {
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
        /**
         * Make DB names prettier
         */
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
        /**
         * Take a field and compute the relative frequency it appears in the last N logs
         */
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
        /**
         * Kick off the loading of data
         */
        async loadData() {
            this.$Progress.start()
            let selector = this.host
            let sort = 'desc'
            let skip = 0
            let fields = []

            //Get the logs
            try {
                const results = await api.getLogs(
                    this.host == '' ? undefined : this.host,
                    undefined,
                    0,
                    undefined,
                    this.entryLimit
                )
                // Lets do something with this data
                this.data = results.data.docs
                this.totalLogs = results.data.docs.length

                this.honeypotIDs = []
                for (let i = 0; i < this.data.length; i++) {
                    if (this.honeypotIDs.includes(this.data[i].uuid) === false) {
                        this.honeypotIDs.push(this.data[i].uuid)
                    }
                }
            } catch (err) {
                console.log(err)
            }

            // Mark everything as done loading
            this.$Progress.finish()
        },
    },
    beforeMount() {
        this.loadData()
    },
}
</script>
