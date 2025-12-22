import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useMovieStore = defineStore('movie', () => {
  const movie = ref(null)
  const castList = ref([])
  const youtubeUrl = ref(null)
  const isLoading = ref(false)
  
  // Django 서버 주소
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  const fetchMovieDetail = async (id) => {
    isLoading.value = true
    
    try {
      // 1. 진짜 DB에 요청 보내기
      // (주의: id는 DB에 저장된 그 긴 문자열이어야 함)
      const response = await axios.get(`${API_URL}/api/v1/movies/${id}/`)
      const data = response.data

      // 2. 데이터 가공 (DB랑 프론트 입맛 맞추기)
      movie.value = {
        ...data,
        // ★ 중요: DB엔 파일명만 있으니 앞에 주소를 붙여줍니다.
        backdrop_path: data.backdrop_path 
          ? `https://image.tmdb.org/t/p/original${data.backdrop_path}` 
          : null,
          
        // ★ 중요: DB에 'reviews'가 아직 없다면 빈 배열로 처리 (에러 방지)
        reviews: data.reviews || [] 
      }

      // 3. 출연진 데이터 처리 (credits 컬럼 파싱)
      // DB에서 credits가 JSON 객체로 잘 넘어오면 data.credits.cast
      // 만약 문자열로 넘어오면 JSON.parse(data.credits).cast 해야 함
      if (data.credits && data.credits.cast) {
        castList.value = data.credits.cast.slice(0, 10) // 최대 10명만
      } else {
        castList.value = []
      }

      // 4. 유튜브 영상 처리
      // DB에 youtube_key가 있다면 URL로 변환
      if (data.youtube_key) {
        youtubeUrl.value = `https://www.youtube.com/embed/${data.youtube_key}`
      } else {
        youtubeUrl.value = null
      }

    } catch (error) {
      console.error('영화 정보 로딩 실패:', error)
      movie.value = null
    } finally {
      isLoading.value = false
    }
  }

  return { 
    movie, 
    castList, 
    youtubeUrl, 
    isLoading, 
    fetchMovieDetail 
  }
})