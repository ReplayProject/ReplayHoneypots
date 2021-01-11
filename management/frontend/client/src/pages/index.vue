<template>
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Home</template>
            <template v-slot:pageName>General Stats</template>
        </component-title>
        <hr class="o-20" />
        <section
            v-if="!hostsData"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <div class="flex-m flex-l flex-wrap items-center justify-between nl3 nr3">
                <div
                    v-if="hostsData"
                    style="margin: auto;"
                    class="w-100 w-50-l w-75-m tc mb4 mb0-l"
                >
                    <doughnut
                        :options="{
                            cutoutPercentage: 65,
                            layout: {
                                padding: {
                                    left: 0,
                                    right: 0,
                                    top: 0,
                                    bottom: 0,
                                },
                            },
                            title: {
                                display: true,
                                fontSize: 19,
                                text: [
                                    'Log Distribution',
                                    Number(
                                        //TODO: Get file size
                                        (
                                            logsData.sizes.file / 1000000
                                        ).toPrecision(4)
                                    ) + ' mb',
                                ],
                            },
                            //legend: {
                            //    position: 'bottom',
                            //    display: true,
                            //    labels: {
                            //        fontSize: 14,
                            //    },
                            //},
                        }"
                        :chartData="{
                            labels: piData[1].map((x, i) => x + ': ' + piData[0][i]),
                            datasets: [
                                {
                                    data: piData[0],
                                    backgroundColor: piData[2],
                                    hoverBackgroundColor: piData[2],
                                },
                            ],
                        }"
                    ></doughnut>
                </div>
            </div>
        </section>
    </main>
</template>

<style scoped>
@media screen and (min-width: 60em) {
    .w-33-l {
        width: 33.3%;
    }
}
</style>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import doughnut from '../components/doughnut'
import sparkline from '../components/sparkline'
import { mapState } from 'vuex'
import api from '../api.js'

export default {
    name: 'index',
    components: {
        componentTitle,
        PropagateLoader,
        doughnut,
        sparkline,
    },
    data() {
        return {
            hostsData: null,
            logsData: null,
            timespan: {
                minutes: 0,
                hours: 1,
                days: 0,
                specificity: 2,
            },
        }
    },
    computed: {
        ...mapState(['hostsInfo']),
        /**
         * Detup date for the pie chart
         */
        piData() {
            var l = this.hostsData.map(x => x.key)
            return [
                this.hostsData.map(x => x.value),
                l,
                l.map(x => this.$pickColor(x, this.hostsData.length > 4).slice(3)),
            ]
        },
        isNested() {
            return this.$route.name == 'overview'
        },
        /**
         * Convert user selections into a span of ms
         */
        timediff() {
            // Time diff in milliseconds
            return (
                this.timespan.minutes * 60 * 1000 +
                this.timespan.hours * 60 * 60 * 1000 +
                this.timespan.days * 24 * 60 * 60 * 1000
            )
        },
    },
    methods: {
        async loadData() {
            // Retrieve basic info about the DB
            try {
                const logInfo = await api.getLogDBInfo()
                this.logsData = logInfo.data
                const hostsInfo = await api.getHostsInfo()
                this.hostsData = hostsInfo.data.rows.map(x => ({ key: x.key[0], value: x.value }))
            } catch (err) {
                console.log(err)
            }
        },
    },
    beforeMount() {
        this.loadData()
    },
}
</script>
