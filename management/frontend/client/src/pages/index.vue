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
    <section
      v-if="Object.keys(hostsInfo).length == 0"
      class="mw1 center mt6 mt6-ns"
    >
      <PropagateLoader :size="20" color="#387ddb" />
    </section>
    <section v-else>
      <div
        class="flex-m flex-l flex-wrap items-center justify-between nl3 nr3 pt1 mb2"
      >
        <div
          v-if="hostsInfo"
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
                Number(
                  ($store.state.aggInfo.sizes.file / 1000000).toPrecision(4)
                )
              }}
              Mb</b
            >
          </h3>
        </div>
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
          v-for="db in hostsInfo"
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
    sparkline
  },
  data () {
    return {
      numLogs: 50
    }
  },
  computed: {
    ...mapState(['hostsInfo']),
    piData () {
      var l = this.hostsInfo.map(x => x.key)
      return [
        this.hostsInfo.map(x => x.value),
        l,
        l.map(x => this.pickColor(x).slice(3))
      ]
    },
    isNested () {
      return this.$route.name == 'overview'
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
