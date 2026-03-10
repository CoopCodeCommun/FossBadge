from django.contrib import admin

from badge_generator.models import BadgeCategory, BadgeLevel, GeneratedBadge, Pictogram


@admin.register(BadgeCategory)
class BadgeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "icon", "color", "text_color", "display_order"]
    list_editable = ["display_order"]
    search_fields = ["name", "abbreviation"]


@admin.register(BadgeLevel)
class BadgeLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "rank", "posture_text", "stroke_width", "shape_sides"]
    list_editable = ["rank", "stroke_width"]
    ordering = ["rank"]


@admin.register(Pictogram)
class PictogramAdmin(admin.ModelAdmin):
    list_display = ["name", "tags"]
    search_fields = ["name", "tags"]
    filter_horizontal = ["categories"]


@admin.register(GeneratedBadge)
class GeneratedBadgeAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "level", "created_at"]
    list_filter = ["category", "level"]
    readonly_fields = ["uuid", "svg_content", "created_at"]
