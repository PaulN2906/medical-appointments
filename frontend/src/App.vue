<template>
  <div id="app">
    <Navbar />
    <router-view />
    <footer class="footer mt-auto py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">© 2025 Medical Appointments System</span>
      </div>
    </footer>
  </div>
</template>

<script>
import Navbar from "@/components/common/Navbar.vue";

export default {
  name: "App",
  components: {
    Navbar,
  },
};
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.footer {
  margin-top: auto;
}
</style>
