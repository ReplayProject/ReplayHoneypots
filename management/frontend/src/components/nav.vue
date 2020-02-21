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
    <!-- Temporary Links -->
    <h2 class="ttu mt0 mb2 f6 fw5 silver">Test Links</h2>
    <ul class="list pl0 mt0 mb4">
      <li class="mb2">
        <router-link to="/" class="block link dim blue">Home</router-link>
      </li>
      <li class="mb2">
        <router-link to="/about" class="block link dim blue">About</router-link>
      </li>
      <li class="mb2">
        <router-link to="/edit" class="block link dim blue">Edit</router-link>
      </li>
    </ul>
    <!-- More Realistic Options -->
    <h2 class="ttu mt0 mb2 f6 fw5 silver">Dashboards</h2>
    <ul class="list pl0 mt0 mb4">
      <li class="mb2">
        <router-link to="/overview" class="block link dim blue"
          >Overview</router-link
        >
      </li>
      <li v-for="db in $parent.dbInfo" :key="db.db_name" class="mb2">
        <router-link
          :to="'/details/' + db.db_name"
          class="block link dim blue"
          >{{ db.db_name | formatDBName }}</router-link
        >
      </li>
    </ul>
    <h2 class="ttu mt0 mb2 f6 fw5 silver">More</h2>
    <ul class="list pl0 mt0 mb2">
      <!-- <li class="mb2">
        <router-link to="/toolkitDocs" class="block link dim blue"
          >Toolkit Docs</router-link
        >
      </li> -->
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
  data () {
    return {
      managementDBUrl: process.env.DB_URL
    }
  }
}
</script>
