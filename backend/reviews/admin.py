from django.contrib import admin

from .models import Review, ReviewLike


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "user", "rating", "is_spoiler", "created_at")
    list_filter = ("is_spoiler", "created_at", "rating")
    search_fields = ("movie__title", "user__email", "user__username")
    ordering = ("-created_at",)


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("review__movie__title", "user__email", "user__username")
    ordering = ("-created_at",)
