<template>
    <div class="br2 cf">
        <div class="pa3 flex-auto bb b--white-10 cf">
            <h3 class="mt0 mb1 f6 ttu white o-70">{{ title }} time span</h3>
            <transition name="fade">
                <h2 v-if="timespan != 0" class="mv0 f2 fw5 white">{{ timespan }}</h2>
            </transition>
        </div>
        <line-chart class="pt2" ref="chart" :chartData="chartData" :options="options" />
    </div>
</template>

<script>
import LineChart from './lineChart'

export default {
    components: { LineChart },
    props: ['title', 'value', 'numLogs'],
    data() {
        return {
            chartData: null,
            timespan: 0,
            options: {
                responsive: true,
                maintainAspectRatio: true,
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
    watch: {
        numLogs: function () {
            this.init()
        },
    },
    methods: {
        findTimeSpan(data) {
            let s = data.slice(-1) - data[0]

            let isSeconds = s < 60
            let isMinutes = s >= 60 && s < 60 * 60
            let isHours = s >= 60 * 60 && s < 60 * 60 * 24

            let dumb = x => parseFloat(Number(x).toPrecision(2))

            this.timespan = isSeconds
                ? dumb(s) + ' secs'
                : isMinutes
                ? dumb(s / 60) + ' mins'
                : isHours
                ? dumb(s / (60 * 60)) + ' hrs'
                : dumb(s / (60 * 60 * 25)) + ' days'
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

            let dumb = x => parseFloat(Number(x).toPrecision(9))

            var groupBy = (xs, key) =>
                xs.reduce((rv, x) => {
                    ;(rv[dumb(x[key])] = rv[dumb(x[key])] || []).push(x)
                    return rv
                }, {})

            let selector = { hostname: { $eq: this.title } }
            let sort = [{ timestamp: 'desc' }]
            let skip = 0
            // Actually do a query
            let results = await this.$pouch.find(
                {
                    selector,
                    sort,
                    skip,
                    fields: ['timestamp'],
                    limit: this.numLogs,
                },
                this.dbURI
            )
            // Apply local filter or just throw it on the page
            let mine = groupBy(results.docs, 'timestamp')
            // TODO: abstract this date logic from here and the details page

            let labels = Object.keys(mine).map(x => {
                let s = new Date(x * 1000)
                    .toLocaleString()
                    .replace('/' + new Date().getFullYear(), '')
                return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
            })

            // Find time difference (seconds then convert)
            // let keys = Object.keys(mine) // Use group times
            let keys = [results.docs.slice(-1)[0].timestamp, results.docs[0].timestamp] // Use result times
            this.findTimeSpan(keys)

            let data = Object.values(mine).map(x => x.length)

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
        async init() {
            // Wait till we have first status
            try {
                await this.loadData()
            } catch (error) {
                console.log(error)
            }
        },
    },
    async mounted() {
        this.init()
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
