<template>
    <!-- This page serves as a template for creating new ones! -->
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'configs',
            'w-75-l': $route.name != 'configs',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Manage</template>
            <template v-slot:pageName>Add New Config</template>
        </component-title>
        <hr class="o-20" />
        <hr class="o-20" />
        <div class="mt3">
            <h2 class="ttu mt0 mb1 f6 fw5 silver">Config Data</h2>
            <label class="db fw6 lh-copy f6" for="config">Config JSON</label>
            <textarea
                class="pa2 input-reset ba bg-transparent w-100"
                rows="20"
                v-model="configData.config"
                name="config"
                id="config"
                required
            ></textarea>
            <label class="db fw6 lh-copy f6" for="name">Name (ID)</label>
            <input
                class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                type="text"
                v-model="configData.name"
                name="name"
                id="name"
                required
            />
        </div>
        <hr class="o-20" />
        <div class="">
            <input
                class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                type="button"
                value="Import Config"
                v-on:click="addConfig()"
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
            configData: {},
            rolesData: [],
        }
    },
    computed: {
        formIsValid: function () {
            try {
                if(this.$store.state.permsData.configs !== 2) {
                    return false
                }

                let config = JSON.parse(this.configData.config)

                // Check for required fields
                if (config.response_delay === undefined || config.portscan_window === undefined || config.portscan_threshold === undefined || config.whitelist_addrs === undefined || config.whitelist_ports === undefined || config.os === undefined || config.fingerprint === undefined || config.filtered_ports === undefined || config.services === undefined || this.configData.name === undefined) {
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

                // Check that ID is unique
                for (let i = 0; i < this.allConfigs.length; i++) {
                    if (this.allConfigs[i]._id === this.configData.name) {
                        return false
                    }
                }
            } catch (err) {
                return false
            }

            return true
        },
    },
    methods: {
        /**
         * Adds the config object in the database with the contents of the form
         */
        async addConfig() {
            this.$Progress.start()
            let config = JSON.parse(this.configData.config)
            config._id = this.configData.name
            config._rev = undefined
            try {
                let addResponse = await api.addConfig(config)
                if (addResponse.status !== 200) {
                    console.log("addResponse code was not 200")
                    this.$toasted.show('Failed to add config. Error: addResponse code was not 200')
                } else {
                    let adminLogData = {
                        changedBy: this.$store.state.userData.username,
                        message: 'Added Config' + this.config._id,
                        timestamp: Date.now()
                    }
                    let logResponse = await api.addAdminLog(adminLogData)
                    
                    this.$toasted.show('Added New Config')
                    this.loadItems()
                }
            } catch (addError) {
                console.log(addError)
                this.$toasted.show('Failed to add config. Error: ' + addError.message)
                this.loadItems()
            }
            this.$Progress.finish()
        },
        /**
         * Checks if the user should have access to this page and sends them back to index if not
         */
        checkPageAccessPermissions() {
            if (this.$store.state.permsData.configs !== 2) {
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

            let configResponse = await api.getConfigs(undefined, undefined, undefined, ["_id"], undefined)
            this.allConfigs = configResponse.data.docs;

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
