<template>
  <div id="app">
    <SeatView />
  </div>
</template>

<script>
import SeatView from './views/SeatView.vue'

export default {
  name: 'App',
  components: {
    SeatView
  }
}
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f5f5;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
