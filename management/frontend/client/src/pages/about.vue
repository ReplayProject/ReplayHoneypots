<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>At a Glance</component-title>
    <hr class="o-20" />
    <div class="divide tc relative mv4">
      <h5 class="fw4 ttu mv0 dib bg-white ph3">Fake Data</h5>
    </div>
    <hr class="o-20 mt4" />
    <div class="flex flex-wrap pt3 nl3 nr3">
      <div class="w-100 w-50-l ph3 mb3 mb0-l">
        <div class="bt bl br b--black-10 br2">
          <div class="pa3 bb b--black-10">
            <h4 class="mv0">Source IP Frequency</h4>
          </div>
          <metric-list-item
            v-for="(country, index) in srcIPData"
            :key="index"
            :show-bar="country.showBar"
            :name="country.name"
            :value="country.value"
          >
          </metric-list-item>
        </div>
        <a
          href="#"
          class="no-underline fw5 mt3 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
          >All Countries</a
        >
      </div>
      <div class="w-100 w-50-l ph3 mb3 mb0-l">
        <div class="bt bl br b--black-10 br2">
          <div class="pa3 bb b--black-10">
            <h4 class="mv0">Destination IP Frequency</h4>
          </div>
          <metric-list-item
            v-for="(page, index) in destIPData"
            :key="index"
            :show-bar="page.showBar"
            :name="page.name"
            :value="page.value"
          >
          </metric-list-item>
        </div>
        <a
          href="#"
          class="no-underline fw5 mt3 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
          >All Pages</a
        >
      </div>
    </div>
    <div class="mt4">
      <div class="w-100 mb3 mb0-l">
        <div class="bt bl br b--black-10 br2">
          <div class="pa3 bb b--black-10">
            <h4 class="mv0">Devices and Resolutions</h4>
          </div>
          <metric-list-item
            v-for="(device, index) in deviceData"
            :key="index"
            :show-bar="device.showBar"
            :name="device.name"
            :value="device.value"
          >
          </metric-list-item>
        </div>
        <a
          href="#"
          class="no-underline fw5 mt3 br2 ph3 pv2 dib ba b--blue blue bg-white hover-bg-blue hover-white"
          >All Devices</a
        >
      </div>
    </div>
  </main>
</template>

<script>
import componentTitle from '../components/title'
import metricListItem from '../components/metric-list-item'

export default {
  name: 'about',
  components: {
    componentTitle,
    metricListItem
  },
  data () {
    return {
      dbURI: process.env.DB_URL + '/' + 'aggregate_logs',
      data: null,
      pageData: [
        {
          name: '/ (Logged out)',
          value: '3,929,481',
          showBar: false
        },

        {
          name: '/ (Logged in)',
          value: '1,143,393',
          showBar: false
        },

        {
          name: '/tour',
          value: '938,287',
          showBar: false
        },

        {
          name: '/features/something',
          value: '749,393',
          showBar: false
        },

        {
          name: '/features/another-thing',
          value: '695,912',
          showBar: false
        },

        {
          name: '/users/username',
          value: '501,938',
          showBar: false
        },

        {
          name: '/page-title',
          value: '392,842',
          showBar: false
        }
      ],
      deviceData: [
        {
          name: 'Desktop (1920x1080)',
          value: '3,929,481',
          showBar: false
        },

        {
          name: 'Desktop (1366x768)',
          value: '1,143,393',
          showBar: false
        },

        {
          name: 'Desktop (1440x900)',
          value: '938,287',
          showBar: false
        },

        {
          name: 'Desktop (1280x800)',
          value: '749,393',
          showBar: false
        },

        {
          name: 'Tablet (1024x768)',
          value: '695,912',
          showBar: false
        },

        {
          name: 'Tablet (768x1024)',
          value: '501,938',
          showBar: false
        },

        {
          name: 'Phone (320x480)',
          value: '392,842',
          showBar: false
        },

        {
          name: 'Phone (720x450)',
          value: '298,183',
          showBar: false
        },

        {
          name: 'Desktop (2560x1080)',
          value: '193,129',
          showBar: false
        },

        {
          name: 'Desktop (2560x1600)',
          value: '93,382',
          showBar: false
        }
      ],
      logs: null,
      error: null
    }
  },
  computed: {
    srcIPData () {
      if (!this.data) return []

      var groupBy = (xs, key) =>
        xs.reduce((rv, x) => {
          ;(rv[x[key]] = rv[x[key]] || []).push(x)
          return rv
        }, {})

      /*
      destIPAddress: (...)
      destMAC: (...)
      destPortNumber: (...)
      hostname: (...)
      isPortOpen: (...)
      sourceIPAddress: (...)
      sourceMAC: (...)
      sourcePortNumber: (...)
      timestamp: (...)
      trafficType: (...)
      */
      let stats = groupBy(this.data, 'sourceIPAddress')

      /*
      {
        name: 'United States',
        value: '62.4',
        showBar: true
      }
      */
      let displayObj = Object.keys(stats).map(x => {
        return {
          name: x,
          value: stats[x].length,
          showBar: true
        }
      })

      return displayObj.sort((a, b) => b.value - a.value)
    },
    destIPData () {
      if (!this.data) return []

      return {
        name: 'United Gatesssss',
        value: '62.4',
        showBar: true
      }
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

      let selector = {
        /*hostname: { $eq: this.title }*/
      }
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
      // // Apply local filter or just throw it on the page
      // let mine = groupBy(results.docs, 'timestamp')
      // // TODO: abstract this date logic from here and the details page
      // this.labels = Object.keys(mine).map(x => {
      //   let s = new Date(x * 1000)
      //     .toLocaleString()
      //     .replace('/' + new Date().getFullYear(), '')
      //   return s.slice(0, s.indexOf(':', 9) + 3) + ' ' + s.split(' ')[2]
      // })

      // this.data = Object.values(mine).map(x => x.length)

      // Lets do something with this data
      this.data = results.docs
      // Mark everything as done loading
      this.$Progress.finish()
    },
    setData (err, logs) {
      if (err) {
        this.error = err.toString()
      } else {
        this.logs = logs
      }
    }
  },
  async mounted () {
    try {
      await this.loadData()
    } catch (error) {
      console.log(error)
    }
  }
}
</script>
