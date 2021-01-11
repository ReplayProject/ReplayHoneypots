<template>
    <!-- This page serves as a template for creating new ones! -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'configs',
            'w-75-l': $route.name != 'configs',
        }"
    >
        <section
            v-if="!configData"
            class="mw1 center mt6 mt6-ns"
        >
            <PropagateLoader :size="20" color="#387ddb" />
        </section>
        <section v-else>
            <component-title>
                <template v-slot:pageCategory>Manage</template>
                <template v-slot:pageName>{{ configData._id }}</template>
            </component-title>
            <hr class="o-20" />
            <div class="mt3">
                <h2 class="ttu mt0 mb1 f6 fw5 silver"></h2>
                <label class="db fw6 lh-copy f6" for="config">Config JSON</label>
                <textarea
                    class="pa2 input-reset ba bg-transparent w-100"
                    rows="20"
                    v-model="configData"
                    name="config"
                    id="config"
                    required
                ></textarea>
            </div>
            <hr class="o-20" />
            <div class="">
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Update Config"
                    v-on:click="updateConfig()"
                    :disabled="!formIsValid || !canUpdateConfig"
                />
                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Delete Config"
                    v-on:click="deleteConfig()"
                    :disabled="!canDeleteConfig"
                />

                <hr class="o-20" />
                <div class="mt3">
                    <h2 class="ttu mt0 mb1 f6 fw5 silver">Applying Auth Groups</h2>
                    <div class="mv3 w-100">Select Auth Groups</div>
                    <div class="mv3 w-100">
                        <select name="local" id="local" v-model="selectedAuthGroup" :value="selectedAuthGroup"> 
                            <option v-for="authGroup in authGroups" :value="authGroup._id" :key="authGroup._id">{{authGroup._id}} </option>
                        </select>
                </div>

                <input
                    class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                    type="button"
                    value="Apply this Config to Auth Group"
                    v-on:click="applyConfig()"
                    :disabled="!canApplyConfig"
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
            configData: null,
            selectedAuthGroup: '',
            authGroups: [],
            rolesData: [],
        }
    },
    computed: {
        formIsValid: function () {
            if(this.$store.state.permsData.configs !== 2) {
                return false
            }

            try {
                let config = JSON.parse(this.configData)

                // Check for required fields
                if (config.response_delay === undefined || config.portscan_window === undefined || config.portscan_threshold === undefined || config.whitelist_addrs === undefined || config.whitelist_ports === undefined || config.os === undefined || config.fingerprint === undefined || config.filtered_ports === undefined || config.services === undefined) {
                    return false
                }
                // More checks for user input
                if (config.response_delay < 0 || config.portscan_window < 0 || config.portscan_threshold < 0){
                    return false
                }
                for (let i = 0; i < config.whitelist_ports.length; i++) {
                    let whitelist = config.whitelist_ports[i]
                    if (whitelist < 0 || whitelist > 65535) {
                        return false
                    }
                }
                for (let i = 0; i < config.filtered_ports.length; i++) {
                    let filteredlist = config.filtered_ports[i]
                    if (filteredlist < 0 || filteredlist > 65535) {
                        return false
                    }
                }
                for (let i = 0; i < config.services.length; i++) {
                    let service = config.services[i]
                    if (service.name === undefined || service.port === undefined || service.protocol === undefined) {
                        return false
                    }
                    if (service.port < 0 || service.port > 65535) {
                        return false
                    }
                }
            } catch (err) {
                return false
            }

            return true
        },
        canDeleteConfig: function () {
            // Protect defaults
            if (this.$route.params.config === "configDefault") {
                return false
            } else if (this.$store.state.permsData.configs === 2) {
                return true
            } else {
                return false
            }
        },
        canUpdateConfig: function () {
            // Protect defaults
            if (this.$route.params.config === "configDefault") {
                return false
            } else if (this.$store.state.permsData.configs === 2) {
                return true
            } else {
                return false
            }
        },
        canApplyConfig: function () {
            // Protect defaults
            if (this.$store.state.permsData.configs === 2) {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        /**
         * Updates the config object in the database with the contents of the form
         */
        async updateConfig() {
            this.$Progress.start()
            try {
                let updateResponse = await api.updateConfig(this.$route.params.config, JSON.parse(this.configData))
                if (updateResponse.status !== 200) {
                    console.log("updateResponse code was not 200")
                    this.$toasted.show('Failed to update config. Error: updateResponse code was not 200')
                } else {
                    this.$toasted.show('Updated Config ' + this.$route.params.config)
                    this.loadItems()

                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Updated Config ' + this.configData._id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update config. Error: ' + updateError.message)
                this.loadItems()
            }
            this.$Progress.finish()
        },
        /**
         * Deletes the config object from the database
         */
        async deleteConfig() {
            try {
                let deleteResponse = await api.deleteConfig(this.$route.params.config)
                if (deleteResponse.status !== 200) {
                    console.log("deleteResponse code was not 200")
                    this.$toasted.show('Failed to delete config. Error: deleteResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Deleted Config ' + this.configData._id,
                        timestamp:Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)

                    this.$toasted.show('Deleted Config ' + this.$route.params.config)
                    this.$router.push('/configs')
                }
            } catch (err) {
                console.log(error)
                this.$toasted.show('Failed to delete config. Error: ' + error.message)
            }
        },
        /**
         * Updates the config object in the database with the contents of the form
         */
        async applyConfig() {
            this.$Progress.start()
            try {
                const honeypots = await api.getHoneypots(undefined, undefined, undefined, undefined, undefined)
                
                for (let i = 0; i < honeypots.data.docs.length; i++) {
                    if (honeypots.data.docs[i].auth_group_id === this.selectedAuthGroup){
                        honeypots.data.docs[i].config_id = this.$route.params.config
                        let updateResponse = await api.updateHoneypot(honeypots.data.docs[i]._id, honeypots.data.docs[i])
                        if (updateResponse.status !== 200) {
                            console.log("Apply config code was not 200")
                            this.$toasted.show('Failed to apply config. Error: Apply config code was not 200')
                        } else {
                            let adminLogData = {
                                changedBy: this.$store.state.userData.username,
                                message: 'Updated this config to Auth Group ' + this.selectedAuthGroup,
                                timestamp: Date.now()
                            }
                            let logResponse = await api.addAdminLog(adminLogData)
                            this.$toasted.show('Updated Auth Group ' + this.selectedAuthGroup)
                        }
                    }
                }
            } catch (updateError) {
                console.log(updateError)
                this.$toasted.show('Failed to update honeypot. Error: ' + updateError.message)
            }
            this.$Progress.finish()
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.configs === 0) {
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
                // Get config data
                let configResponse = await api.getConfigs(this.$route.params.config)
                let config = configResponse.data.docs[0]
                config._id = undefined
                config._rev = undefined
                this.configData = JSON.stringify(config, null, 2)
            } catch (err) {
                console.log(err)
            }

            try {
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
    },
    beforeMount() {
        this.checkPageAccessPermissions()
        this.loadItems()
    },
}
</script>
