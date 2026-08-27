import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import moviesApi from '@/api/moviesApi'

export const useMovieStore = defineStore('movie', () => {
  const movie = ref(null)
  const castList = ref([])
  const crewList = ref([]) // ✨ 추가: 제작진 데이터를 담을 변수
  const youtubeUrl = ref(null)
  const isLoading = ref(false)
  const relatedVideos = ref([])
  
  // Django 서버 주소
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  let fetchGeneration = 0

  const fetchMovieDetail = async (id) => {
    isLoading.value = true
    const generation = ++fetchGeneration

    try {
      // 1. Django API에 상세 정보 요청
      const response = await axios.get(`${API_URL}/api/v1/movies/${id}/`)
      if (generation !== fetchGeneration) return

      const data = response.data

      // 2. 기본 데이터 가공
      movie.value = {
        ...data,
        // 배경 이미지가 파일명만 올 경우를 대비해 풀 경로 생성
        backdrop_path: data.backdrop_path
          ? `https://image.tmdb.org/t/p/original${data.backdrop_path}`
          : null,
        reviews: data.reviews || []
      }

      // 3. 출연진(Cast) 및 제작진(Crew) 파싱
      if (data.credits) {
        // 데이터가 문자열(JSON String)로 올 경우와 객체로 올 경우 모두 대응
        const credits = typeof data.credits === 'string' ? JSON.parse(data.credits) : data.credits

        // 출연진 상위 10명만 저장
        castList.value = credits.cast ? credits.cast.slice(0, 10) : []
        // 전체 제작진 저장 (나중에 감독을 찾기 위함)
        crewList.value = credits.crew || []
      } else {
        castList.value = []
        crewList.value = []
      }

      // 4. 유튜브 영상 주소 처리
      if (data.youtube_key) {
        youtubeUrl.value = `https://www.youtube.com/embed/${data.youtube_key}`
      } else {
        youtubeUrl.value = null
      }

      // 5. 리뷰 목록 조회
      try {
        const reviewRes = await moviesApi.getMovieReviews(id)
        if (generation === fetchGeneration) {
          movie.value.reviews = Array.isArray(reviewRes.data) ? reviewRes.data : []
        }
      } catch (reviewError) {
        console.error('리뷰 로딩 실패:', reviewError)
        if (generation === fetchGeneration) movie.value.reviews = []
      }

      // 6. 유튜브 관련 영상 조회
      try {
        const videosRes = await moviesApi.getRelatedVideos(id)
        if (generation === fetchGeneration) {
          relatedVideos.value = videosRes.data?.videos || []
        }
      } catch (videoError) {
        console.error('유튜브 영상 로딩 실패:', videoError)
        if (generation === fetchGeneration) relatedVideos.value = []
      }

    } catch (error) {
      console.error('영화 정보 로딩 실패:', error)
      if (generation === fetchGeneration) {
        movie.value = null
        relatedVideos.value = []
      }
    } finally {
      if (generation === fetchGeneration) isLoading.value = false
    }
  }

  return { 
    movie, 
    castList,
    crewList, // ✨ 반환값에 추가 필수
    youtubeUrl, 
    relatedVideos,
    isLoading, 
    fetchMovieDetail 
  }
})
