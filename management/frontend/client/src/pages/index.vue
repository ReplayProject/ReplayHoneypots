<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>General Stats</component-title>
    <hr class="o-20" />
    <div
      class="flex-m flex-l flex-wrap items-center justify-between nl3 nr3 pt1 mb2"
    >
      <div
        v-if="appRef.hostsInfo"
        style="margin:auto"
        class="w-100 w-50-l w-75-m ph3 tc mb4 mb0-l"
      >
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :chartData="{
              labels: piData[1],
              datasets: [
                {
                  data: piData[0],
                  backgroundColor: piData[2],
                  hoverBackgroundColor: piData[2]
                }
              ]
            }"
          ></doughnut>
        </div>
        <h4 class="dark-gray f3 fw3 mv0">Log Distribution</h4>
        <h3 class="mt2 f6 fw5 silver">
          Disk Usage:<br />
          <b
            >{{
              Number((appRef.aggInfo.sizes.file / 1000000).toPrecision(4))
            }}
            Mb</b
          >
        </h3>
      </div>
      <!-- <div
        v-for="db in appRef.hostsInfo"
        :key="db.key"
        class="w-100 w-50-m w-33-l ph3 tc mb4 mb0-l"
      >
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :chartData="{
              labels: ['DB Docs', 'Total Docs'],
              datasets: [
                {
                  data: [db.value, appRef.totalLogs - db.value],
                  backgroundColor: ['#1BC98E', '#1CA8DD'],
                  hoverBackgroundColor: ['#1BC98E', '#1CA8DD']
                }
              ]
            }"
          ></doughnut>
        </div>
        <h4 class="dark-gray f3 fw3 mv0">{{ db.key }}</h4>
        <h3 class="mt2 mb1 f6 fw5 silver">
          Disk Usage:<br />
          <b
            >{{
              Number(((db.value / appRef.totalLogs) * 100).toPrecision(4))
            }}
            %</b
          >
        </h3>
      </div> -->
    </div>
    <div class="divide tc relative">
      <h5 class="fw4 ttu mv0 dib bg-white ph3">Quick Stats</h5>
    </div>
    <p class="tc center w-100 mv1">
      Total device logs and a time distribution of last
      <b>{{ numLogs }}</b> logs for each device
    </p>

    <div class="flex flex-wrap justify-center">
      <div
        v-for="n in [50, 100, 500]"
        :key="n"
        @click="numLogs = n"
        class="pointer b mv1 mh2 ph4 pv2 br2 ba b--blue blue hover-bg-blue hover-white shadow-hover"
      >
        Analyze Last {{ n }}
      </div>
    </div>

    <div class="flex flex-wrap mt2">
      <div
        v-for="db in appRef.hostsInfo"
        :key="db.key"
        class="w-100 w-50-m w-33-l mb4 mb0-l relative flex flex-column ph3 mv2"
      >
        <sparkline
          :title="db.key"
          :class="pickColor(db.key)"
          :value="db.value"
          :numLogs="numLogs"
        ></sparkline>
      </div>
    </div>
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
import componentTitle from '../components/title'
import doughnut from '../components/doughnut'
import sparkline from '../components/sparkline'

export default {
  name: 'index',
  components: {
    componentTitle,
    doughnut,
    sparkline
  },
  data () {
    return {
      numLogs: 50
    }
  },
  created () {},
  computed: {
    piData () {
      var l = this.appRef.hostsInfo.map(x => x.key)
      return [
        this.appRef.hostsInfo.map(x => x.value),
        l,
        l.map(x => this.pickColor(x).slice(3))
      ]
    },
    isNested () {
      return this.$route.name == 'overview'
    },
    appRef () {
      return this.isNested ? this.$parent.$parent : this.$parent
    }
  },
  methods: {
    pickColor (s) {
      let colors = ['bg-green', 'bg-red', 'bg-purple', 'bg-blue']
      let idx = s.split('').reduce((a, x) => a + x.charCodeAt(0), 0)
      return colors[idx % colors.length]
    }
  },
  mounted () {}
}
</script>
