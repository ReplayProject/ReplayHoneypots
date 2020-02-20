<template>
  <a
    href="#"
    class="link dark-gray flex justify-between relative pa3 bb b--black-10 hover-bg-near-white"
  >
    <span
      v-if="showBar"
      class="absolute top-0 left-0 right-0 bottom-0 h-100 bg-near-white"
      v-bind:style="{ width: barWidth, zIndex: -1 }"
    ></span>
    <span>{{ name }}</span>
    <span>{{ value }}</span>
  </a>
</template>

<script>
export default {
  props: ['name', 'value', 'showBar'],
  data () {
    return {
      ctx: null
    }
  },
  computed: {
    barWidth: function () {
      return `${this.value}%`
    }
  }
}
</script>
