from datetime import timedelta

import numpy as np
from django.utils import timezone
from sklearn.metrics.pairwise import cosine_similarity

from movies.models import Movie, MovieEmbedding, UserMovieLog


class MovieRecommender:
    def __init__(self, user):
        self.user = user

    def get_batch_recommendations(self, batch_size=10, exclude_movie_ids=None):
        exclude_movie_ids = set(exclude_movie_ids or [])
        interacted_ids = UserMovieLog.objects.filter(
            user=self.user
        ).values_list("movie_id", flat=True)
        exclude_movie_ids.update([str(mid) for mid in interacted_ids])

        has_logs = UserMovieLog.objects.filter(user=self.user).exists()
        has_ratings = UserMovieLog.objects.filter(
            user=self.user, rating__isnull=False
        ).exists()
        recent_like_ids = list(
            UserMovieLog.objects.filter(
                user=self.user,
                is_liked=True,
                updated_at__gte=timezone.now() - timedelta(minutes=30),
            ).values_list("movie_id", flat=True)
        )

        if not has_logs:
            return self._cold_start(batch_size, exclude_movie_ids)

        if not recent_like_ids:
            return self._explore_mode(batch_size, exclude_movie_ids, has_ratings)

        return self._immersive_mode(batch_size, exclude_movie_ids, recent_like_ids, has_ratings)

    def _cold_start(self, n, exclude_ids):
        trending = self._popular_movies(n=8, exclude_ids=exclude_ids)
        exclude_ids.update([str(m.id) for m in trending])
        randoms = self._random_movies(n=n - len(trending), exclude_ids=exclude_ids)
        return (trending + randoms)[:n]

    def _explore_mode(self, n, exclude_ids, has_ratings):
        recs = []
        if has_ratings:
            long_term = self._long_term_recommendations(5, exclude_ids)
            recs.extend(long_term)
            exclude_ids.update([str(m.id) for m in long_term])

        trending = self._popular_movies(n=3, exclude_ids=exclude_ids)
        recs.extend(trending)
        exclude_ids.update([str(m.id) for m in trending])

        randoms = self._random_movies(n=n - len(recs), exclude_ids=exclude_ids)
        recs.extend(randoms)
        return recs[:n]

    def _immersive_mode(self, n, exclude_ids, recent_like_ids, has_ratings):
        recs = []
        short_term = self._short_term_recommendations(7, exclude_ids, recent_like_ids)
        recs.extend(short_term)
        exclude_ids.update([str(m.id) for m in short_term])

        if has_ratings:
            long_term = self._long_term_recommendations(2, exclude_ids)
            recs.extend(long_term)
            exclude_ids.update([str(m.id) for m in long_term])

        randoms = self._random_movies(n=n - len(recs), exclude_ids=exclude_ids)
        recs.extend(randoms)
        return recs[:n]

    def _popular_movies(self, n, exclude_ids):
        if n <= 0:
            return []
        return list(
            Movie.objects.exclude(id__in=exclude_ids)
            .order_by("-popularity", "-vote_average")[:n]
        )

    def _random_movies(self, n, exclude_ids):
        if n <= 0:
            return []
        return list(Movie.objects.exclude(id__in=exclude_ids).order_by("?")[:n])

    def _short_term_recommendations(self, n, exclude_ids, like_ids):
        liked_movies = list(Movie.objects.filter(id__in=like_ids))
        return self._get_similar_movies(liked_movies, n, exclude_ids)

    def _long_term_recommendations(self, n, exclude_ids):
        high_rated = list(
            UserMovieLog.objects.filter(user=self.user, rating__gte=4.0)
            .select_related("movie")
            .order_by("-rating")[:5]
        )
        base_movies = [log.movie for log in high_rated]
        return self._get_similar_movies(base_movies, n, exclude_ids)

    def _get_similar_movies(self, reference_movies, n, exclude_ids):
        if n <= 0 or not reference_movies:
            return []

        vectors = []
        for movie in reference_movies:
            try:
                vectors.append(movie.embedding.vector)
            except MovieEmbedding.DoesNotExist:
                continue

        if not vectors:
            return []

        avg_vector = np.mean(np.array(vectors), axis=0).reshape(1, -1)
        candidates = MovieEmbedding.objects.exclude(
            movie_id__in=list(exclude_ids)
        ).select_related("movie")

        scored = []
        for emb in candidates:
            candidate_vector = np.array(emb.vector).reshape(1, -1)
            score = cosine_similarity(avg_vector, candidate_vector)[0][0]
            scored.append((emb.movie, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, _ in scored[:n]]
