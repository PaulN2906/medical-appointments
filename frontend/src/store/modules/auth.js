import AuthService from "@/services/auth.service";

// Helper functions for localStorage
const saveUserToStorage = (user) => {
  try {
    localStorage.setItem("user", JSON.stringify(user));
  } catch (error) {
    console.warn("Failed to save user to localStorage:", error);
  }
};

const loadUserFromStorage = () => {
  try {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.warn("Failed to load user from localStorage:", error);
    localStorage.removeItem("user"); // Clear corrupted data
    return null;
  }
};

const clearUserFromStorage = () => {
  try {
    localStorage.removeItem("user");
  } catch (error) {
    console.warn("Failed to clear user from localStorage:", error);
  }
};

export default {
  namespaced: true,

  state: {
    user: loadUserFromStorage(), // Load user on initialization
    token: null,
    requires2FA: false,
    tempUserId: null,
  },

  mutations: {
    setUser(state, user) {
      state.user = user;
      if (user) {
        saveUserToStorage(user);
      } else {
        clearUserFromStorage();
      }
    },
    setToken(state, token) {
      state.token = token;
    },
    setRequires2FA(state, { requires2FA, userId }) {
      state.requires2FA = requires2FA;
      state.tempUserId = userId;
    },
    clearAuth(state) {
      state.user = null;
      state.token = null;
      state.requires2FA = false;
      state.tempUserId = null;
      clearUserFromStorage();
    },
  },

  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await AuthService.login(credentials);

        if (response.data.requires_2fa) {
          commit("setRequires2FA", {
            requires2FA: true,
            userId: response.data.user_id,
          });
          return { requires2FA: true };
        } else {
          const userData = {
            id: response.data.user_id,
            email: response.data.email,
            role: response.data.role,
            first_name: response.data.first_name,
            last_name: response.data.last_name,
            doctor_id: response.data.doctor_id,
            patient_id: response.data.patient_id,
            two_fa_enabled: response.data.two_fa_enabled,
          };

          commit("setUser", userData);
          commit("setToken", response.data.token);
          return { success: true };
        }
      } catch (error) {
        return { error: error.response?.data?.error || "Login failed" };
      }
    },

    async verify2FA({ commit, state }, code) {
      try {
        const response = await AuthService.verify2FA(state.tempUserId, code);
        const userData = {
          id: response.data.user_id,
          email: response.data.email,
          role: response.data.role,
          first_name: response.data.first_name,
          last_name: response.data.last_name,
          doctor_id: response.data.doctor_id,
          patient_id: response.data.patient_id,
          two_fa_enabled: response.data.two_fa_enabled,
        };

        commit("setUser", userData);
        commit("setToken", response.data.token);
        commit("setRequires2FA", { requires2FA: false, userId: null });
        return { success: true };
      } catch (error) {
        return {
          error: error.response?.data?.error || "2FA verification failed",
        };
      }
    },

    async register(_, userData) {
      try {
        await AuthService.register(userData);
        return { success: true };
      } catch (error) {
        return { error: error.response?.data || "Registration failed" };
      }
    },

    async logout({ commit }) {
      try {
        await AuthService.logout();
      } catch (error) {
        console.warn("Logout API call failed:", error);
        // Continue with local logout even if API fails
      } finally {
        commit("clearAuth");
      }
    },

    // Add action to check authentication on app startup
    async checkAuth({ commit, state }) {
      // If we have a user in state/localStorage, verify they're still authenticated
      if (state.user) {
        try {
          // Try to get user profile to verify auth is still valid
          const response =
            (await AuthService.getUserProfile?.()) ||
            (await fetch("/api/auth/users/get_profile/", {
              credentials: "include",
            }));

          if (response.ok || response.status === 200) {
            // User is still authenticated, keep the stored user
            console.log("Authentication verified on startup");
            return true;
          } else {
            // Auth expired, clear it
            console.log("Authentication expired, clearing user");
            commit("clearAuth");
            return false;
          }
        } catch (error) {
          console.warn("Auth check failed:", error);
          // If we can't verify, assume auth is invalid
          commit("clearAuth");
          return false;
        }
      }
      return false;
    },
  },

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentUser: (state) => state.user,
    requires2FA: (state) => state.requires2FA,
  },
};
