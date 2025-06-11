import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "./assets/main.css";
import * as bootstrap from "bootstrap";

window.bootstrap = bootstrap;

// Initialize the app
const app = createApp(App);

// Check authentication status before mounting
async function initializeApp() {
  try {
    // Check if user is still authenticated on app startup
    await store.dispatch("auth/checkAuth");
  } catch (error) {
    console.warn("Auth check failed during app initialization:", error);
  }
  // Mount the app
  app.use(store).use(router).mount("#app");
}

// Initialize the app
initializeApp();
