import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, BoxOfficeRank

class Command(BaseCommand):
    help = 'KOBIS API에서 박스오피스 데이터를 가져와서 DB에 저장합니다.'

    def add_arguments(self, parser):
        """명령어 실행 시 옵션 추가"""
        parser.add_argument(
            '--date',
            type=str,
            help='조회할 날짜 (YYYYMMDD 형식). 미입력 시 어제 날짜 사용'
        )
        parser.add_argument(
            '--rank-type',
            type=str,
            choices=['daily', 'weekly'],
            default='daily',
            help='박스오피스 타입 (daily: 일간, weekly: 주간)'
        )
        parser.add_argument(
            '--no-auto-add',
            action='store_true',
            help='TMDB 자동 추가 비활성화 (빠르지만 매칭률 낮음)'
        )

    def handle(self, *args, **options):
        """실제 실행되는 메인 로직"""
        
        # 1. KOBIS API 키 확인
        api_key = getattr(settings, 'KOBIS_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ KOBIS_API_KEY가 설정되지 않았습니다.'))
            self.stdout.write(self.style.WARNING('settings.py에 KOBIS_API_KEY를 추가해주세요.'))
            return

        # 2. 날짜 설정 (미입력 시 어제 날짜)
        target_date = options.get('date')
        if not target_date:
            yesterday = datetime.now() - timedelta(days=1)
            target_date = yesterday.strftime('%Y%m%d')
        
        rank_type = options['rank_type']
        
        self.stdout.write(self.style.SUCCESS(f'\n📅 조회 날짜: {target_date}'))
        self.stdout.write(self.style.SUCCESS(f'📊 타입: {rank_type}\n'))

        # 3. KOBIS API 호출
        if rank_type == 'daily':
            boxoffice_data = self.fetch_daily_boxoffice(api_key, target_date)
        else:
            boxoffice_data = self.fetch_weekly_boxoffice(api_key, target_date)

        if not boxoffice_data:
            self.stdout.write(self.style.ERROR('❌ 박스오피스 데이터를 가져오지 못했습니다.'))
            return

        # 4. DB 저장
        success_count = 0
        fail_count = 0
        auto_add = not options.get('no_auto_add', False)  # 기본값: True

        if auto_add:
            self.stdout.write(self.style.SUCCESS('🔍 자동 추가 모드: TMDB에서 누락 영화 검색\n'))
        else:
            self.stdout.write(self.style.WARNING('⚡ 빠른 모드: 매칭 실패 시 건너뜀\n'))

        for rank_info in boxoffice_data:
            try:
                # 영화 매칭 (KOBIS movieNm → DB Movie.title)
                movie_title = rank_info['movieNm']
                movie = self.find_movie(movie_title, auto_add=auto_add)

                if not movie:
                    self.stdout.write(self.style.WARNING(f'⚠️  영화를 찾을 수 없음: {movie_title}'))
                    fail_count += 1
                    continue

                # BoxOfficeRank 저장 (중복 시 업데이트)
                obj, created = BoxOfficeRank.objects.update_or_create(
                    movie=movie,
                    rank_type=rank_type,
                    date=datetime.strptime(target_date, '%Y%m%d').date(),
                    defaults={
                        'rank': int(rank_info['rank']),
                        'audience_count': int(rank_info['audiCnt'])
                    }
                )

                status = '✅ 생성' if created else '🔄 업데이트'
                self.stdout.write(f'{status} | {rank_info["rank"]}위: {movie_title} ({rank_info["audiCnt"]}명)')
                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ 저장 실패: {movie_title} - {str(e)}'))
                fail_count += 1

        # 5. 결과 요약
        self.stdout.write(self.style.SUCCESS(f'\n🎉 완료! 성공: {success_count}개, 실패: {fail_count}개'))


    def fetch_daily_boxoffice(self, api_key, target_date):
        """일간 박스오피스 조회"""
        url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json'
        params = {
            'key': api_key,
            'targetDt': target_date
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data['boxOfficeResult']['dailyBoxOfficeList']
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API 요청 실패: {e}'))
            return None
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'응답 데이터 파싱 실패: {e}'))
            return None


    def fetch_weekly_boxoffice(self, api_key, target_date):
        """주간 박스오피스 조회"""
        url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json'
        params = {
            'key': api_key,
            'targetDt': target_date,
            'weekGb': '0'  # 0: 주간, 1: 주말, 2: 주중
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data['boxOfficeResult']['weeklyBoxOfficeList']
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API 요청 실패: {e}'))
            return None
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'응답 데이터 파싱 실패: {e}'))
            return None


    def find_movie(self, kobis_title, auto_add=False):
        """
        KOBIS 영화 제목으로 DB에서 Movie 찾기
        매칭 우선순위:
        1. 제목 정확 일치
        2. 원제 정확 일치
        3. 정규화 후 비교 (띄어쓰기/특수문자 제거)
        4. 핵심 키워드 추출 후 검색
        5. (auto_add=True인 경우) TMDB API 검색 후 추가
        """
        # 1. 정확 일치 (한글 제목)
        movie = Movie.objects.filter(title__iexact=kobis_title).first()
        if movie:
            return movie

        # 2. 정확 일치 (원제)
        movie = Movie.objects.filter(original_title__iexact=kobis_title).first()
        if movie:
            return movie

        # 3. 정규화된 제목으로 비교 (띄어쓰기/특수문자 제거)
        normalized_kobis = self.normalize_title(kobis_title)
        
        for movie in Movie.objects.all():
            if self.normalize_title(movie.title) == normalized_kobis:
                self.stdout.write(f'📌 정규화 매칭: {kobis_title} → {movie.title}')
                return movie
            if self.normalize_title(movie.original_title) == normalized_kobis:
                self.stdout.write(f'📌 정규화 매칭(원제): {kobis_title} → {movie.original_title}')
                return movie

        # 4. 핵심 키워드 추출 후 검색 (극장판, 더 무비 등 제거)
        core_keyword = self.extract_core_keyword(kobis_title)
        if core_keyword:
            movie = Movie.objects.filter(title__icontains=core_keyword).first()
            if movie:
                self.stdout.write(f'📌 키워드 매칭: {kobis_title} → {movie.title}')
                return movie
            
            movie = Movie.objects.filter(original_title__icontains=core_keyword).first()
            if movie:
                self.stdout.write(f'📌 키워드 매칭(원제): {kobis_title} → {movie.original_title}')
                return movie

        # 5. TMDB 자동 추가 (옵션 활성화 시)
        if auto_add:
            movie = self.search_and_create_from_tmdb(kobis_title)
            if movie:
                return movie

        return None


    def normalize_title(self, title):
        """
        제목 정규화: 띄어쓰기, 특수문자 제거하고 소문자 변환
        예: "극장판 체인소 맨: 레제편" → "극장판체인소맨레제편"
        """
        import re
        if not title:
            return ""
        # 띄어쓰기, 콜론, 하이픈, 마침표 등 제거
        normalized = re.sub(r'[\s\:\-\.\,]', '', title)
        return normalized.lower()


    def extract_core_keyword(self, title):
        """
        핵심 키워드 추출: 불필요한 접두사/접미사 제거
        예: "극장판 체인소 맨: 레제편" → "체인소 맨"
        """
        import re
        
        # 제거할 접두사/접미사 목록
        prefixes = ['극장판', '더 무비', '더무비', '극장판:', '극장판 ']
        suffixes = ['편', '더 무비', '더무비']
        
        # 접두사 제거
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        # 콜론 뒤 부분 제거 (부제 제거)
        if ':' in title:
            title = title.split(':')[0].strip()
        
        # 너무 짧으면 None 반환
        if len(title) < 2:
            return None
        
        return title


    def search_and_create_from_tmdb(self, title):
        """
        TMDB API로 영화 검색 후 DB에 추가
        Args:
            title: 검색할 영화 제목
        Returns:
            Movie 객체 or None
        """
        import time
        
        api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not api_key:
            return None
        
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': title,
            'language': 'ko-KR'
        }
        
        try:
            self.stdout.write(f'🔍 TMDB 검색 중: {title}')
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            if not results:
                self.stdout.write(self.style.WARNING(f'  ❌ TMDB에서도 찾을 수 없음'))
                return None
            
            # 첫 번째 결과 사용
            movie_data = results[0]
            tmdb_id = movie_data['id']
            
            # 이미 DB에 있는지 확인 (tmdb_id로)
            existing = Movie.objects.filter(tmdb_id=tmdb_id).first()
            if existing:
                self.stdout.write(f'  ℹ️  이미 존재 (tmdb_id 일치): {existing.title}')
                return existing
            
            # 상세 정보 가져오기
            detail_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            detail_params = {
                'api_key': api_key,
                'language': 'ko-KR',
                'append_to_response': 'videos,credits'
            }
            
            detail_response = requests.get(detail_url, params=detail_params)
            detail_response.raise_for_status()
            detail = detail_response.json()
            
            # Movie 생성
            movie = Movie.objects.create(
                tmdb_id=tmdb_id,
                title=detail.get('title', ''),
                original_title=detail.get('original_title', ''),
                overview=detail.get('overview', ''),
                poster_path=detail.get('poster_path', ''),
                backdrop_path=detail.get('backdrop_path', ''),
                release_date=detail.get('release_date') or None,
                vote_average=detail.get('vote_average', 0),
                vote_count=detail.get('vote_count', 0),
                popularity=detail.get('popularity', 0),
                runtime=detail.get('runtime', 0),
                original_language=detail.get('original_language', '')
            )
            
            # 장르 추가
            from movies.models import Genre
            genre_ids = detail.get('genre_ids', []) or [g['id'] for g in detail.get('genres', [])]
            for genre_id in genre_ids:
                genre = Genre.objects.filter(id=genre_id).first()
                if genre:
                    movie.genres.add(genre)
            
            self.stdout.write(self.style.SUCCESS(f'  ✨ TMDB에서 추가됨: {movie.title}'))
            
            # API 호출 제한 방지 (0.3초 대기)
            time.sleep(0.3)
            
            return movie
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'  ❌ TMDB API 오류: {e}'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 생성 실패: {e}'))
            return None
