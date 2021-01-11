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
                <template v-slot:pageCategory>Manage</template>
                <template v-slot:pageName>User Details: {{ userData.username }}</template>
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
                    placeholder="unchanged"
                    :disabled="!canChangePassword"
                />
                <label class="db fw6 lh-copy f6" for="onetimepassword">Password Expires Next Login</label>
                <select name="local" id="local" v-model="userData.otp" :value="userData.otp" required>
                    <option v-bind:value="true">True</option>
                    <option v-bind:value="false">False</option>
                </select>
            </div>
            <hr class="o-20" />
            <div class="mt3">
                <h2 class="ttu mt0 mb1 f6 fw5 silver">Role Assignment</h2>
                <select name="roles" id="roles" v-model="userData.role" :value="userData.role" :disabled="!canChangeRole" required>
                    <option v-for="item in rolesData" v-bind:value="item._id" v-bind:key="item._id">
                        {{item._id}}
                    </option>
                </select>
            </div>
            <hr class="o-20" />
            <div class="mt3">
                <h2 class="ttu mt0 mb1 f6 fw5 silver">Local User</h2>
                <select name="localUser" id="local" v-model="userData.local" :value="userData.local" required>
                    <option v-bind:value="true">True</option>
                    <option v-bind:value="false">False</option>
                </select>
            </div>
            <hr class="o-20" />
            <div class="">
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    name="btnUpdateUser"
                    value="Update User"
                    v-on:click="updateUser()"
                    :disabled="!formIsValid || !canUpdateUser"
                />
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    name="btnDeleteUser"
                    value="Delete User"
                    v-on:click="deleteUser()"
                    :disabled="!canDeleteUser"
                />
                <p style="color:red">{{errorMessage}}</p>
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
            rolesData: [],
        }
    },
    computed: {
        canChangePassword: function () {
            if (this.$store.state.userData._id === this.$route.params.user) {
                // Can change own password
                return true
            } else if (this.$store.state.permsData.users === 2 && this.$route.params.user !== "SystemSuperUser") {
                // Can change all other passwords if has write access, except for the super user
                return true
            } else {
                // Can not change other's passwords if does not have write access
                return false
            }
        },
        canChangeRole: function () {
            // console.log(this.$store.state.userData)
            // console.log(this.$route.params)
            if (this.$store.state.userData._id === this.$route.params.user && this.$store.state.userData._id === "SystemSuperUser") {
                // ONLY SUPERUSER CAN CHANGE SUPER'S ROLE
                return true
            } else if (this.$store.state.userData._id === this.$route.params.user) {
                // Cannot change own role
                return false
            } else if(this.$route.params.user !== "SystemSuperUser"){
                return true
            } else {
                return false
            }
        },
        formIsValid: function () {
            if (this.$store.state.userData._id === this.$route.params.user && this.userData.enabled === false) {
                // Cannot disable own account
                return false
            }else if (this.$store.state.userData._id === this.$route.params.user && this.$store.state.userData._id === "SystemSuperUser") {
                // Only superuser can update superuser
                return true
            } else if (this.userData.username && this.userData.firstname && this.userData.lastname && this.$route.params.user !== "SystemSuperUser") {
                // All required fields complete
                return true
            } else {
                // Required fields missing
                return false
            }
        },
        canUpdateUser: function () {
            if (this.$store.state.permsData.users !== 2) {
                return false
            } else {
                return true
            }
        },
        canDeleteUser: function () {
            if (this.$store.state.userData._id === this.$route.params.user || this.$route.params.user === "SystemSuperUser") {
                // Cannot delete own account, or system super user
                return false
            } else if (this.$store.state.permsData.users === 2) {
                // Can delete other accounts if has write access
                return true
            } else {
                // Cannot delete other accounts if does not have write access
                return false
            }
        },
        errorMessage: function () {
            if (!this.formIsValid && this.$route.params.user === "SystemSuperUser") {
                return 'Cannot update super user!'
            } else if (!this.formIsValid) {
                return 'Form is not valid!'
            } else if (this.$store.state.userData._id === this.$route.params.user) {
                return 'Cannot delete your own user!'
            } else if (this.$route.params.user === "SystemSuperUser") {
                return 'Cannot delete the system super user!'
            } else if (this.$store.state.permsData.users !== 2) {
                return 'You do not have write access to users!'
            } else {
                return ''
            }
        }
    },
    methods: {
        /**
         * Updates the user object in the database with the contents of the form
         */
        async updateUser() {
            this.$Progress.start()
            try {
                let updateResponse = await api.updateUser(this.$route.params.user, this.userData)
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
                    this.$toasted.show('Updated User ' + this.$route.params.user)
                    this.$router.push('/users')
                    this.loadItems()
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update user. Error: ' + updateError.message)
                this.loadItems()
            }
            this.$Progress.finish()
        },
        /**
         * Deletes the user object from the database
         */
        async deleteUser() {
            try {
                let deleteResponse = await api.deleteUser(this.$route.params.user)
                if (deleteResponse.status !== 200) {
                    console.log("deleteResponse code was not 200")
                    this.$toasted.show('Failed to delete user. Error: deleteResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Deleted User ' + this.userData.username,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)

                    this.$toasted.show('Deleted User ' + this.$route.params.user)
                    this.$router.push('/users')
                }
            } catch (deleteError) {
                console.log(deleteError)
                this.$toasted.show('Failed to delete user. Error: ' + deleteError.message)
            }
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            // A person with zero level access to users cannot see any page but their own
            if (this.$store.state.permsData.users === 0 && this.$store.state.userData._id !== this.$route.params.user) {
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
                // Get user data
                let userResponse = await api.getUsers(this.$route.params.user)
                this.userData = userResponse.data.docs[0]
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
