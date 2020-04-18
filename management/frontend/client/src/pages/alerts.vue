<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>Alerts</component-title>
    <hr class="o-20" />
    <section class="ph2 pt2">
      <p class="ma3 pa2 i tc w-100">
        click on the "{...}" to expand the log and click on the references to
        open them in a new tab
      </p>
      <!-- Choices -->
      <div class="flex flex-auto justify-center pa2 mh2">
        <div
          v-for="n in [10, 20, 100, null]"
          :key="n"
          @click="numAlerts = n"
          class="pointer b mv3 br2 ph4 pv2 mh2 ba b--blue blue hover-bg-blue hover-white shadow-hover"
        >
          {{ n > 0 ? 'Last ' + n : 'All' }}
        </div>
      </div>
    </section>

    <!-- List of alerts -->
    <ul class="list pl0 mt0 measure center">
      <li
        v-for="(a, idx) in $store.state.alerts"
        :key="idx"
        class="alert cf items-center lh-copy pa3 ph0-l bb b--black-20"
      >
        <!-- container for icon and desc -->
        <div class="w-80 flex fl">
          <img class="w2 h2 w3-ns h3-ns br2" :src="variantMap[a.variant]" />
          <div class="w-auto pl3">
            <span class="f6 db black">{{ a.message }}</span>
            <span class="f6 db black-60 i">{{
              $parseDateWithTime(a.timestamp)
            }}</span>
          </div>
        </div>
        <!-- Link / Hostname -->
        <router-link
          :to="'/details/' + a.hostname"
          class="w-20 fr tr f4 link blue hover-dark-gray hover-shadow"
          >{{ a.hostname }}</router-link
        >
        <!-- Pretty JSON -->
        <vue-json-pretty
          class="fl mt2 pa3 w-100 shadow-hover"
          style="background:#f4f4f470;"
          showLength
          showLine
          highlightMouseoverNode
          :showSelectController="false"
          :showDoubleQuotes="false"
          :deep="0"
          :path="''"
          :data="a"
          @click="jsonClick"
        />
      </li>
    </ul>
  </main>
</template>

<script>
import componentTitle from '../components/title'
import VueJsonPretty from 'vue-json-pretty'

export default {
  name: 'alerts',
  components: {
    componentTitle,
    VueJsonPretty
  },
  data () {
    return {
      numAlerts: 10,
      variantMap: {
        admin:
          'data:image/png;base64,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',
        meta:
          'data:image/png;base64,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',
        alert:
          'data:image/png;base64,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'
      }
    }
  },
  watch: {
    numAlerts: function () {
      this.loadData()
    }
  },
  methods: {
    jsonClick (path, data) {
      // console.log(path, data)
      if (path.includes('.references[') && data.length != 0) {
        console.log('User clicked on a valid reference')
        window.open(this.dbURI + '/' + data)
      }
    },
    async loadData () {
      this.$Progress.start()

      let fields = ['timestamp']

      // Query index
      let idx = await this.$pouch.createIndex(
        {
          index: { fields }
        },
        this.alertsURI
      )
      // Only log index creation if it was new
      if (idx.result != 'exists') {
        console.log('New Index created: ', idx)
        this.$toasted.show('New query index created')
      }

      let options = {
        selector: {},
        sort: [{ timestamp: 'desc' }],
        skip: 0,
        fields: []
      }

      if (this.numAlerts > 0) options.limit = this.numAlerts

      // Actually do a query
      let results = await this.$pouch.find(options, this.alertsURI)
      this.$store.commit('setAlerts', results.docs)
      this.$Progress.finish()
    }
  },
  async mounted () {
    this.loadData()

    var changes = this.$pouch.changes(
      {
        since: 'now',
        live: true,
        include_docs: true
      },
      this.alertsURI
    )

    changes.on('change', change => {
      if (!change.deleted) {
        this.$store.commit('unshiftList', change.doc)
        this.$store.commit('popAlerts') // remove element to keep number the same
        this.$toasted.show('New alert from ' + change.doc.hostname)
      }
    })

    changes.on('complete', info => {
      console.log('complete', info)
    })

    changes.on('error', err => {
      console.log(err)
    })
  }
}
</script>
