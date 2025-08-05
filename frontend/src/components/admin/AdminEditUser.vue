<template>
  <div>
    <div class="alert alert-info">
      <i class="bi bi-info-circle me-2"></i>
      <strong>Edit User:</strong> {{ user.first_name }} {{ user.last_name }} ({{
        user.email
      }})
    </div>

    <form @submit.prevent="updateUser">
      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">First Name</label>
          <input type="text" class="form-control" v-model="form.firstName" />
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Last Name</label>
          <input type="text" class="form-control" v-model="form.lastName" />
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input
          type="email"
          class="form-control"
          v-model="form.email"
          readonly
        />
        <div class="form-text">
          Email cannot be changed for security reasons
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div class="text-end">
        <button
          type="button"
          class="btn btn-secondary me-2"
          @click="$emit('cancelled')"
        >
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="updating">
          <span
            v-if="updating"
            class="spinner-border spinner-border-sm me-2"
          ></span>
          Update User
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";

export default {
  name: "AdminEditUser",
  props: {
    user: {
      type: Object,
      required: true,
    },
    userType: {
      type: String,
      required: true,
    },
  },
  emits: ["updated", "cancelled"],

  setup(props, { emit }) {
    const updating = ref(false);
    const error = ref("");
    const success = ref("");

    const form = reactive({
      firstName: "",
      lastName: "",
      email: "",
    });

    const updateUser = async () => {
      updating.value = true;
      error.value = "";

      try {
        // TODO: Implement user update API call
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API call

        success.value = "User updated successfully!";

        setTimeout(() => {
          emit("updated");
        }, 1500);
      } catch (err) {
        console.error("Failed to update user", err);
        error.value = "Failed to update user";
      } finally {
        updating.value = false;
      }
    };

    onMounted(() => {
      // Initialize form with user data
      form.firstName = props.user.first_name || "";
      form.lastName = props.user.last_name || "";
      form.email = props.user.email || "";
    });

    return {
      updating,
      error,
      success,
      form,
      updateUser,
    };
  },
};
</script>
