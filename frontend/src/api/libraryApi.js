import api from './http'; 

export default {
  // 1. 나중에 볼 영화 (me -> my 로 변경 필수!)
  getSavedMovies() {
    return api.get('/api/v1/movies/my/saved/'); 
  },

  // 2. 평가한 영화 (me -> my 로 변경 필수!)
  getRatedMovies() {
    return api.get('/api/v1/movies/my/rated/');
  }
};
