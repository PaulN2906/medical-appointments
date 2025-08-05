<template>
  <div>
    <form @submit.prevent="createUser">
      <div class="row">
        <!-- Basic User Info -->
        <div class="col-md-6 mb-3">
          <label class="form-label">First Name *</label>
          <input
            type="text"
            class="form-control"
            v-model="form.firstName"
            required
          />
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Last Name *</label>
          <input
            type="text"
            class="form-control"
            v-model="form.lastName"
            required
          />
        </div>
      </div>

      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Username *</label>
          <input
            type="text"
            class="form-control"
            v-model="form.username"
            required
          />
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Email *</label>
          <input
            type="email"
            class="form-control"
            v-model="form.email"
            required
          />
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Password *</label>
        <input
          type="password"
          class="form-control"
          v-model="form.password"
          required
          minlength="8"
        />
        <div class="form-text">Minimum 8 characters</div>
      </div>

      <!-- Doctor-specific fields -->
      <div v-if="userType === 'doctor'">
        <div class="mb-3">
          <label class="form-label">Speciality *</label>
          <input
            type="text"
            class="form-control"
            v-model="form.speciality"
            placeholder="e.g., Cardiology, General Medicine"
            required
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

      <!-- Patient-specific fields -->
      <div v-if="userType === 'patient'">
        <div class="mb-3">
          <label class="form-label">Date of Birth</label>
          <input type="date" class="form-control" v-model="form.dateOfBirth" />
        </div>
      </div>

      <!-- Error Display -->
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

      <!-- Success Display -->
      <div v-if="success" class="alert alert-success">
        <i class="bi bi-check-circle me-2"></i>
        {{ success }}
      </div>

      <!-- Form Actions -->
      <div class="text-end">
        <button
          type="button"
          class="btn btn-secondary me-2"
          @click="$emit('cancelled')"
        >
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="creating">
          <span
            v-if="creating"
            class="spinner-border spinner-border-sm me-2"
            role="status"
          ></span>
          <i v-else class="bi bi-person-plus me-2"></i>
          Create {{ userType === "doctor" ? "Doctor" : "Patient" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, watch } from "vue";
import AdminService from "@/services/admin.service";

export default {
  name: "AdminCreateUser",
  props: {
    userType: {
      type: String,
      required: true,
      validator: (value) => ["doctor", "patient"].includes(value),
    },
  },
  emits: ["created", "cancelled"],

  setup(props, { emit }) {
    const creating = ref(false);
    const error = ref("");
    const success = ref("");

    const form = reactive({
      firstName: "",
      lastName: "",
      username: "",
      email: "",
      password: "",
      speciality: "", // doctor only
      description: "", // doctor only
      dateOfBirth: "", // patient only
    });

    const resetForm = () => {
      Object.keys(form).forEach((key) => {
        form[key] = "";
      });
      error.value = "";
      success.value = "";
    };

    // Reset form cand se schimba tipul utilizatorului
    watch(() => props.userType, resetForm);

    const createUser = async () => {
      creating.value = true;
      error.value = "";
      success.value = "";

      try {
        const userData = {
          username: form.username,
          email: form.email,
          password: form.password,
          first_name: form.firstName,
          last_name: form.lastName,
          user_type: props.userType,
        };

        // Add role-specific data
        if (props.userType === "doctor") {
          userData.speciality = form.speciality;
          if (form.description) {
            userData.description = form.description;
          }
        } else if (props.userType === "patient") {
          if (form.dateOfBirth) {
            userData.date_of_birth = form.dateOfBirth;
          }
        }

        await AdminService.createUser(userData);

        success.value = `${
          props.userType === "doctor" ? "Doctor" : "Patient"
        } created successfully!`;

        // Emit success after a short delay
        setTimeout(() => {
          emit("created");
        }, 1500);
      } catch (err) {
        console.error("Failed to create user", err);
        error.value = err.response?.data || "Failed to create user";
      } finally {
        creating.value = false;
      }
    };

    return {
      creating,
      error,
      success,
      form,
      createUser,
    };
  },
};
</script>
