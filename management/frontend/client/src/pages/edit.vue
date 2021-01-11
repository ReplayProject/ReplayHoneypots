<template>
    <!-- This page serves as a template for creating new ones! -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>Edit</template>
        </component-title>
        <hr class="o-20" />
        <p>A gloriusly blank edit page!</p>
    </main>
</template>

<script>
import componentTitle from '../components/title'

export default {
    name: 'edit',
    components: {
        componentTitle,
    },
}
</script>
