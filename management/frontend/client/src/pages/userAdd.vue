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
            <template v-slot:pageName>Add New User</template>
        </component-title>
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Enabled</h2>
            <select name="localEnabled" id="local" v-model="userData.enabled" :value="userData.enabled" required>
                <option v-bind:value="true">True</option>
                <option v-bind:value="false">False</option>
            </select> 
        </div>
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Basic User Data</h2>
            <label class="db fw6 lh-copy f6" for="username">Username</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="username"
                v-model="userData.username"
                name="username"
                id="username"
                required
            />
            <label class="db fw6 lh-copy f6" for="firstname">First Name</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="text"
                v-model="userData.firstname"
                name="firstname"
                id="firstname"
                required
            />
            <label class="db fw6 lh-copy f6" for="lastname">Last Name</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="text"
                v-model="userData.lastname"
                name="lastname"
                id="lastname"
                required
            />
        </div>
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Authentication</h2>
            <label class="db fw6 lh-copy f6" for="password">Password</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="password"
                v-model="userData.password"
                name="password"
                id="password"
                required
            />
            <label class="db fw6 lh-copy f6" for="onetimepassword">Password Expires Next Login</label>
            <select name="onetimepassword" id="local" v-model="userData.otp" :value="userData.otp" required>
                <option v-bind:value="true">True</option>
                <option v-bind:value="false">False</option>
            </select>
        </div>
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Role Assignment</h2>
            <select name="roles" id="roles" v-model="userData.role" :value="userData.role" required>
                <option v-for="item in rolesData" v-bind:value="item._id" v-bind:key="item._id">
                    {{item._id}}
                </option>
            </select>
        </div>
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Local User</h2>
            <select name="local" id="local" v-model="userData.local" :value="userData.local" required>
                <option value="true">True</option>
                <option value="false">False</option>
            </select>
        </div>
        <hr class="o-20" />
        <div class="">
            <input
                class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                type="button"
                value="Create User"
                name="addUser"
                v-on:click="addUser()"
                :disabled="!formIsValid"
            />
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
            userData: {},
            rolesData: [],
        }
    },
    computed: {
        formIsValid: function () {
            if (this.userData.username == undefined || this.userData.username.trim().length === 0 ||
                this.userData.password == undefined || this.userData.password.trim().length === 0 ||
                this.userData.firstname == undefined || this.userData.firstname.trim().length === 0 ||
                this.userData.lastname == undefined || this.userData.lastname.trim().length === 0 ||
                this.userData.local == undefined || this.userData.enabled == undefined || 
                this.userData.role == undefined || this.userData.otp == undefined) {
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
         * Updates the user object in the database with the contents of the form
         */
        async addUser() {
            this.$Progress.start()
            try {
                let addResponse = await api.addUser(this.userData)
                if (addResponse.status !== 200) {
                    console.log("addResponse code was not 200")
                    this.$toasted.show('Failed to add user. Error: addResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Added new User ' + this.userData.username,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                    this.$toasted.show('Added New User')
                    this.$router.push('/users')
                    this.loadItems()
                }
            } catch (addError) {
                console.log(addError)
                this.$toasted.show('Failed to add user. Error: ' + addError.message)
                this.loadItems()
            }
            this.$Progress.finish()
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.users === 0) {
                this.$toasted.show('Invalid Page Access Detected. Redirecting.')
                this.$router.push('/')
            }
        },
        /**
         * load items is what brings back the rows from server
         */
        async loadItems() {
            this.$Progress.start()
            this.isLoading = true

            try {
                // Zero the userData
                this.userData = {}
                // Get roles data
                let rolesResponse = await api.getRoles(undefined, undefined, undefined, ["_id", "admin"], undefined)
                this.rolesData = rolesResponse.data.docs
            } catch (err) {
                console.log(err)
            }

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
    },
    beforeMount() {
        this.checkPageAccessPermissions()
        this.loadItems()
    },
}
</script>
