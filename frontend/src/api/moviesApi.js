import http from './http';

export default {
  // 영화 상세 정보 조회 (GET /movies/{id}/)
  getMovieDetail(movieId) {
    return http.get(`/movies/${movieId}/`);
  },
  // 영화 리뷰 조회 (나중에 리뷰 기능 붙일 때 사용)
  getMovieReviews(movieId) {
    return http.get(`/reviews/`, { params: { movie_id: movieId } });
  }
};