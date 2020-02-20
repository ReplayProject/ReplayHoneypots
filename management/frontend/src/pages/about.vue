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
    <hr class="o-20 mt4" />
    <div class="flex flex-wrap pt3 nl3 nr3">
      <div class="w-100 w-50-l ph3 mb3 mb0-l">
        <div class="bt bl br b--black-10 br2">
          <div class="pa3 bb b--black-10">
            <h4 class="mv0">Countries</h4>
          </div>
          <metric-list-item
            v-for="(country, index) in countryData"
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
            <h4 class="mv0">Most Visited Pages</h4>
          </div>
          <metric-list-item
            v-for="(page, index) in pageData"
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
      countryData: [
        {
          name: 'United States',
          value: '62.4',
          showBar: true
        },
        {
          name: 'India',
          value: '15',
          showBar: true
        },
        {
          name: 'United Kingdom',
          value: '5',
          showBar: true
        },
        {
          name: 'Canada',
          value: '5',
          showBar: true
        },
        {
          name: 'Russia',
          value: '4.5',
          showBar: true
        },
        {
          name: 'Mexico',
          value: '2.3',
          showBar: true
        },
        {
          name: 'Spain',
          value: '1.7',
          showBar: true
        }
      ],
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
      ]
    }
  }
}
</script>
