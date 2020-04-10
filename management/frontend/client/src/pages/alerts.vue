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
    <section class="ph2 pv2">
      <article class="mw8 center br2 ba b--light-blue bg-lightest-blue">
        <div class="dt-ns dt--fixed-ns w-100">
          <div class="pa3 pa4-ns dtc-ns v-mid">
            <div>
              <h2 class="fw4 blue mt0 mb3">Sample Alert</h2>
              <p class="black-70 measure lh-copy mv0">
                🤷 You hate to see it 🤷
              </p>
            </div>
          </div>
          <div class="pa3 pa4-ns dtc-ns v-mid">
            <a
              href="https://www.youtube.com/watch?v=oHg5SJYRHA0"
              class="no-underline f6 tc db w-100 pv3 bg-animate bg-blue hover-bg-dark-blue white br2"
              >Fix it!</a
            >
          </div>
        </div>
      </article>
    </section>

    <ul class="list pl0 mt0 measure center">
      <li
        v-for="(a, idx) in alerts"
        :key="idx"
        class="flex items-center lh-copy pa3 ph0-l bb b--black-10"
      >
        <img class="w2 h2 w3-ns h3-ns br-100" :src="a.img" />
        <div class="pl3 flex-auto">
          <span class="f6 db black-70">{{ a.name }}</span>
          <span class="f6 db black-70">{{ a.company }}</span>
        </div>
        <div>
          <a href="tel:" class="f6 link blue hover-dark-gray">{{ a.phone }}</a>
        </div>
      </li>
    </ul>
  </main>
</template>

<script>
import componentTitle from '../components/title'

export default {
  name: 'alerts',
  components: {
    componentTitle
  },

  data () {
    return {
      alerts: [
        {
          img: 'http://tachyons.io/img/avatar-mrmrs.jpg',
          phone: '+1 (999) 555-5555',
          name: 'Mrmrs',
          company: 'Medium Hexagon, LLC'
        },
        {
          img: 'http://tachyons.io/img/avatar-jxnblk.jpg',
          phone: '+1 (999) 555-5555',
          name: 'Jxnblk',
          company: 'Large Circle, Inc'
        },
        {
          img: 'http://tachyons.io/img/avatar-jasonli.jpg',
          phone: '+1 (999) 555-5555',
          name: 'Jason Li',
          company: 'Little Blue Square, Inc'
        },
        {
          img: 'http://tachyons.io/img/avatar-yavor.jpg',
          phone: '+1 (999) 555-5555',
          name: 'Yavor',
          company: 'Large Circle, Inc'
        }
      ]
    }
  }
}
</script>
