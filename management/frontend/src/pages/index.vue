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
        v-for="db in appRef.dbInfo"
        :key="db.db_name"
        class="w-100 w-50-m w-33-l ph3 tc mb4 mb0-l"
      >
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :labels="['DB Docs', 'Total Docs']"
            :data="[db.doc_count, appRef.totalLogs]"
          ></doughnut>
        </div>
        <h4 class="dark-gray f3 fw3 mv0">{{ db.db_name }}</h4>
        <h3 class="mt2 mb1 f6 fw5 silver">
          Disk Usage:<br />
          <b>{{ db.disk_size / 1000000 }} mb</b>
        </h3>
      </div>
    </div>
    <div class="divide tc relative">
      <h5 class="fw4 ttu mv0 dib bg-white ph3">Quick Stats</h5>
    </div>
    <div class="flex flex-wrap mt3 nl3 nr3">
      <div
        v-for="(db, idx) in appRef.dbInfo"
        :key="db.db_name + '1'"
        class="w-50 w-33-l mb4 mb0-l relative flex flex-column ph3"
      >
        <sparkline
          :title="db.db_name"
          :class="idxToColor(idx)"
          :value="db.doc_count"
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
    idxToColor (i) {
      return i == 0 ? 'bg-green' : i == 1 ? 'bg-red' : 'bg-purple'
    }
  },
  mounted () {
    console.log(this.appRef.dbInfo)
  }
}
</script>
