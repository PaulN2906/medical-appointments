<template>
  <span :class="['spinner-border', sizeClass]" role="status">
    <span class="visually-hidden">Loading...</span>
  </span>
</template>

<script>
export default {
  name: "LoadingSpinner",
  props: {
    size: {
      type: String,
      default: null,
    },
  },
  computed: {
    sizeClass() {
      return this.size ? `spinner-border-${this.size}` : "";
    },
  },
};
</script>
