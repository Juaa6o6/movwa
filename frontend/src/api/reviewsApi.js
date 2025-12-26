import http from "@/api/http";

const reviewsApi = {
  getMyReviews(params = {}) {
    return http.get("/api/v1/reviews/me/", { params });
  },
  createReview(payload) {
    return http.post("/api/v1/reviews/", payload);
  },
  updateReview(reviewId, payload) {
    return http.patch(`/api/v1/reviews/${reviewId}/`, payload);
  },
  deleteReview(reviewId) {
    return http.delete(`/api/v1/reviews/${reviewId}/`);
  },
  toggleLike(reviewId) {
    return http.post(`/api/v1/reviews/${reviewId}/like/`);
  },
};

export default reviewsApi;
