// src/api/movieApi.js
import http from './http';

export default {
  // Movie detail (GET /movies/{id}/)
  getMovieDetail(movieId) {
    return http.get(`/api/v1/movies/${movieId}/`);
  },
  // Movie related videos (GET /movies/{id}/related-videos/)
  getRelatedVideos(movieId) {
    return http.get(`/api/v1/movies/${movieId}/related-videos/`);
  },
  // Movie reviews (GET /reviews/?movie_id=...)
  getMovieReviews(movieId) {
    return http.get(`/api/v1/reviews/`, { params: { movie_id: movieId } });
  },
  // -----------------------
  // HOME (REC-01~09)
  // -----------------------

  // 추천 10개 (GET /movies/?page_size=10&sort=popularity)
  getRecommendations(limit = 10, genreIds = [], page = 1) {
    const params = { page_size: limit, sort: 'popularity', exclude_future: 1, page };
    if (Array.isArray(genreIds) && genreIds.length) {
      params.genres = genreIds.join(',');
    }
    return http.get(`/api/v1/movies/`, { params });
  },

  getRecommendationBatch(limit = 10, excludeIds = []) {
    const params = { limit };
    if (Array.isArray(excludeIds) && excludeIds.length) {
      params.exclude = excludeIds.join(',');
    }
    return http.get(`/api/v1/movies/recommendations/batch/`, { params });
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

  // RATE 삭제 (DELETE /movies/{id}/rate/)
  deleteRate(movieId) {
    return http.delete(`/api/v1/movies/${movieId}/rate/`);
  },

  // SAVE (POST /movies/{id}/save/) body: { is_saved: true/false }
  saveMovie(movieId, is_saved = true) {
    return http.post(`/api/v1/movies/${movieId}/save/`, { is_saved });
  },

  // 오늘의 픽 (GET /movies/my/todays-pick/)
  getTodayPicks() {
    return http.get(`/api/v1/movies/my/todays-pick/`);
  },

  // 유저 로그 벌크 조회 (POST /movies/user-logs/)
  getUserMovieLogs(movieIds = []) {
    return http.post(`/api/v1/movies/user-logs/`, { movie_ids: movieIds });
  },

  // 박스오피스 (GET /movies/boxoffice/)
  getBoxOffice(limit = 10) {
    return http.get(`/api/v1/movies/boxoffice/`, { params: { limit } });
  },

  // 개봉 예정 (GET /movies/upcoming/)
  getUpcomingMovies(limit = 10) {
    return http.get(`/api/v1/movies/upcoming/`, { params: { limit } });
  },

  // 평점 높은 영화 (GET /movies/top-rated/)
  getTopRatedMovies(limit = 10) {
    return http.get(`/api/v1/movies/top-rated/`, { params: { limit } });
  },

  // 전체 영화 목록 (GET /movies/)
  getMoviesList(pageSize = 100) {
    return http.get(`/api/v1/movies/`, { params: { page_size: pageSize } });
  },

  // 영화 검색 (GET /movies/search/)
  searchMovies(query, sort = 'popularity', page = 1) {
    return http.get(`/api/v1/movies/search/`, { params: { q: query, sort, page } });
  },

  // 내가 평가한 영화 로그 (GET /movies/my/rated/logs/)
  getRatedMovieLogs() {
    return http.get(`/api/v1/movies/my/rated/logs/`);
  },
};
