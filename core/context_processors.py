# This file permit to add things to all templates context

def placeholder_image(request):
    placeholder_path = "/media/placeholder.svg"

    return {"placeholder_image": placeholder_path}
