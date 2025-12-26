import time

from django.conf import settings
from django.core.management.base import BaseCommand

from openai import OpenAI

from movies.models import Movie, MovieEmbedding


class Command(BaseCommand):
    help = "Generate OpenAI embeddings for movies"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of movies to process at once",
        )
        parser.add_argument(
            "--sleep-every",
            type=int,
            default=50,
            help="Sleep every N requests (default: 50)",
        )
        parser.add_argument(
            "--sleep-seconds",
            type=int,
            default=60,
            help="Sleep duration in seconds (default: 60)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate embeddings even if they exist",
        )

    def handle(self, *args, **options):
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            self.stderr.write("OPENAI_API_KEY is missing in settings.")
            return

        base_url = getattr(settings, "OPENAI_BASE_URL", "") or None
        self.stdout.write(f"Using OPENAI_API_KEY prefix: {api_key[:8]}")
        if base_url:
            self.stdout.write(f"Using OPENAI_BASE_URL: {base_url}")
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        batch_size = options["batch_size"]
        sleep_every = options["sleep_every"]
        sleep_seconds = options["sleep_seconds"]
        force = options["force"]

        if force:
            movies = Movie.objects.all()
        else:
            existing_ids = MovieEmbedding.objects.values_list("movie_id", flat=True)
            movies = Movie.objects.exclude(id__in=existing_ids)

        total = movies.count()
        self.stdout.write(f"Processing {total} movies...")

        for idx, movie in enumerate(movies.iterator(), 1):
            try:
                genres_text = ", ".join([g.name for g in movie.genres.all()])
                text = f"Genres: {genres_text}\nOverview: {movie.overview or ''}"
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text,
                    encoding_format="float",
                )
                vector = response.data[0].embedding

                MovieEmbedding.objects.update_or_create(
                    movie=movie,
                    defaults={
                        "vector": vector,
                        "model_version": "text-embedding-3-small",
                    },
                )
                self.stdout.write(f"[{idx}/{total}] {movie.title}")

                if sleep_every > 0 and idx % sleep_every == 0:
                    time.sleep(max(0, sleep_seconds))
            except Exception as exc:
                self.stderr.write(f"Failed: {movie.title} - {exc}")
