<template>
    <div class="br2">
        <div class="pa3 flex-auto bb b--white-10">
            <h3 class="mt0 mb1 f6 ttu white o-70">{{ title }}</h3>
            <h2 class="mv0 f2 fw5 white">{{ value }}</h2>
        </div>
        <div class="pt2">
            <line-chart ref="chart" :chartData="chartData" :options="options" />
        </div>
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
                            display: false,
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
                    fields: [],
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
