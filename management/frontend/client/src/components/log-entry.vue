<template>
  <table>
    <tr>
      <th>Month</th>
      <th>Savings</th>
    </tr>
    <tr>
      <td>January</td>
      <td>$100</td>
    </tr>
  </table>

  <!-- <a
    href="#"
    class="link dark-gray flex justify-between relative pa3 bb b--black-10 hover-bg-near-white"
  >
    <span
      v-if="showBar"
      class="absolute top-0 left-0 right-0 bottom-0 h-100 bg-near-white"
      v-bind:style="{ width: barWidth, zIndex: -1 }"
    ></span> -->

  <!--
  "sourcePortNumber": 443,
  "sourceIPAddress": "152.1.0.44",
  "destPortNumber": 44516,
  "destIPAddress": "192.168.42.51",
  "timestamp": 1582307832,
  "trafficType": "TCP",
  "isPortOpen": false,
 -->

  <!-- <span>{{ entry.id }}</span>
    <span>{{
      entry.doc.destIPAddress +
        ':' +
        entry.doc.destPortNumber +
        '  -  ' +
        entry.doc.timestamp
    }}</span>
  </a> -->
</template>

<script>
export default {
  props: ['entry', 'showBar'],
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
