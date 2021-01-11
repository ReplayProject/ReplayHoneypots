<template>
    <!-- This page serves as a template for creating new ones! -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'authGroupsAdd',
            'w-75-l': $route.name != 'authGroupsAdd',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>Add New Auth Group</template>
        </component-title>
        <hr class="o-20" />
        <div class="mt3">
            <label class="db fw6 lh-copy f6" for="name">Name of Auth Group</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="_id"
                v-model="authGroupData._id"
                name="_id"
                id="_id"
                required
            />
        </div>
        <div class="">
            <input
                class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                type="button"
                name="btnAddAuthGroup"
                value="Create Auth Group"
                v-on:click="addAuthGroup()"
                :disabled="!formIsValid"
            />
</template>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import { mapState } from 'vuex'
import api from '../api.js'

export default {
    name: 'authGroupsAdd',
    components: {
        componentTitle,
    },
    data() {
        return {
            authGroupData: {},
        }
    },
    computed: {
        formIsValid: function () {
            if (this.authGroupData._id === undefined || this.authGroupData._id.trim().length === 0) {
                // required fields missing
                return false
            } else {
                // All fields complete
                return true
            }
        },
    },
    methods: {
        /**
         * Updates the auth group object in the database with the contents of the form
         */
        async addAuthGroup() {
            this.$Progress.start()
            try {
                let addResponse = await api.addAuthGroup(this.authGroupData)
                if (addResponse.status !== 200) {
                    console.log("addResponse code was not 200")
                    this.$toasted.show('Failed to add authGroup. Error: addResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Added Auth Group ' + this.authGroupData._id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                    
                    this.$toasted.show('Added New Auth Group')
                    this.$router.push('/authGroups')
                }

            } catch (addError) {
                console.log(addError)
                this.$toasted.show('Failed to add Auth Group. Error: ' + addError.message)
            }
            this.$Progress.finish()
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.authGroupsMgmt !== 2) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
    },
    beforeMount() {
        this.checkPageAccessPermissions()
    },
}
</script>
