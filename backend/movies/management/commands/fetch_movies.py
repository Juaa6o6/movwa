import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Genre

class Command(BaseCommand):
    help = 'TMDB API를 사용하여 영화 및 장르 데이터를 주기적으로 수집합니다.'

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3"
        
        # 1. 장르 수집 및 저장
        self.stdout.write(self.style.SUCCESS('>>> 1. 장르 데이터 수집 시작...'))
        genre_url = f"{base_url}/genre/movie/list?api_key={api_key}&language=ko-KR"
        
        try:
            response = requests.get(genre_url)
            response.raise_for_status() # 요청 실패 시 예외 발생
            genres_data = response.json().get('genres', [])
            for g in genres_data:
                Genre.objects.get_or_create(id=g['id'], defaults={'name': g['name']})
            self.stdout.write(self.style.SUCCESS('장르 데이터 수집 완료!'))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'장르 데이터 수집 실패: {e}'))
            return

        # 2. 인기 영화 수집 (원하는 페이지 수만큼 조절)
        self.stdout.write(self.style.SUCCESS('\n>>> 2. 인기 영화 데이터 수집 시작...'))
        TOTAL_PAGES_TO_FETCH = 50 # 10 페이지 = 200개 영화

        for page in range(1, TOTAL_PAGES_TO_FETCH + 1):
            self.stdout.write(f'--- 페이지 {page}/{TOTAL_PAGES_TO_FETCH} ---')
            movie_list_url = f"{base_url}/movie/popular?api_key={api_key}&language=ko-KR&page={page}"
            
            try:
                list_response = requests.get(movie_list_url)
                list_response.raise_for_status()
                movies_data = list_response.json().get('results', [])

                for m in movies_data:
                    tmdb_id = m['id']
                    
                    # 상세 정보 API 호출
                    detail_url = f"{base_url}/movie/{tmdb_id}?api_key={api_key}&language=ko-KR&append_to_response=videos,credits"
                    
                    try:
                        detail_response = requests.get(detail_url)
                        detail_response.raise_for_status()
                        d = detail_response.json()

                        # 예고편 키 추출
                        videos = d.get('videos', {}).get('results', [])
                        youtube_key = next((v['key'] for v in videos if v.get('site') == 'YouTube' and v.get('type') == 'Trailer'), "")

                        # DB 저장
                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=tmdb_id,
                            defaults={
                                'title': d.get('title'),
                                'original_title': d.get('original_title'),
                                'overview': d.get('overview', ""),
                                'release_date': d.get('release_date') or None,
                                'runtime': d.get('runtime'),
                                'status': d.get('status', 'Released'),
                                'tagline': d.get('tagline', ""),
                                'poster_path': d.get('poster_path'),
                                'backdrop_path': d.get('backdrop_path'),
                                'youtube_key': youtube_key,
                                'popularity': d.get('popularity', 0.0),
                                'vote_average': d.get('vote_average', 0.0),
                                'vote_count': d.get('vote_count', 0),
                                'adult': d.get('adult', False),
                                'original_language': d.get('original_language', 'en'),
                                'credits': d.get('credits', {}),
                            }
                        )

                        # 장르 연결
                        genre_ids = [g['id'] for g in d.get('genres', [])]
                        movie.genres.set(Genre.objects.filter(id__in=genre_ids))
                        
                        # 진행 상황 출력
                        action = "생성" if created else "업데이트"
                        self.stdout.write(f"  - {movie.title} ({action})")

                    except requests.exceptions.RequestException as e:
                        self.stdout.write(self.style.WARNING(f'  [경고] 영화 ID {tmdb_id} 상세 정보 처리 실패: {e}'))
                    
                    # TMDB API 속도 제한을 피하기 위한 약간의 지연
                    time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'페이지 {page} 목록 처리 실패: {e}'))

        self.stdout.write(self.style.SUCCESS('\n>>> 모든 영화 데이터 수집 완료!'))