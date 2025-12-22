import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Genre

class Command(BaseCommand):
    help = 'TMDB API를 사용하여 영화 및 장르 데이터를 수집합니다.'

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3"
        
        # 1. 장르 수집 및 저장
        self.stdout.write('장르 데이터를 가져오는 중...')
        genre_url = f"{base_url}/genre/movie/list?api_key={api_key}&language=ko-KR"
        response = requests.get(genre_url)
        
        if response.status_code == 200:
            genres = response.json().get('genres', [])
            for g in genres:
                Genre.objects.get_or_create(id=g['id'], name=g['name'])
            self.stdout.write(self.style.SUCCESS('장르 수집 완료!'))
        
        # 2. 인기 영화 수집 (1페이지)
        self.stdout.write('영화 데이터를 가져오는 중...')
        movie_url = f"{base_url}/movie/popular?api_key={api_key}&language=ko-KR&page=1"
        movie_response = requests.get(movie_url)
        
        if movie_response.status_code == 200:
            movies = movie_response.json().get('results', [])
            for m in movies:
                # 데이터가 이미 있으면 업데이트, 없으면 생성
                movie, created = Movie.objects.update_or_create(
                    id=m['id'],
                    defaults={
                        'title': m['title'],
                        'overview': m['overview'],
                        'release_date': m.get('release_date') or None,
                        'poster_path': m.get('poster_path'),
                        'vote_average': m.get('vote_average', 0),
                        'original_language': m.get('original_language'),
                    }
                )
                # ManyToMany 관계인 장르 연결
                genre_ids = m.get('genre_ids', [])
                movie.genres.set(Genre.objects.filter(id__in=genre_ids))
            
            self.stdout.write(self.style.SUCCESS(f'{len(movies)}개의 영화 데이터 저장 완료!'))