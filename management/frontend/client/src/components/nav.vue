<template>
    <nav class="w-100 w-25-m w-25-l mb4 mb0-l ph3-m ph3-l">
        <header class="mb2">
            <i class="material-icons f2 black-70">dashboard</i>
        </header>
        <form class="mb4 w-100 w-70-m w-80-l">
            <input
                type="text"
                placeholder="Search"
                class="input-reset ba b--black-20 pa1 br2 f5 w-100"
            />
        </form>
        <p v-if="showAllToolbar">Welcome, {{fullUserName}}!</p>
        <ul class="list pl0 mt0 mb4">
            <li
                class="mb2"
                v-for="(l, idx) in [
                    ['Home', '/'],
                ]"
                :key="idx"
            >
                <router-link :to="l[1]" class="block link dim blue">{{
                    l[0]
                }}</router-link>
            </li>
        </ul>
        <ul class="list pl0 mt0 mb4" v-if="showAllToolbar">
            <li
                class="mb2"
                v-for="(l, idx) in [
                    ['My Profile', myProfileLink],
                    ['About', '/about'],
                ]"
                :key="idx"
            >
                <router-link :to="l[1]" class="block link dim blue">{{
                    l[0]
                }}</router-link>
            </li>
            <li class="mb2">
                <div
                    class="block link dim blue pointer"
                    name="logoutClick"
                    @click="logout"
                >
                    Logout
                </div>
            </li>
        </ul>
        <!-- Main Navigation Links -->
        <div v-if="showAllToolbar && viewableManagePages.length != 0">
            <h2 class="ttu mt0 mb2 f6 fw5 silver">Manage</h2>
            <ul class="list pl0 mt0 mb4">
                <li
                    class="mb2"
                    v-for="(l, idx) in viewableManagePages"
                    :key="idx"
                >
                    <router-link :to="l[1]" class="block link dim blue">{{
                        l[0]
                    }}</router-link>
                </li>
            </ul>
        </div>
        <!-- Dashboards for Individual Hosts -->
        <div v-if="showAllToolbar && viewableDashboards.length != 0">
            <h2 class="ttu mt0 mb2 f6 fw5 silver">Dashboards</h2>
            <ul class="list pl0 mt0 mb4">
                <li
                    class="mb2"
                    v-for="(l, idx) in viewableDashboards"
                    :key="idx"
                >
                    <router-link :to="l[1]" class="block link dim blue">{{
                        l[0]
                    }}</router-link>
                </li>
                <li v-if="$store.state.logsInfo.doc_count != 0" class="mb2">
                    <router-link to="/details/aggregate" class="block link dim blue">{{
                        'aggregate' | formatDBName
                    }}</router-link>
                </li>
            </ul>
        </div>
    
        <h2 class="ttu mt0 mb2 f6 fw5 silver">More</h2>
        <ul class="list pl0 mt0 mb2">
            <li class="mb2">
                <a
                    :href="managementDBUrl + '/_utils'"
                    target="_blank"
                    class="block link dim blue"
                >
                    Management Database
                </a>
            </li>
            <li class="mb2">
                <a
                    href="https://github.com/MDSLKTR/pouch-vue"
                    target="_blank"
                    class="block link dim blue"
                >
                    PouchDB API
                </a>
            </li>
            <li>
                <a
                    href="https://docs.couchdb.org/en/stable/api/index.html"
                    target="_blank"
                    class="block link dim blue"
                >
                    Database API
                </a>
            </li>
        </ul>
    </nav>
</template>

<script>
export default {
    name: 'Nav',
    computed: {
        showAllToolbar: function () {
            if (this.$route.name === 'login' || this.$store.state.userData == undefined ||  this.$store.state.permsData == undefined) {
                return false
            } else {
                return true
            }
        },
        myProfileLink: function () {
            return '/users/' + this.$store.state.userData._id
        },
        fullUserName: function () {
            return this.$store.state.userData.firstname + ' ' + this.$store.state.userData.lastname
        },
        viewableManagePages: function () {
            if (this.$store.state.permsData == undefined) return []
            const managePages = []
            if (this.$store.state.permsData.users !== 0) managePages.push(['Users', '/users']);
            if (this.$store.state.permsData.roles !== 0) managePages.push(['Roles', '/roles']);
            if (this.$store.state.permsData.configs !== 0) managePages.push(['Configs', '/configs']);
            if (this.$store.state.permsData.authGroupsMgmt !== 0) managePages.push(['Auth Groups', '/authGroups']);
            if (this.$store.state.permsData.adminLogs !== 0) managePages.push(['Admin Logs', '/adminLogs']);
            return managePages
        },
        viewableDashboards: function () {
            if (this.$store.state.permsData == undefined) return []
            const dashPages = []
            if (this.$store.state.permsData.traffLogs !== 0) dashPages.push(['Overview', '/overview']);
            if (this.$store.state.permsData.devices !== 0) dashPages.push(['Honeypots', '/honeypots']);
            if (this.$store.state.permsData.metrics !== 0) dashPages.push(['Metrics', '/metrics']);
            if (this.$store.state.permsData.alerts !== 0) dashPages.push(['Alerts', '/alerts']);
            return dashPages
        },
    },
    methods: {
        async logout(e) {
            let res = await this.axios.get('/logout')
            this.$store.commit('setUserData', undefined)
            this.$store.commit('setPermsData', undefined)
            this.$toasted.show('Logged out.')
            this.$router.push('/login')
        },
    },
    data() {
        return {
            managementDBUrl: process.env.DB_URL,
        }
    },
}
</script>
