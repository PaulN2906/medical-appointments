<template>
  <div>
    <div v-if="loadingProfile" class="text-center p-4">
      <LoadingSpinner />
    </div>

    <div v-else-if="personalInfoError" class="alert alert-danger">
      {{ personalInfoError }}
    </div>

    <form @submit.prevent="savePersonalInfo">
      <div class="row mb-3">
        <div class="col-md-6">
          <label for="firstName" class="form-label">First Name</label>
          <input
            type="text"
            class="form-control"
            id="firstName"
            v-model="personalInfo.firstName"
            required
          />
        </div>
        <div class="col-md-6">
          <label for="lastName" class="form-label">Last Name</label>
          <input
            type="text"
            class="form-control"
            id="lastName"
            v-model="personalInfo.lastName"
            required
          />
        </div>
      </div>

      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="personalInfo.email"
          required
          readonly
        />
        <div class="form-text">Email cannot be changed.</div>
      </div>

      <div class="mb-3">
        <label for="phone" class="form-label">Phone Number</label>
        <input
          type="tel"
          class="form-control"
          id="phone"
          v-model="personalInfo.phone"
        />
      </div>

      <div v-if="userType === 'patient'" class="mb-3">
        <label for="birthDate" class="form-label">Date of Birth</label>
        <input
          type="date"
          class="form-control"
          id="birthDate"
          v-model="personalInfo.birthDate"
        />
      </div>

      <div v-if="userType === 'doctor'" class="mb-3">
        <label for="speciality" class="form-label">Speciality</label>
        <input
          type="text"
          class="form-control"
          id="speciality"
          v-model="personalInfo.speciality"
        />
      </div>

      <div v-if="userType === 'doctor'" class="mb-3">
        <label for="description" class="form-label"
          >Professional Description</label
        >
        <textarea
          class="form-control"
          id="description"
          v-model="personalInfo.description"
          rows="4"
        ></textarea>
      </div>

      <div v-if="personalInfoSaved" class="alert alert-success mb-3">
        Personal information updated successfully!
      </div>

      <div class="text-end">
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="savingPersonalInfo"
        >
          <LoadingSpinner v-if="savingPersonalInfo" size="sm" class="me-2" />
          Save Changes
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import UserService from "@/services/user.service";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

export default {
  name: "ProfilePersonalInfo",
  components: { LoadingSpinner },
  setup() {
    const store = useStore();
    const loadingProfile = ref(true);
    const savingPersonalInfo = ref(false);
    const personalInfoSaved = ref(false);
    const personalInfoError = ref("");

    const personalInfo = reactive({
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      birthDate: "",
      speciality: "",
      description: "",
    });

    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const userType = computed(() => currentUser.value?.role || "patient");

    const loadUserProfile = async () => {
      try {
        const response = await UserService.getUserProfile();
        const profile = response.data;
        personalInfo.firstName = profile.first_name || "";
        personalInfo.lastName = profile.last_name || "";
        personalInfo.email = profile.email || "";
        personalInfo.phone = profile.phone_number || "";
        if (userType.value === "doctor") {
          personalInfo.speciality = profile.speciality || "";
          personalInfo.description = profile.description || "";
        } else if (userType.value === "patient") {
          personalInfo.birthDate = profile.date_of_birth || "";
        }
      } catch (error) {
        console.error("Failed to load user profile:", error);
        personalInfoError.value =
          "Failed to load profile data. Please refresh the page.";
      } finally {
        loadingProfile.value = false;
      }
    };

    const savePersonalInfo = async () => {
      savingPersonalInfo.value = true;
      personalInfoSaved.value = false;
      personalInfoError.value = "";

      try {
        const updateData = {
          first_name: personalInfo.firstName,
          last_name: personalInfo.lastName,
          phone_number: personalInfo.phone,
        };

        if (userType.value === "doctor") {
          updateData.speciality = personalInfo.speciality;
          updateData.description = personalInfo.description;
        } else if (userType.value === "patient") {
          updateData.date_of_birth = personalInfo.birthDate;
        }

        const response = await UserService.updateProfile(updateData);
        const updatedUser = {
          ...currentUser.value,
          first_name: response.data.first_name,
          last_name: response.data.last_name,
        };
        store.commit("auth/setUser", updatedUser);

        personalInfoSaved.value = true;
        setTimeout(() => {
          personalInfoSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to save personal information:", error);
        personalInfoError.value =
          error.response?.data?.error ||
          "Failed to save personal information. Please try again.";
      } finally {
        savingPersonalInfo.value = false;
      }
    };

    onMounted(() => {
      loadUserProfile();
    });

    return {
      loadingProfile,
      personalInfo,
      savingPersonalInfo,
      personalInfoSaved,
      personalInfoError,
      userType,
      savePersonalInfo,
    };
  },
};
</script>
