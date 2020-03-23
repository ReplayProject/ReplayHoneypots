<template>
  <canvas></canvas>
</template>

<script>
import Chart from 'chart.js'

export default {
  props: ['data', 'labels'],
  data () {
    return {
      ctx: null
    }
  },
  mounted () {
    let self = this
    this.ctx = this.$el.getContext('2d')

    new Chart(this.ctx, {
      type: 'doughnut',
      options: {
        cutoutPercentage: 80
      },
      data: {
        labels: self.labels,
        datasets: [
          {
            data: self.data,
            backgroundColor: ['#1BC98E', '#1CA8DD'],
            hoverBackgroundColor: ['#1BC98E', '#1CA8DD']
          }
        ]
      }
    })
  }
}
</script>
