<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>Query Panel</component-title>
    <hr class="o-20" />
    <div class="pa4-l">
      <form
        onsubmit="return false;"
        class="bg-light-red mw7 center pa4 br2-ns ba b--black-10"
      >
        <fieldset class="bn ma0 pa0 ">
          <legend class="pa0 f4 f3-ns mb3 black-80">Perform a Query</legend>
          <!-- Select Device -->
          <p class="f4 mb1 w-100 b db fl b">Which device shall I query:</p>
          <label for="device" class="clip">Request Type</label>
          <select
            name="device"
            v-model="device"
            autocomplete="off"
            type="text"
            class="pl2 db fl mw-4 w-40 border-box hover-black  center ba bg-white b--black-20 pa2 br2 mb2"
          >
            <option
              v-for="(db, idx) in $parent.dbInfo"
              :key="idx"
              :value="db.db_name"
            >
              {{ db.db_name }}
            </option>
          </select>

          <!-- Select Field -->
          <p class="f4 mb1 w-100 b db fl b">Which field are we using:</p>
          <label for="log-field" class="clip">Log Field</label>
          <select
            name="log-field"
            v-model="logField"
            autocomplete="off"
            type="text"
            class="pl2 db fl mw-4 w-40 border-box hover-black  center ba bg-white b--black-20 pa2 br2"
          >
            <option
              v-for="(name, idx) in [
                'destIPAddress',
                'destPortNumber',
                'isPortOpen',
                'sourceIPAddress',
                'sourcePortNumber',
                'timestamp',
                'trafficType'
              ]"
              :key="idx"
              :value="name"
            >
              {{ name }}
            </option>
          </select>

          <p class="f4 mb1 w-100 b db fl b">
            Descending Order?

            <label class="clip" for="field-value">Field Value</label>
            <input v-model="desc" type="checkbox" name="desc" />
          </p>

          <p class="f4 mb1 w-100 b db fl b">What should it be:</p>
          <label class="clip" for="field-value">Field Value</label>
          <input
            class="f6 f5-l input-reset bn fl black-80 bg-white pa3 lh-solid w-100 w-75-m w-80-l br2-ns br--left-ns"
            placeholder="Field Value"
            v-model="value"
            type="text"
            name="field-value"
            value=""
            autocomplete="off"
            id="field-value"
          />
          <button
            class="f6 f5-l button-reset fl pv3 tc bn bg-animate bg-black-70 hover-bg-black white pointer w-100 w-25-m w-20-l br2-ns br--right-ns"
            type="submit"
            @click="query()"
          >
            Search
          </button>
        </fieldset>
      </form>
    </div>

    <div class="mv2" v-for="log in logs" :key="log._id">{{ log }}</div>
    <!-- Possibility for differently themed input -->
    <!-- <form class="pa4 black-80">
      <div class="measure">
        <label for="name" class="f6 b db mb2"
          >Name <span class="normal black-60">(optional)</span></label
        >
        <input
          id="name"
          class="input-reset ba b--black-20 pa2 mb2 db w-100"
          type="text"
          aria-describedby="name-desc"
        />
        <small id="name-desc" class="f6 black-60 db mb2"
          >Helper text for the form control.</small
        >
      </div>
    </form> -->
  </main>
</template>

<script>
import componentTitle from '../components/title'

export default {
  name: 'query',
  components: {
    componentTitle
  },
  watch: {
    '$parent.dbInfo': function () {
      if (this.$parent.dbInfo.length != 0)
        this.device = this.$parent.dbInfo[0].db_name
    }
  },
  data () {
    return {
      value: '',
      device: '',
      logField: '',
      desc: '',
      limit: 10,
      logs: []
    }
  },
  methods: {
    castType (value, field) {
      // Turn string into proper type
      let translation = {
        destIPAddress: String,
        destPortNumber: String,
        isPortOpen: x => x == 'true',
        sourceIPAddress: String,
        sourcePortNumber: parseInt,
        timestamp: parseInt,
        trafficType: String
      }

      return translation[field](value)
    },
    async query () {
      let dbURI =
        (this.device == 'aggregate' ? '' : process.env.DB_URL + '/') +
        this.device

      this.$Progress.start()
      let idx = await this.$pouch.createIndex(
        {
          index: {
            fields: [this.logField]
          }
        },
        dbURI
      )

      // Only log index creation if it was new
      if (idx.result != 'exists')
        console.log('New Index created: ', idx, this.logField)

      // Actually do a query
      let fieldSort = {}
      fieldSort[this.logField] = this.desc ? 'desc' : ''
      let sort = [fieldSort]

      let selector = {}

      selector[this.logField] = {
        $eq: this.castType(this.value, this.logField)
      }

      let results = await this.$pouch.find(
        {
          selector,
          sort,
          // skip: this.lower,
          limit: this.limit
        },
        dbURI
      )
      this.logs = results.docs
      console.log(results)
      this.$Progress.finish()
    },
    setData (err, results) {
      if (err) {
        this.error = err.toString()
      } else {
        this.logs.push.apply(this.logs, results.docs)
      }
    }
  }
}
</script>
