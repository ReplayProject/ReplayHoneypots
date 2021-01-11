<template>
    <!-- This page serves as a template for creating new ones! -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <section
            v-if="!userData"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <component-title>
                <template v-slot:pageCategory>Security</template>
                <template v-slot:pageName>Password for {{ userData.username }} has Expired</template>
            </component-title>
            <hr class="o-20" />
            <div class="mt3">
                <label class="db fw6 lh-copy f6" for="password">Password</label>
                <input
                    class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                    type="password"
                    v-model="userData.password"
                    name="password"
                    id="password"
                    placeholder="unchanged"
                />
            </div>
            <hr class="o-20" />
            <div class="">
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Update Password"
                    v-on:click="updateUser()"
                    :disabled="!formIsValid"
                />
            </div>
        </section>
            
</template>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import { mapState } from 'vuex'
import api from '../api.js'

export default {
    name: 'userDetails',
    components: {
        componentTitle,
    },
    data() {
        return {
            userData: null,
        }
    },
    computed: {
        formIsValid: function () {
            if (this.userData.username != undefined && this.userData != '') {
                // All required fields complete
                return true
            } else {
                // Required fields missing
                return false
            }
        },
    },
    methods: {
        /**
         * Updates the user object in the database with the contents of the form
         */
        async updateUser() {
            this.$Progress.start()
            try {
                // Reset password expiration flag
                this.userData.otp = false
                let updateResponse = await api.updateUser(this.userData._id, this.userData)
                if (updateResponse.status !== 200) {
                    console.log("updateResponse code was not 200")
                    this.$toasted.show('Failed to update user. Error: updateResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Updated User ' + this.userData.username,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)

                    this.$toasted.show('Updated User ' + this.userData.username)
                    this.$router.push('/')
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update user. Error: ' + updateError.message)
                this.loadItems()
            }
            this.$Progress.finish()
        },
        /**
         * load items is what brings back the rows from server
         */
        async loadItems() {
            this.$Progress.start()
            this.isLoading = true

            // Get user data from the store
            this.userData = this.$store.state.userData

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
    },
    beforeMount() {
        this.loadItems()
    },
}
</script>
