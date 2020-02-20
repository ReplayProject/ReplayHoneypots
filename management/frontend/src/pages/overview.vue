<template>
  <section style="width:100%">
    <index> </index>
    <about> </about>
  </section>
</template>

<script>
import index from './index'
import about from './about'

export default {
  name: 'overview',
  components: {
    index,
    about
  },
  created () {},
  data () {
    return {}
  }
}
</script>
