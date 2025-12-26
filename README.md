---

# MOVWA – 인터랙션 기반 영화 추천 플랫폼

## 💡 프로젝트 소개

**MOVWA**는 “오늘 뭐 보지?”라는 선택의 피로를 줄이기 위해
**10개 한정 마이크로 큐레이션**과 **직관적인 버튼 인터랙션**을 중심으로 설계된 AI 기반 영화 추천 웹 플랫폼입니다.

* **진행 기간** : 2025. 12. ~ 2025. 12.
* **소개** : PASS / LIKE / RATE / SAVE 인터랙션을 통해
  사용자의 취향을 빠르게 학습하고,
  매번 새로운 추천 경험을 제공하는 영화 큐레이션 서비스

---

## ⚙ 팀 구성

|      이름      |                역할                |
| :----------: | :------------------------------: |
| **박주형** (팀장) | 기획, 백엔드, 프론트엔드, API/DB 설계, AI 추천 로직 설계  |
|    **김태연**   |  기획, 프론트엔드,  컴포넌트 구조 설계   |

---

## 🧬 주요 서비스 기능

### 🎬 메인 영화 추천 (10-Pick Curation)

* AI 기반 영화 추천 **10개 카드만 제공**
* 카드 Hover 2초 → **예고편 자동 재생**
* PASS / LIKE / RATE / SAVE 버튼 인터랙션
* 모든 카드 소진 시 **새 추천 요청 가능**

### 📂 이원화 보관함 시스템

* **Daily Like**

  * LIKE한 영화 저장
  * 24시간 후 자동 초기화
* **My Archive**

  * SAVE한 영화 영구 저장

### 📄 영화 상세 페이지

* 예고편 재생
* 줄거리, 장르, 감독, 출연진 정보 제공
* 별점 및 리뷰 작성 / 조회
* 유사 영화 추천
* 시청 가능한 OTT 플랫폼 안내

### 🔍 검색 & 탐색

* 영화 제목 기반 통합 검색
* 추천순 / 인기순 / 최신순 정렬
* 장르별 영화 탐색

### 👤 사용자 프로필

* 내가 평가한 영화 목록
* 저장 / 좋아요 영화 관리
* 작성한 리뷰 확인

### 🛠 관리자 기능

* 영화 데이터 CRUD
* 회원 관리
* 리뷰/평점 모니터링

---

## 🎯 기획 / 차별화 포인트

* **무한 스크롤 제거**
* **선택지를 10개로 제한**
* 즉각적인 버튼 인터랙션 기반 추천
* LIKE와 SAVE를 분리한 보관함 설계
* UX 흐름을 최우선으로 고려한 구조

---

## 추천 시스템 요약
임베딩은 **OpenAI `text-embedding-3-small`**(1536차원) 기반입니다.  
추천 로직은 사용자 상태에 따라 **동적 비율**로 배치 추천을 구성합니다.

- **콜드 스타트**: 인기 8 + 랜덤 2  
- **탐색 모드**(최근 Like 없음): 장기 취향 5 + 인기 3 + 랜덤 2  
- **몰입 모드**(최근 Like 있음): 단기 취향 7 + 장기 취향 2 + 랜덤 1

추천/피드백 API는 다음 흐름으로 연결됩니다:
1) `GET /api/v1/movies/recommendations/batch/`  
2) `POST /api/v1/movies/<uuid>/feedback/` (like/pass/rate)

## 기술 스택
**Backend**
- Python, Django, DRF, dj-rest-auth, SimpleJWT
- OpenAI SDK (GMS OpenAI 호환 엔드포인트 지원)
- SQLite (개발 기본)

**Frontend**
- Vue 3, Vite, Pinia, Vuetify
- Axios

## 프로젝트 구조
```
movwa/
  backend/
    accounts/   movies/   reviews/   config/
  frontend/
    src/
      api/      components/  views/  stores/
  docs/ref/     # API/DB/SRS/추천 명세서
```

## 환경 변수
`backend/.env`에 아래 값을 설정합니다.
```
TMDB_API_KEY=...
KOBIS_API_KEY=...
YOUTUBE_API_KEY=...
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1
```
- `OPENAI_BASE_URL`은 GMS OpenAI 호환 엔드포인트 사용 시에만 필요합니다.

## 로컬 실행
### Backend
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```
cd frontend
npm install
npm run dev
```

## 임베딩 생성
```
cd backend
python manage.py generate_embeddings
```
속도 조절 옵션:
```
python manage.py generate_embeddings --sleep-every 100 --sleep-seconds 10
```

## 주요 API (요약)
### Auth
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/registration/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/user/`

### Movies / 추천
- `GET /api/v1/movies/`
- `GET /api/v1/movies/search/`
- `GET /api/v1/movies/boxoffice/`
- `GET /api/v1/movies/recommendations/batch/`
- `POST /api/v1/movies/<uuid>/feedback/`
- `POST /api/v1/movies/<uuid>/like/`
- `POST /api/v1/movies/<uuid>/save/`
- `POST /api/v1/movies/<uuid>/rate/`

### Reviews
- `GET /api/v1/reviews/`
- `POST /api/v1/reviews/`

## 데이터 모델 개요
주요 모델은 `Movie`, `UserMovieLog`, `MovieEmbedding`, `Review`, `ReviewLike`로 구성됩니다.  
자세한 관계/속성은 `docs/ref/DB 명세서_movies.pdf`를 참고하세요.

## 문서
- `docs/ref/API 명세서_movies.pdf`
- `docs/ref/DB 명세서_movies.pdf`
- `docs/ref/SRS 명세서_movies.pdf`
- `docs/ref/추천_기능_구현.pdf`

---

## 느낀점

### 박주형

서비스 개발 프로젝트를 처음으로 주도하며 기획과 문서화의 중요성을 다시 한 번 체감했습니다.
초반에 탄탄하게 준비한 기획 덕분에 개발 과정에서 방향성을 잃지 않고 진행할 수 있었고, 
팀원과의 소통도 훨씬 명확해져 문제 발생 시 빠르게 대응할 수 있었습니다.

또한 기획부터 프론트엔드, 백엔드까지 전반적인 개발 과정을 경험하며, 
배운 지식을 실제 서비스에 적용하는 방법과 개발 워크플로우에 대한 이해도를 높일 수 있었습니다.
특히 백엔드와 프론트엔드를 연동하는 과정에서 예상치 못한 이슈들을 해결하며 실무적인 문제 해결 경험과 큰 성취감을 얻었습니다.


### 김태연

처음에 너무 막막했는데 프로젝트 진행하면서 팀원과 함께 기획도 직접 해볼 수 있어서 좋았습니다.
구현하는데 많이 더뎠지만 탄탄한 기획 덕에 시행착오를 줄였던 것 같습니다.

그리고 프론트가 페이지만 만드는게 다가 아니라는 걸 뒤늦게 깨달았습니다.
팀원이 없었으면 낙동강 오리알이 되었을 것 같습니다. 정말 감사한 프로젝트 경험이었습니다.

---

## 👫 저작권 및 오픈소스 안내

본 프로젝트는 교육 목적의 비상업적 프로젝트입니다.

