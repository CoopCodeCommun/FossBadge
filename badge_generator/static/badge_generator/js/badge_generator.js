/*
 * JavaScript du generateur de badges — preview temps reel.
 * On utilise HTMX pour charger la previsualisation.
 * Ce fichier gere :
 * - La selection des cartes (categorie, niveau, forme)
 * - Le debounce des champs texte (titre, sous-titre)
 * - L'appel de la preview a chaque changement
 * - La generation finale du badge
 *
 * NOMS FALC : fonctions avec des noms longs et explicites.
 *
 * Badge generator JavaScript — real-time preview.
 * Uses HTMX to load preview. FALC: long explicit function names.
 *
 * LOCALISATION : badge_generator/static/badge_generator/js/badge_generator.js
 */

document.addEventListener("DOMContentLoaded", function () {

    // ================================================================
    // Variables pour stocker le minuteur de debounce.
    // On utilise un minuteur pour ne pas appeler la preview
    // a chaque frappe de clavier. On attend 300ms apres
    // la derniere frappe avant d'envoyer la requete.
    //
    // Debounce timer variable.
    // Waits 300ms after last keystroke before sending request.
    // ================================================================

    var debounce_timer_for_text_input = null;
    var DEBOUNCE_DELAY_IN_MILLISECONDS = 300;


    // ================================================================
    // Fonction : selectionner une carte dans une grille.
    // Quand on clique sur une carte, on la met en surbrillance.
    // On enleve la surbrillance des autres cartes du meme groupe.
    // On stocke la valeur dans le champ cache correspondant.
    // Gere les 3 types de cartes : categorie, niveau, forme.
    //
    // Select a card in a grid. Highlight it, unselect siblings,
    // store value in the matching hidden input.
    // Handles 3 card types: category, level, shape.
    // ================================================================

    function handle_card_selection(click_event) {
        var clicked_element = click_event.target.closest(".selection-card");

        // Si on n'a pas clique sur une carte, on ne fait rien.
        // If we didn't click a card, do nothing.
        if (!clicked_element) {
            return;
        }

        // On empeche le comportement par defaut du bouton.
        // Prevent default button behavior.
        click_event.preventDefault();

        // On cherche la grille parente pour deselectionner les autres cartes.
        // Find parent grid to deselect other cards.
        var parent_grid = clicked_element.closest(".selection-grid");
        if (parent_grid) {
            var all_cards_in_this_grid = parent_grid.querySelectorAll(".selection-card");
            for (var card_index = 0; card_index < all_cards_in_this_grid.length; card_index++) {
                all_cards_in_this_grid[card_index].classList.remove("selected");
                all_cards_in_this_grid[card_index].setAttribute("aria-checked", "false");
            }
        }

        // On ajoute la classe "selected" a la carte cliquee.
        // Add "selected" to the clicked card.
        clicked_element.classList.add("selected");
        clicked_element.setAttribute("aria-checked", "true");

        // On stocke la valeur dans le champ cache correspondant.
        // Les 3 types de cartes ont des attributs data differents.
        // Store value in the corresponding hidden input.
        // Each card type has a different data attribute.

        if (clicked_element.classList.contains("category-card")) {
            var category_uuid = clicked_element.getAttribute("data-category-uuid");
            document.getElementById("selected-category-uuid").value = category_uuid;
        }

        if (clicked_element.classList.contains("level-card")) {
            var level_uuid = clicked_element.getAttribute("data-level-uuid");
            document.getElementById("selected-level-uuid").value = level_uuid;
        }

        if (clicked_element.classList.contains("shape-card")) {
            var shape_key = clicked_element.getAttribute("data-shape-key");
            document.getElementById("selected-shape").value = shape_key;
        }

        // On met a jour la preview et le bouton generer.
        // Update preview and generate button.
        request_badge_preview();
        update_generate_button_state();
    }


    // ================================================================
    // Fonction : demander une previsualisation du badge.
    // On rassemble toutes les valeurs du formulaire
    // (categorie, niveau, forme, titre, sous-titre)
    // et on appelle le serveur pour generer le SVG.
    //
    // Request a badge preview.
    // Gather all form values and call the server to generate SVG.
    // ================================================================

    function request_badge_preview() {
        // On rassemble tous les parametres.
        // Gather all parameters.
        var category_uuid = document.getElementById("selected-category-uuid").value;
        var level_uuid = document.getElementById("selected-level-uuid").value;
        var shape_key = document.getElementById("selected-shape").value;
        var title = document.getElementById("badge-title").value;
        var subtitle = document.getElementById("badge-subtitle").value;

        // On construit l'URL de la preview avec les parametres.
        // Build preview URL with parameters.
        var preview_url = window.BADGE_PREVIEW_URL;
        var query_parameters = [];

        if (category_uuid) {
            query_parameters.push("category_uuid=" + encodeURIComponent(category_uuid));
        }
        if (level_uuid) {
            query_parameters.push("level_uuid=" + encodeURIComponent(level_uuid));
        }
        if (shape_key) {
            query_parameters.push("shape=" + encodeURIComponent(shape_key));
        }
        if (title) {
            query_parameters.push("title=" + encodeURIComponent(title));
        }
        if (subtitle) {
            query_parameters.push("subtitle=" + encodeURIComponent(subtitle));
        }

        if (query_parameters.length > 0) {
            preview_url = preview_url + "?" + query_parameters.join("&");
        }

        // On utilise HTMX pour charger la preview.
        // Use HTMX to load the preview.
        var preview_container = document.getElementById("badge-preview-container");
        if (preview_container && typeof htmx !== "undefined") {
            htmx.ajax("GET", preview_url, {
                target: "#badge-preview-container",
                swap: "innerHTML"
            });
        }
    }


    // ================================================================
    // Fonction : gerer la frappe dans les champs texte.
    // On attend 300ms apres la derniere frappe avant de demander
    // la previsualisation. C'est le "debounce".
    //
    // Handle text input with 300ms debounce before preview.
    // ================================================================

    function handle_text_input_with_debounce() {
        // On annule le minuteur precedent si il existe.
        // Cancel previous timer if it exists.
        if (debounce_timer_for_text_input !== null) {
            clearTimeout(debounce_timer_for_text_input);
        }

        // On demarre un nouveau minuteur.
        // Start a new timer.
        debounce_timer_for_text_input = setTimeout(function () {
            request_badge_preview();
            update_generate_button_state();
        }, DEBOUNCE_DELAY_IN_MILLISECONDS);
    }


    // ================================================================
    // Fonction : mettre a jour l'etat du bouton "Generer".
    // Le bouton est desactive tant que la categorie, le niveau
    // et le titre ne sont pas remplis.
    //
    // Update generate button state.
    // Disabled until category, level and title are filled.
    // ================================================================

    function update_generate_button_state() {
        var category_uuid = document.getElementById("selected-category-uuid").value;
        var level_uuid = document.getElementById("selected-level-uuid").value;
        var title = document.getElementById("badge-title").value.trim();
        var generate_button = document.getElementById("generate-button");

        if (!generate_button) {
            return;
        }

        // On active le bouton seulement si les 3 champs sont remplis.
        // Enable button only if all 3 fields are filled.
        var all_fields_are_filled = (
            category_uuid !== "" &&
            level_uuid !== "" &&
            title !== ""
        );

        generate_button.disabled = !all_fields_are_filled;
    }


    // ================================================================
    // Fonction : generer le badge (appel POST final).
    // On envoie toutes les donnees au serveur pour sauvegarder.
    // Le serveur renvoie la page de resultat.
    //
    // Generate the badge (final POST call).
    // Send all data to server to save. Server returns result page.
    // ================================================================

    function generate_badge() {
        var category_uuid = document.getElementById("selected-category-uuid").value;
        var level_uuid = document.getElementById("selected-level-uuid").value;
        var shape_key = document.getElementById("selected-shape").value;
        var title = document.getElementById("badge-title").value;
        var subtitle = document.getElementById("badge-subtitle").value;

        // On verifie que tout est rempli.
        // Check that everything is filled.
        if (!category_uuid || !level_uuid || !title.trim()) {
            return;
        }

        // On envoie la requete POST avec HTMX.
        // Le resultat remplace le contenu des deux colonnes.
        // Send POST request with HTMX. Result replaces the two-column content.
        if (typeof htmx !== "undefined") {
            htmx.ajax("POST", window.BADGE_GENERATE_URL, {
                target: ".generator-two-columns",
                swap: "innerHTML",
                values: {
                    "category_uuid": category_uuid,
                    "level_uuid": level_uuid,
                    "shape": shape_key,
                    "title": title,
                    "subtitle": subtitle
                },
                headers: {
                    "X-CSRFToken": window.CSRF_TOKEN
                }
            });
        }
    }


    // ================================================================
    // On attache les ecouteurs d'evenements.
    // Attach event listeners.
    // ================================================================

    // Clic sur les cartes de selection (delegation d'evenement sur le body).
    // Card click (event delegation on body).
    document.body.addEventListener("click", handle_card_selection);

    // Frappe dans le titre.
    // Title input.
    var title_input = document.getElementById("badge-title");
    if (title_input) {
        title_input.addEventListener("input", handle_text_input_with_debounce);
    }

    // Frappe dans le sous-titre.
    // Subtitle input.
    var subtitle_input = document.getElementById("badge-subtitle");
    if (subtitle_input) {
        subtitle_input.addEventListener("input", handle_text_input_with_debounce);
    }

    // Clic sur le bouton "Generer".
    // Generate button click.
    var generate_button = document.getElementById("generate-button");
    if (generate_button) {
        generate_button.addEventListener("click", generate_badge);
    }


});
