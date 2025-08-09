<template>
  <form @submit.prevent="onSubmit">
    <div class="row">
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

    <div v-if="mode === 'create'" class="row">
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
    <div v-else class="mb-3">
      <label class="form-label">Email</label>
      <input type="email" class="form-control" v-model="form.email" readonly />
      <div class="form-text">Email cannot be changed for security reasons</div>
    </div>

    <div class="mb-3" v-if="mode === 'create'">
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
        <label class="form-label"
          >Speciality <span v-if="mode === 'create'">*</span></label
        >
        <input
          type="text"
          class="form-control"
          v-model="form.speciality"
          :required="mode === 'create'"
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

    <!-- Patient-specific fields -->
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
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <LoadingSpinner v-if="loading" size="sm" class="me-2" />
        {{ submitLabel }}
      </button>
    </div>
  </form>
</template>

<script>
import { reactive, watch, onMounted } from "vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

export default {
  name: "UserForm",
  components: { LoadingSpinner },
  props: {
    mode: {
      type: String,
      required: true,
      validator: (value) => ["create", "edit"].includes(value),
    },
    userType: {
      type: String,
      required: true,
      validator: (value) => ["doctor", "patient"].includes(value),
    },
    user: {
      type: Object,
      default: () => null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: [String, Object],
      default: "",
    },
    success: {
      type: String,
      default: "",
    },
    submitLabel: {
      type: String,
      required: true,
    },
  },
  emits: ["submit", "cancelled"],
  setup(props, { emit }) {
    const form = reactive({
      firstName: "",
      lastName: "",
      username: "",
      email: "",
      password: "",
      speciality: "",
      description: "",
      dateOfBirth: "",
      phoneNumber: "",
    });

    const resetForm = () => {
      Object.keys(form).forEach((key) => {
        form[key] = "";
      });
    };

    const initializeForm = () => {
      if (props.mode === "edit" && props.user) {
        form.firstName = props.user.first_name || "";
        form.lastName = props.user.last_name || "";
        form.email = props.user.email || "";
        form.phoneNumber = props.user.phone_number || "";

        if (props.userType === "doctor") {
          form.speciality = props.user.speciality || "";
          form.description = props.user.description || "";
        } else if (props.userType === "patient") {
          form.dateOfBirth = props.user.date_of_birth || "";
        }
      } else if (props.mode === "create") {
        resetForm();
      }
    };

    const onSubmit = () => {
      emit("submit", { ...form });
    };

    watch(
      () => props.userType,
      () => {
        if (props.mode === "create") {
          resetForm();
        }
      }
    );

    watch(() => props.user, initializeForm, { immediate: true, deep: true });

    onMounted(() => {
      initializeForm();
    });

    return {
      form,
      onSubmit,
    };
  },
};
</script>
