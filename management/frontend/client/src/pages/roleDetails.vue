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
            v-if="!roleData"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <component-title>
                <template v-slot:pageCategory>Manage</template>
                <template v-slot:pageName>Role Details: {{ roleData._id }}</template>
            </component-title>
            <hr class="o-20" />
            <div class="mt3">
                <div class="mt3">
                    <h2 class="ttu mt0 mb1 f6 fw5 silver">Basic Permissions</h2>
                    <label class="db fw6 lh-copy f6" for="users">Users</label>
                    <select name="users" id="local" v-model="roleData.users" :value="roleData.users" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="users">Roles</label>
                    <select name="roles" id="local" v-model="roleData.roles" :value="roleData.roles" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 
                
                    <label class="db fw6 lh-copy f6" for="adminLogs">Admin Logs</label>
                    <select name="adminlogs" id="local" v-model="roleData.adminLogs" :value="roleData.adminLogs" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="trafficLogs">Traffic Logs</label>
                    <select name="trafflogs" id="local" v-model="roleData.traffLogs" :value="roleData.traffLogs" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="devices">Devices</label>
                    <select name="devices" id="local" v-model="roleData.devices" :value="roleData.devices" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="metrics">Metrics</label>
                    <select name="metrics" id="local" v-model="roleData.metrics" :value="roleData.metrics" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="authGroupsMgmt">Auth Groups Management</label>
                    <select name="authGroupsMgmt" id="local" v-model="roleData.authGroupsMgmt" :value="roleData.authGroupsMgmt" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select>

                    <label class="db fw6 lh-copy f6" for="alerts">Alerts</label>
                    <select name="alerts" id="local" v-model="roleData.alerts" :value="roleData.alerts" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 

                    <label class="db fw6 lh-copy f6" for="configs">Configs</label>
                    <select name="configs" id="local" v-model="roleData.configs" :value="roleData.configs" required>
                        <option v-bind:value="0">None</option>
                        <option v-bind:value="1">Read</option>
                        <option v-bind:value="2">Write</option>
                    </select> 
                </div>
        
                <hr class="o-20" />
                <div class="mt3">
                    <h2 class="ttu mt0 mb1 f6 fw5 silver">Auth Groups Permissions</h2>
                    <div class="mv3 w-100">Select Auth Groups</div>
                    <div class="mv3 w-100">
                        <select name="authGroupSelect" id="local" v-model="selectedAuthGroup" :value="selectedAuthGroup"> 
                            <option v-for="authGroup in authGroups" :value="authGroup._id" :key="authGroup._id">{{authGroup._id}} </option>
                        </select>
                </div>
            
                <label class="db fw6 lh-copy f6" for="authAccessLevel">Auth Group Access Level</label>
                <select name="authGroupAccess" id="local" v-model="authAccessLevel" :value="authAccessLevel">
                    <option v-bind:value="0">None</option>
                    <option v-bind:value="1">Read</option>
                    <option v-bind:value="2">Write</option>
                </select>

                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Add Auth Group"
                    name="btnAddAuthGroup"
                    v-on:click="addAuthGroup()"
                    :disabled="!authIsValid"
                /> 
                <div class="mv3 w-100">
                    <vue-good-table
                        ref="datatable"
                        mode="remote"
                        :isLoading.sync="isLoading"
                        :columns="columns"
                        :totalRows="totalRoles"
                        :rows="rows"
                        :fixed-header="false"
                        :line-numbers="false"
                        theme="default"
                    >
                        <template slot="table-row" slot-scope="props">
                            <span v-if="props.column.field == 'btn'">
                                <button class="btn" @click="deleteAuthGroup(props.row._id)">Delete</button>
                            </span>
                            <span v-else>
                                {{props.formattedRow[props.column.field]}}
                            </span>
                        </template>
                    </vue-good-table>
                    <hr class="o-20" />
                    <div class="">
                        <input
                            class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                        type="button"
                        value="Update Role"
                        name="btnUpdateRole"
                        v-on:click="updateRole()"
                        :disabled="!formIsValid || !canModifyRole"
                        />
                        <input
                            class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                            type="button"
                            value="Delete Role"
                            name="btnDeleteRole"
                            v-on:click="deleteRole()"
                            :disabled="!canModifyRole"
                        />
                        <p style="color:red">{{errorMessage}}</p>
                    </div>
                </div>
            </div>
        </section>
            
</template>

<script>
import { PropagateLoader } from '@saeris/vue-spinners'
import componentTitle from '../components/title'
import { mapState } from 'vuex'
import api from '../api.js'

export default {
    name: 'editRole',
    components: {
        componentTitle,
    },
    data() {
        return {
            isLoading: false,
            authAccessLevel: 0,
            selectedAuthGroup: '',
            authGroups: [], 
            roleData: {
                authGroupsList: [],
            },
            columns: [
                {
                    label: 'Unique ID',
                    field: '_id',
                    type: 'text',
                    hidden: true,
                },
                {
                    label: 'Name of Auth Group',
                    field: 'id',
                    type: 'text',
                },
                {
                    label: 'Access',
                    field: 'access',
                    type: 'text',
                },
                {
                    label: 'Delete',
                    field: 'btn',
                    html: true,
                },
            ],
            rows: [],
        }
    },
    computed: {
        authIsValid: function () {
            if (this.authAccessLevel == undefined || this.selectedAuthGroup == undefined || this.selectedAuthGroup == '') {
                return false 
            } else  {
                return true
            }
        },
        formIsValid: function () {
            if (this.roleData._id == undefined || this.roleData._id.trim().length === 0 ||
                this.roleData.users == undefined || this.roleData.roles == undefined ||
                this.roleData.adminLogs == undefined || this.roleData.traffLogs == undefined ||
                this.roleData.devices == undefined || this.roleData.authGroupsMgmt == undefined ||
                this.roleData.configs == undefined || this.roleData.authGroupsList == undefined ||
                this.roleData.metrics == undefined || this.roleData.alerts == undefined) {
                // required fields missing
                return false
            } else {
                // All fields complete
                return true
            }
        },
        canModifyRole: function () {
            if (this.$store.state.permsData._id === this.$route.params.role && this.$store.state.permsData._id !== "superUser") {
                return false
            } else if (this.$store.state.permsData._id === this.$route.params.role && this.$store.state.permsData._id === "superUser") {
                return true
            } else if (this.$store.state.permsData.roles === 2 && this.$route.params.role !== "superUser") {
                return true
            } else {
                return false
            }
        },
        errorMessage: function () {
            if (this.$store.state.permsData._id === this.$route.params.role && this.$store.state.permsData._id !== "superUser" ) {
                return 'Cannot modify or delete your own role!'
            } else if (this.$store.state.permsData._id !== "superUser" && this.$route.params.role === "superUser") {
                return "Cannot modify or delete super user"
            }  
            else {
                return ''
            }
        }
    },
    methods: {
        /**
         * Updates the Role object in the database with the contents of the form
         */
        async updateRole() {
            this.$Progress.start()
            try {
                let updateResponse = await api.updateRole(this.$route.params.role, this.roleData)
                if (updateResponse.status !== 200) {
                    console.log("updateResponse code was not 200")
                    this.$toasted.show('Failed to update Role. Error: updateResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Updated Role' + this.roleData._id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)

                    this.$toasted.show('Updated Role ' + this.roleData._id)
                    this.$router.push('/roles')
                
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update Role. Error: ' + updateError.message)

            }
            this.$Progress.finish()
        },
        /**
         * Deletes the role object from the database
         */
        async deleteRole() {
            try {
                let deleteResponse = await api.deleteRole(this.roleData._id)
                if (deleteResponse.status !== 200) {
                    console.log("deleteResponse code was not 200")
                    this.$toasted.show('Failed to delete Role. Error: deleteResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Deleted Role ' + this.roleData._id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)

                    this.$toasted.show('Deleted Role ' + this.roleData._id)
                    this.$router.push('/roles')
                }
            } catch (deleteError) {
                console.log(deleteError)
                this.$toasted.show('Failed to delete role. Error: ' + deleteError.message)
            }
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.roles === 0) {
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
                // Get role data
                let roleResponse = await api.getRoles(this.$route.params.role)
                this.roleData = roleResponse.data.docs[0]
                this.rows = this.roleData.authGroupsList

                //Get auth Groups
                let results = await api.getAuthGroups()
                this.authGroups = results.data.docs

            } catch (err) {
                console.log(err)
            }

            // Mark everything as done loading
            this.$Progress.finish()
            this.isLoading = false
        },
        addAuthGroup() {
            this.roleData.authGroupsList.push({id: this.selectedAuthGroup, access: this.authAccessLevel })
            this.rows = this.roleData.authGroupsList
            this.selectedAuthGroup = ''
            this.authAccessLevel = 0
        },
        deleteAuthGroup(_id) {
            this.roleData.authGroupsList.splice(_id, 1)
            this.rows = this.roleData.authGroupsList
        }
    },
    beforeMount() {
        this.checkPageAccessPermissions()
        this.loadItems()
    },
}
</script>
