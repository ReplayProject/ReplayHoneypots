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
      <div class="w-100 w-50-m w-33-l ph3 tc mb4 mb0-l">
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :labels="newVsReturning.labels"
            :data="newVsReturning.data"
          ></doughnut>
        </div>
        <h3 class="mt3 mb1 f6 fw5 silver">Traffic</h3>
        <h4 class="dark-gray f3 fw3 mv0">New vs. Returning</h4>
      </div>
      <div class="w-100 w-50-m w-33-l ph3 tc mb4 mb0-l">
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :labels="newVsRecurring.labels"
            :data="newVsRecurring.data"
          ></doughnut>
        </div>
        <h3 class="mt3 mb1 f6 fw5 silver">Revenue</h3>
        <h4 class="dark-gray f3 fw3 mv0">New vs. Recurring</h4>
      </div>
      <div class="w-100 w-50-m w-33-l ph3 tc mb4 mb0-l">
        <div class="w-50 w-50-m w-75-l center">
          <doughnut
            :labels="directVsReferrals.labels"
            :data="directVsReferrals.data"
          ></doughnut>
        </div>
        <h3 class="mt3 mb1 f6 fw5 silver">Traffic</h3>
        <h4 class="dark-gray f3 fw3 mv0">Direct vs. Referral</h4>
      </div>
    </div>
    <div class="divide tc relative">
      <h5 class="fw4 ttu mv0 dib bg-white ph3">Quick Stats</h5>
    </div>
    <div class="flex flex-wrap mt3 nl3 nr3">
      <div class="w-50 w-25-l mb4 mb0-l relative flex flex-column ph3">
        <sparkline
          title="Page Views"
          class="bg-green"
          value="1,293"
        ></sparkline>
      </div>
      <div class="w-50 w-25-l mb4 mb0-l relative flex flex-column ph3">
        <sparkline title="Downloads" class="bg-red" value="758"></sparkline>
      </div>
      <div class="w-50 w-25-l mb4 mb0-l relative flex flex-column ph3">
        <sparkline title="Sign-Ups" class="bg-purple" value="1,293"></sparkline>
      </div>
      <div class="w-50 w-25-l mb4 mb0-l relative flex flex-column ph3">
        <sparkline title="Downloads" class="bg-blue" value="758"></sparkline>
      </div>
    </div>
  </main>
</template>

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
  data () {
    return {
      newVsReturning: {
        data: [130, 230],
        labels: ['New', 'Returning']
      },
      newVsRecurring: {
        data: [30, 330],
        labels: ['New', 'Recurring']
      },
      directVsReferrals: {
        data: [260, 160],
        labels: ['Direct', 'Referrals']
      }
    }
  }
}
</script>
