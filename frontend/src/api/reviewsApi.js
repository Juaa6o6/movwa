import http from "@/api/http";

const reviewsApi = {
  getMyReviews(params = {}) {
    return http.get("/api/v1/reviews/me/", { params });
  },
};

export default reviewsApi;
