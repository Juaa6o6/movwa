import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

// 1. 여기서 export const가 꼭 있어야 합니다!
export const useMovieStore = defineStore('movie', () => {
  const movie = ref(null)
  const castList = ref([])
  const youtubeUrl = ref(null)
  const isLoading = ref(false)

  const fetchMovieDetail = async (id) => {
    isLoading.value = true
    
    // --- [가짜 데이터 로직 시작] ---
    setTimeout(() => {
      // 1. 영화 상세 정보
      movie.value = {
        id: id,
        title: "범죄도시 4 (가짜 데이터)",
        overview: "괴물형사 마석도, 이번엔 필리핀이다! 더 커진 판, 더 악랄한 빌런, 그리고 더 강력해진 웃음으로 돌아왔다. 대한민국 대표 범죄 액션 시리즈.",
        release_date: "2024-04-24",
        runtime: 109,
        vote_average: 8.5,
        genres: [{ id: 1, name: "액션" }, { id: 2, name: "범죄" }],
        backdrop_path: "https://image.tmdb.org/t/p/original/kKsxcgf9O4Xz0d8xHkZ4o0Zk8j.jpg",
        
        // 2. 가짜 리뷰 데이터 (이게 있어야 오른쪽 탭에 나옵니다!)
        reviews: [
          { id: 1, user: "마동석팬", content: "진실의 방으로...", rating: 5, date: "2024-05-01" },
          { id: 2, user: "영화광", content: "타격감 하나는 끝내주네요. 시간 가는 줄 몰랐음.", rating: 4.5, date: "2024-05-02" },
          { id: 3, user: "팝콘러", content: "장이수가 이번에 진짜 웃김 ㅋㅋㅋ", rating: 4, date: "2024-05-03" },
          { id: 4, user: "비평가", content: "스토리는 뻔하지만 아는 맛이 무섭다.", rating: 3.5, date: "2024-05-04" },
          { id: 5, user: "ssafy_student", content: "코딩하다가 머리 식히러 왔는데 재밌어요!", rating: 5, date: "2024-05-05" },
        ]
      }

      // 3. 가짜 출연진
      castList.value = [
        { name: "마동석" },
        { name: "김무열" },
        { name: "박지환" },
        { name: "이동휘" },
        { name: "이주빈" }
      ]

      // 4. 가짜 유튜브 링크 (아무거나)
      youtubeUrl.value = "https://www.youtube.com/embed/j_N6kL8b7V8"

      isLoading.value = false
    }, 500) // 0.5초 로딩 흉내
    // --- [가짜 데이터 로직 끝] ---
  }

  // 2. 중요!! 여기서 return을 안 해주면 밖에서 못 씁니다.
  return { 
    movie, 
    castList, 
    youtubeUrl, 
    isLoading, 
    fetchMovieDetail 
  }
})