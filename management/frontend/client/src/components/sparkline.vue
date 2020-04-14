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
import Chart from 'chart.js'

export default {
  props: ['title', 'value', 'calc'],
  data () {
    return {
      dbURI: process.env.DB_URL + '/' + 'aggregate_logs',
      ctx: null
    }
  },
  computed: {
    cLabels () {
      return this.labels || ['A', 'B', 'C', 'D', 'E', 'F']
    },
    cData () {
      return this.data || [2, 4, 6, 4, 8, 10]
    }
  },
  methods: {
    async loadData () {
      this.$Progress.start()

      let fields = ['hostname', 'timestamp']

      // Query index
      let idx = await this.$pouch.createIndex(
        {
          index: { fields }
        },
        this.dbURI
      )
      // Only log index creation if it was new
      if (idx.result != 'exists') {
        console.log('New Index created: ', idx)
        this.$toasted.show('New query index created')
      }

      let dumb = x => parseFloat(Number(x).toPrecision(7))

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
          limit: 400
        },
        this.dbURI
      )
      // Apply local filter or just throw it on the page
      let mine = groupBy(results.docs, 'timestamp')
      // TODO: abstract this date logic from here and the details page
      this.labels = Object.keys(mine).map(x => {
        let s = new Date(x * 1000)
          .toLocaleString()
          .replace('/' + new Date().getFullYear(), '')
        return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
      })

      this.data = Object.values(mine).map(x => x.length)

      // Mark everything as done loading
      this.$Progress.finish()
    }
  },
  async mounted () {
    this.ctx = this.$el.querySelector('canvas').getContext('2d')
    let sparklineGradient = this.ctx.createLinearGradient(0, 0, 0, 135)
    sparklineGradient.addColorStop(0, 'rgba(255,255,255,0.35)')
    sparklineGradient.addColorStop(1, 'rgba(255,255,255,0)')

    try {
      if (this.calc) await this.loadData()
    } catch (error) {
      console.log(error)
    }

    let data = {
      labels: this.cLabels,
      datasets: [
        {
          backgroundColor: sparklineGradient,
          borderColor: '#FFFFFF',
          data: this.cData || [2, 4, 6, 4, 8, 10]
        }
      ]
    }

    Chart.Line(this.ctx, {
      data: data,
      options: {
        elements: {
          point: {
            radius: 3
          }
        },
        scales: {
          xAxes: [
            {
              display: false
            }
          ],
          yAxes: [
            {
              display: false
            }
          ]
        }
      }
    })
  }
}
</script>
