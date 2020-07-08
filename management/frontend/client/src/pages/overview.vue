<template>
    <!-- This page shows how we can compose different full views together -->
    <section style="width: 100%;">
        <index> </index>
        <br /><br />
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
        about,
    },
    created() {},
    data() {
        return {}
    },
}
</script>
