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
      class="flex-m flex-l flex-wrap items-center justify-between nl3 nr3 pt4 mb4"
    >
      <div
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
      </div>
    </div>
    <div class="divide tc relative">
      <h5 class="fw4 ttu mv0 dib bg-white ph3">Quick Stats</h5>
    </div>
    <p class="tc center w-100">
      Total device logs and a time distribution of last
      <b>{{ numLogs }}</b> logs for each device
    </p>

    <div class="tc center w-100">
      <div
        @click="numLogs = 50"
        class="pointer fw5 mv3 br2 ph3 pv2 dib ba b--blue blue"
      >
        Analyze Last 50
      </div>
      <div
        @click="numLogs = 100"
        class="pointer fw5 mv3 br2 ph3 pv2 dib ba b--blue blue"
      >
        Analyze Last 100
      </div>
      <div
        @click="numLogs = 500"
        class="pointer fw5 mv3 br2 ph3 pv2 dib ba b--blue blue"
      >
        Analyze Last 500
      </div>
    </div>

    <div class="flex flex-wrap mt3 nl3 nr3">
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
