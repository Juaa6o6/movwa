// src/api/movieApi.js
import http from './http';

export default {
  // Movie detail (GET /movies/{id}/)
  getMovieDetail(movieId) {
    return http.get(`/api/v1/movies/${movieId}/`);
  },
  // Movie reviews (GET /reviews/?movie_id=...)
  getMovieReviews(movieId) {
    return http.get(`/api/v1/reviews/`, { params: { movie_id: movieId } });
  },
  // -----------------------
  // HOME (REC-01~09)
  // -----------------------

  // 추천 10개 (GET /movies/?page_size=10)
  getRecommendations(limit = 10) {
    return http.get(`/api/v1/movies/`, { params: { page_size: limit } });
  },

  // PASS (POST /movies/{id}/like/) body: { is_liked: false }
  passMovie(movieId) {
    return http.post(`/api/v1/movies/${movieId}/like/`, { is_liked: false });
  },

  // LIKE (POST /movies/{id}/like/)  body: { is_liked: true/false }
  likeMovie(movieId, is_liked = true) {
    return http.post(`/api/v1/movies/${movieId}/like/`, { is_liked });
  },

  // RATE (POST /movies/{id}/rate/) body: { rating: 4.5 }
  rateMovie(movieId, rating) {
    return http.post(`/api/v1/movies/${movieId}/rate/`, { rating });
  },

  // SAVE (POST /movies/{id}/save/)
  saveMovie(movieId) {
    return http.post(`/api/v1/movies/${movieId}/save/`);
  },

  // 오늘의 픽 (GET /movies/my/todays-pick/)
  getTodayPicks() {
    return http.get(`/api/v1/movies/my/todays-pick/`);
  },
};
