import '@babel/polyfill'
import Vue from 'vue'
import app from './app.vue'
import VueProgressBar from "vue-progressbar";
import router from './router'

Vue.use(VueProgressBar, {
  color: "rgb(143, 255, 199)",
  failedColor: "red",
  thickness: "5px"
});

window.v = new Vue({
  el: '#app',
  router,
  render: h => h(app)
})
