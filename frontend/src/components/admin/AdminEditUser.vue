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

    <UserForm
      v-if="user"
      :mode="'edit'"
      :user="user"
      :userType="userType"
      :loading="updating"
      :error="error"
      :success="success"
      submitLabel="Update User"
      @submit="updateUser"
      @cancelled="$emit('cancelled')"
    />
  </div>
</template>

<script>
import { ref } from "vue";
import AdminService from "@/services/admin.service";
import UserForm from "./UserForm.vue";

export default {
  name: "AdminEditUser",
  components: { UserForm },
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

    const updateUser = async (form) => {
      if (!props.user) {
        error.value = "User data is not available";
        return;
      }

      updating.value = true;
      error.value = "";
      success.value = "";

      try {
        const updateData = {
          first_name: form.firstName,
          last_name: form.lastName,
          email: form.email,
          phone_number: form.phoneNumber || "",
        };

        if (props.userType === "doctor") {
          updateData.speciality = form.speciality;
          updateData.description = form.description;
        } else if (props.userType === "patient") {
          if (form.dateOfBirth) {
            updateData.date_of_birth = form.dateOfBirth;
          }
        }

        const response = await AdminService.updateUser(
          props.user.id,
          updateData
        );

        success.value = "User updated successfully!";

        setTimeout(() => {
          emit("updated", response.data);
        }, 1500);
      } catch (err) {
        console.error("Failed to update user", err);

        if (err.response?.data?.error) {
          error.value = err.response.data.error;
        } else if (typeof err.response?.data === "object") {
          const errors = [];
          for (const [field, messages] of Object.entries(err.response.data)) {
            if (Array.isArray(messages)) {
              errors.push(`${field}: ${messages.join(", ")}`);
            } else {
              errors.push(`${field}: ${messages}`);
            }
          }
          error.value = errors.join("; ");
        } else {
          error.value = "Failed to update user";
        }
      } finally {
        updating.value = false;
      }
    };

    return {
      updating,
      error,
      success,
      updateUser,
    };
  },
};
</script>
