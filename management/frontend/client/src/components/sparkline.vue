<template>
    <div class="br2 cf">
        <div class="pa3 flex-auto bb b--white-10 cf">
            <h3 class="mt0 mb1 f6 ttu white o-70">{{ title }} timespan</h3>
            <transition name="fade">
                <h2 v-if="logsInFrame != 0" class="mv0 f2 fw5 white">
                    {{ logsInFrame }}
                </h2>
            </transition>
        </div>
        <line-chart class="pt2" ref="chart" :chartData="chartData" :options="options" />
    </div>
</template>

<script>
import LineChart from './lineChart'

export default {
    components: { LineChart },
    props: ['title', 'value', 'timediff', 'specificity'],
    data() {
        return {
            chartData: null,
            logsInFrame: null,
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
        timediff() {
            this.init()
        },
        specificity() {
            this.init()
        },
    },
    methods: {
        async findTimeBounds() {
            let selector = { hostname: { $eq: this.title } }
            let sort = [{ timestamp: 'desc' }]
            let skip = 0
            // Get the single most recent log to be the "end time" of our main query
            let results = await this.$pouch.find(
                {
                    selector,
                    sort,
                    skip,
                    fields: ['timestamp'],
                    limit: 1,
                },
                this.dbURI
            )

            if (results.docs.length == 0) {
                console.log('No Records found for ' + this.title)
                return
            }
            let endtime = new Date(results.docs[0].timestamp * 1000)
            let starttime = new Date(endtime.getTime() - this.timediff)
            return [starttime, endtime].map(x => x.getTime() / 1000)
        },
        async loadData(bounds) {
            this.$Progress.start()
            console.log(bounds)

            const div = (time, power) => Math.floor(time / Math.pow(10, power))
            const keymap = ts =>
                [...Array(Number(4)).keys()].map(x => div(ts, x)).reverse()

            let results = await this.$pouch.query(
                `timestamp-${this.title}/timestamp`,
                {
                    startkey: keymap(bounds[0]),
                    endkey: keymap(bounds[1]),
                    reduce: true,
                    group: true,
                    group_level: this.specificity,
                },
                this.dbURI
            )

            if (results.rows.length == 0) {
                this.chartData = {
                    datasets: [],
                }
                this.logsInFrame = 0
                return
            }

            this.logsInFrame = results.rows.reduce((a, x) => a + x.value, 0) + ' logs'

            // Apply local filter or just throw it on the page
            // TODO: abstract this date logic from here and the details page
            let labels = results.rows.map(x => {
                let s = new Date(x.key.slice(-1)[0] * 1000)
                    .toLocaleString()
                    .replace('/' + new Date().getFullYear(), '')
                return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
            })

            let data = results.rows.map(x => x.value)

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
                await this.loadData(await this.findTimeBounds())
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
