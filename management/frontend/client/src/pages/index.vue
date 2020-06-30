<template>
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>General Stats</component-title>
        <hr class="o-20" />
        <section
            v-if="Object.keys(hostsInfo).length == 0"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <div class="flex-m flex-l flex-wrap items-center justify-between nl3 nr3">
                <div
                    v-if="hostsInfo"
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
                                        (
                                            $store.state.aggInfo.sizes.file / 1000000
                                        ).toPrecision(4)
                                    ) + ' mb',
                                ],
                            },
                            legend: {
                                position: 'right',
                                display: true,
                                labels: {
                                    fontSize: 14,
                                },
                            },
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
            <div class="divide tc relative">
                <h5 class="fw4 ttu mv0 dib bg-white ph3">Quick Stats</h5>
            </div>
            <p class="tc center w-100 mv1">
                Time distribution, clusters, and total logs of the
                <b>last active timespan</b> for each device
            </p>

            <div class="pa2 flex flex-wrap black b">
                <div class="dib w-50 w-25-l tc">
                    <label for="minutes">Minutes:</label>
                    <br />
                    <input
                        class="w4"
                        :class="{
                            'bg-light-blue': timespan.minutes != 0,
                        }"
                        v-model.lazy.number="timespan.minutes"
                        type="number"
                        name="minutes"
                        min="0"
                        max="60"
                    />
                </div>
                <div class="dib w-50 w-25-l tc">
                    <label for="hours">Hours:</label>
                    <br />
                    <input
                        class="w4"
                        :class="{
                            'bg-light-blue': timespan.hours != 0,
                        }"
                        v-model.lazy.number="timespan.hours"
                        type="number"
                        name="hours"
                        min="0"
                        max="24"
                    />
                </div>
                <div class="dib w-50 w-25-l tc">
                    <label for="days">Days:</label>
                    <br />
                    <input
                        class="w4"
                        :class="{
                            'bg-light-blue': timespan.days != 0,
                        }"
                        v-model.lazy.number="timespan.days"
                        type="number"
                        name="days"
                        min="0"
                        max="365"
                    />
                </div>
                <div class="dib w-50 w-25-l tc">
                    <label for="days">Specificity</label>
                    <br />
                    <input
                        class="w4"
                        v-model.lazy.number="timespan.specificity"
                        type="number"
                        name="specificity"
                        min="1"
                        max="4"
                    />
                </div>
            </div>
            <br />
            <div class="flex flex-wrap">
                <div
                    v-for="db in hostsInfo"
                    :key="db.key"
                    class="w-100 w-50-m w-33-l mb4 mb0-l relative flex flex-column ph2"
                >
                    <sparkline
                        :title="db.key"
                        :class="pickColor(db.key)"
                        :value="db.value"
                        :timediff="timediff"
                        :specificity="timespan.specificity"
                    ></sparkline>
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
        piData() {
            var l = this.hostsInfo.map(x => x.key)
            return [
                this.hostsInfo.map(x => x.value),
                l,
                l.map(x => this.pickColor(x).slice(3)),
            ]
        },
        isNested() {
            return this.$route.name == 'overview'
        },
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
        pickColor(s) {
            let colors = ['bg-green', 'bg-red', 'bg-purple', 'bg-blue', 'bg-orange']

            if (this.hostsInfo.length > 4) {
                colors.push('bg-gray')
                colors.push('bg-silver')
            }

            let idx = s.split('').reduce((a, x) => a + x.charCodeAt(0), 0) + s.length
            return colors[idx % colors.length]
        },
    },
    mounted() {},
}
</script>
