"""
YouTube Data API v3 연동 헬퍼 함수
영화 관련 YouTube 영상을 검색합니다.
"""

import requests
from django.conf import settings
from typing import List, Dict, Optional


def fetch_youtube_videos(movie_title: str, max_results: int = 15) -> List[Dict]:
    """
    영화 제목으로 YouTube 관련 영상을 검색합니다.
    
    Args:
        movie_title: 영화 제목
        max_results: 최대 결과 개수 (기본 15개 = 각 쿼리당 5개씩)
    
    Returns:
        [
            {
                'video_id': 'abc123',
                'title': '영화제목 리뷰',
                'thumbnail': 'https://...',
                'channel_title': '채널명',
                'published_at': '2024-01-01',
                'query_type': 'review'  # review, 후기, 예고편
            },
            ...
        ]
    
    YouTube API가 설정되지 않았거나 오류 발생 시 빈 리스트 반환
    """
    
    # API 키 확인
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        print("⚠️ YOUTUBE_API_KEY가 설정되지 않았습니다.")
        return []
    
    # 검색 쿼리 목록 (리뷰, 후기, 예고편)
    queries = [
        (f"{movie_title} 리뷰", "review"),
        (f"{movie_title} 후기", "review"),
        (f"{movie_title} 예고편", "trailer"),
    ]
    
    all_videos = []
    
    # 각 쿼리별로 YouTube 검색
    for query, query_type in queries:
        videos = _search_youtube(query, query_type, api_key, max_results=5)
        all_videos.extend(videos)
    
    # 중복 제거 (같은 video_id)
    seen_ids = set()
    unique_videos = []
    for video in all_videos:
        if video['video_id'] not in seen_ids:
            seen_ids.add(video['video_id'])
            unique_videos.append(video)
    
    return unique_videos[:max_results]  # 최대 개수 제한


def _search_youtube(query: str, query_type: str, api_key: str, max_results: int = 5) -> List[Dict]:
    """
    YouTube Data API v3로 영상 검색 (내부 함수)
    
    Args:
        query: 검색어
        query_type: 쿼리 타입 (review, trailer)
        api_key: YouTube API 키
        max_results: 최대 결과 개수
    
    Returns:
        영상 목록
    """
    
    url = "https://www.googleapis.com/youtube/v3/search"
    
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key,
        'regionCode': 'KR',  # 한국 지역 우선
        'relevanceLanguage': 'ko',  # 한국어 우선
        'order': 'relevance',  # 관련도순 정렬
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            video_id = item.get('id', {}).get('videoId')
            snippet = item.get('snippet', {})
            
            if not video_id:
                continue
            
            videos.append({
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'description': snippet.get('description', ''),
                'query_type': query_type,
            })
        
        return videos
        
    except requests.exceptions.RequestException as e:
        print(f"❌ YouTube API 요청 실패: {e}")
        return []
    except Exception as e:
        print(f"❌ YouTube 영상 파싱 실패: {e}")
        return []
