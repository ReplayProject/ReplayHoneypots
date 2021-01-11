<template>
    <div class="br2">
        <div class="pa3 flex-auto bb b--white-10">
            <h3 class="mt0 mb1 f6 ttu white o-70">{{ title }} timespan</h3>
            <transition name="fade">
                <h2 class="mv0 f2 fw5 white">
                    {{ logsInFrame ? logsInFrame : '0 logs' }}
                </h2>
            </transition>
        </div>
        <line-chart
            :style="chartstyles"
            ref="chart"
            :chartData="chartData"
            :options="options"
        />
    </div>
</template>

<script>
import LineChart from './lineChart'
import api from '../api.js'

export default {
    components: { LineChart },
    props: ['title', 'dataIdentifier', 'chartstyles', 'endtimespan', 'timediff', 'specificity'],
    data() {
        return {
            chartData: null,
            logsInFrame: null,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                elements: {
                    point: {
                        radius: 3,
                    },
                },
                scales: {
                    xAxes: [
                        {
                            display: false,
                        },
                    ],
                    yAxes: [
                        {
                            display: true,
                            gridLines: { color: '#00000075' },
                            ticks: {
                                beginAtZero: false,
                                fontColor: '#00000075',
                            },
                        },
                    ],
                },
            },
        }
    },
    /**
     * This section reloads the chart when various bits of data change
     */
    watch: {
        timediff() {
            this.init()
        },
        title() {
            this.chartData = {
                datasets: [],
            }
            this.logsInFrame = 0
            this.init()
        },
        endtimespan() {
            this.init()
        },
        specificity() {
            this.init()
        },
    },
    methods: {
        /**
         * Find the bounds for a couchDB query
         */
        async findTimeBounds() {
            let fields = ['timestamp']
            let limit = 1
            let results = {}

            let getError = false
            try {
                results = await api.getLogs(this.dataIdentifier, undefined, 0, fields, limit)
            } catch (err) {
                getError = true
                console.log(err)
            }

            if (getError === true || results.data.docs.length == 0) {
                console.log('No Records found for ' + this.title)
                return
            }

            let endtime = new Date(results.data.docs[0].timestamp * 1000)
            let starttime = new Date(endtime.getTime() - this.timediff)

            return [starttime, endtime].map(x => x.getTime() / 1000)
        },
        /**
         * Given some time bounds, fetch data from the index, format it human reable
         * and display it
         */
        async loadData(bounds) {
            this.$Progress.start()
            const div = (time, power) => Math.floor(time / Math.pow(10, power))
            const keymap = ts => [
                this.dataIdentifier,
                ...[...Array(Number(4)).keys()].map(x => div(ts, x)).reverse(),
            ]

            let results = {}
            try {
                results = await api.getHostsInfoBy(
                    keymap(bounds[0]),
                    keymap(bounds[1]),
                    this.specificity + 1
                )
            } catch (err) {
                console.log(err)
            }

            if (!results.data || results.data.rows.length == 0) {
                this.chartData = {
                    datasets: [],
                }
                this.logsInFrame = 0
                return
            }
            // Count totals
            this.logsInFrame =
                results.data.rows.reduce((a, x) => a + x.value, 0) + ' logs'

            // Apply local filter or just throw it on the page
            // TODO: abstract this date logic from here and the details page
            let labels = results.data.rows.map(x => {
                // Convery the varying size numbers to the same date range by filling in zeroes
                let ts = x.key.slice(-1)[0] * Math.pow(10, 4 - this.specificity)
                let s = new Date(ts * 1000)
                    .toLocaleString()
                    .replace('/' + new Date().getFullYear(), '')
                // Use the pretty formatted string
                return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
            })

            let data = results.data.rows.map(x => x.value)

            this.chartData = {
                labels,
                datasets: [
                    {
                        pointBackgroundColor: 'white',
                        borderWidth: 2,
                        borderColor: '#FFFFFF',
                        data,
                    },
                ],
            }

            // Mark everything as done loading
            this.$Progress.finish()
        },
        /**
         * Kick off loading data
         */
        async init() {
            const parseDateString = x => new Date(x).getTime() / 1000
            // Wait till we have first status
            try {
                let bounds = !this.endtimespan
                    ? await this.findTimeBounds()
                    : [
                        parseDateString(this.timediff),
                        parseDateString(this.endtimespan),
                    ]
                await this.loadData(bounds)
            } catch (error) {
                console.log(error)
            }
        },
    },
    async mounted() {
        await this.init()
    },
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
    opacity: 0;
}
</style>
