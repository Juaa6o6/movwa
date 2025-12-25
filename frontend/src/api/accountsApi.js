import http from "@/api/http";

const accountsApi = {
  getFollowings(username) {
    return http.get(`/api/v1/accounts/${username}/followings/`);
  },
  getFollowers(username) {
    return http.get(`/api/v1/accounts/${username}/followers/`);
  },
  toggleFollow(username) {
    return http.post(`/api/v1/accounts/${username}/follow/`);
  },
  getUserDetail(username) {
    return http.get(`/api/v1/accounts/${username}/`);
  },
  updateProfile(formData) {
    return http.patch("/api/v1/accounts/me/update/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default accountsApi;
