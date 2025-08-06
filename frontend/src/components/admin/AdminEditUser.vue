<template>
  <div>
    <div class="alert alert-info" v-if="user">
      <i class="bi bi-info-circle me-2"></i>
      <strong>Edit User:</strong> {{ user.first_name || "N/A" }}
      {{ user.last_name || "N/A" }} ({{ user.email || "N/A" }})
    </div>

    <div v-if="!user" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      User data is not available.
    </div>

    <form @submit.prevent="updateUser" v-if="user">
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

      <!-- Role-specific fields for doctors -->
      <div v-if="userType === 'doctor'">
        <div class="mb-3">
          <label class="form-label">Speciality</label>
          <input
            type="text"
            class="form-control"
            v-model="form.speciality"
            placeholder="e.g., Cardiology, General Medicine"
          />
        </div>

        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea
            class="form-control"
            v-model="form.description"
            rows="3"
            placeholder="Professional description (optional)"
          ></textarea>
        </div>
      </div>

      <!-- Role-specific fields for patients -->
      <div v-if="userType === 'patient'">
        <div class="mb-3">
          <label class="form-label">Date of Birth</label>
          <input type="date" class="form-control" v-model="form.dateOfBirth" />
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        <div v-if="typeof error === 'string'">{{ error }}</div>
        <div v-else>
          <div v-for="(messages, field) in error" :key="field">
            <strong>{{ field }}:</strong>
            {{ Array.isArray(messages) ? messages.join(", ") : messages }}
          </div>
        </div>
      </div>

      <div v-if="success" class="alert alert-success">
        <i class="bi bi-check-circle me-2"></i>
        {{ success }}
      </div>

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
import { ref, reactive, onMounted, watch } from "vue";

export default {
  name: "AdminEditUser",
  props: {
    user: {
      type: Object,
      required: true,
      default: () => null,
    },
    userType: {
      type: String,
      required: true,
      validator: (value) => ["doctor", "patient"].includes(value),
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
      speciality: "", // doctor only
      description: "", // doctor only
      dateOfBirth: "", // patient only
    });

    const initializeForm = () => {
      if (props.user) {
        form.firstName = props.user.first_name || "";
        form.lastName = props.user.last_name || "";
        form.email = props.user.email || "";

        // Initialize role-specific fields based on userType
        if (props.userType === "doctor") {
          // If we have doctor-specific data in the user object
          form.speciality = props.user.speciality || "";
          form.description = props.user.description || "";
        } else if (props.userType === "patient") {
          // If we have patient-specific data in the user object
          form.dateOfBirth = props.user.date_of_birth || "";
        }
      }
    };

    const updateUser = async () => {
      if (!props.user) {
        error.value = "User data is not available";
        return;
      }

      updating.value = true;
      error.value = "";
      success.value = "";

      try {
        // Prepare update data
        const updateData = {
          first_name: form.firstName,
          last_name: form.lastName,
          // Note: email is readonly, so we don't include it
        };

        // Add role-specific data
        if (props.userType === "doctor") {
          updateData.speciality = form.speciality;
          updateData.description = form.description;
        } else if (props.userType === "patient") {
          updateData.date_of_birth = form.dateOfBirth;
        }

        // TODO: Implement actual API call to update user
        // For now, simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000));

        success.value = "User updated successfully!";

        setTimeout(() => {
          emit("updated");
        }, 1500);
      } catch (err) {
        console.error("Failed to update user", err);
        error.value = err.response?.data || "Failed to update user";
      } finally {
        updating.value = false;
      }
    };

    // Watch for user prop changes and reinitialize form
    watch(() => props.user, initializeForm, { immediate: true, deep: true });

    onMounted(() => {
      initializeForm();
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
