import AuthService from "@/services/auth.service";

export default {
  namespaced: true,

  state: {
    user: AuthService.getUser(),
    token: null,
    requires2FA: false,
    tempUserId: null,
  },

  mutations: {
    setUser(state, user) {
      state.user = user;
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
          };

          AuthService.saveUserData(userData);
          commit("setUser", userData);
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
        };

        AuthService.saveUserData(userData);
        commit("setUser", userData);
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
      } finally {
        commit("clearAuth");
      }
    },
  },

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentUser: (state) => state.user,
    requires2FA: (state) => state.requires2FA,
  },
};
