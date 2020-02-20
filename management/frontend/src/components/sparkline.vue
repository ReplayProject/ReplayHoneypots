<template>
  <div class="br2">
    <div class="pa3 flex-auto bb b--white-10">
      <h3 class="mt0 mb1 f6 ttu white o-70">{{ title }}</h3>
      <h2 class="mv0 f2 fw5 white">{{ value }}</h2>
    </div>
    <div class="pt2">
      <canvas></canvas>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js'

export default {
  props: ['title', 'value'],
  data () {
    return {
      ctx: null
    }
  },
  mounted () {
    this.ctx = this.$el.querySelector('canvas').getContext('2d')
    let sparklineGradient = this.ctx.createLinearGradient(0, 0, 0, 135)
    sparklineGradient.addColorStop(0, 'rgba(255,255,255,0.35)')
    sparklineGradient.addColorStop(1, 'rgba(255,255,255,0)')

    let data = {
      labels: ['A', 'B', 'C', 'D', 'E', 'F'],
      datasets: [
        {
          backgroundColor: sparklineGradient,
          borderColor: '#FFFFFF',
          data: [2, 4, 6, 4, 8, 10]
        }
      ]
    }

    Chart.Line(this.ctx, {
      data: data,
      options: {
        elements: {
          point: {
            radius: 0
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
