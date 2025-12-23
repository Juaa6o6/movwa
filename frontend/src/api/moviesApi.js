import http from './http';

export default {
  // Movie detail (GET /movies/{id}/)
  getMovieDetail(movieId) {
    return http.get(`/movies/${movieId}/`);
  },
  // Movie reviews (GET /reviews/?movie_id=...)
  getMovieReviews(movieId) {
    return http.get(`/reviews/`, { params: { movie_id: movieId } });
  }
};
