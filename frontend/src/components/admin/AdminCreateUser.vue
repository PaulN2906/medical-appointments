<template>
  <UserForm
    :mode="'create'"
    :userType="userType"
    :loading="creating"
    :error="error"
    :success="success"
    :submitLabel="`Create ${userType === 'doctor' ? 'Doctor' : 'Patient'}`"
    @submit="createUser"
    @cancelled="$emit('cancelled')"
  />
</template>

<script>
import { ref } from "vue";
import AdminService from "@/services/admin.service";
import UserForm from "./UserForm.vue";

export default {
  name: "AdminCreateUser",
  components: { UserForm },
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

    const createUser = async (form) => {
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
      createUser,
    };
  },
};
</script>
