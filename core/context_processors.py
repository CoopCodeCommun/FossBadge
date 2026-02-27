# This file permit to add things to all templates context

def placeholder_image(request):
    placeholder_path = "/media/placeholder.svg"
    placeholder_dream_badge = "/media/dream_badge.svg"

    return {
        "placeholder_image": placeholder_path,
        "placeholder_dream_badge":placeholder_dream_badge
    }
