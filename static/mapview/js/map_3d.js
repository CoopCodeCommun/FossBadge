/**
 * Logique JavaScript pour la carte hexagonale 3D Deck.gl
 * JavaScript Logic for the Deck.gl 3D Hexagon Map
 *
 * Deux modes d'affichage dans le panneau latéral :
 * 1. Vue globale : compteurs + liste des structures visibles + sélecteur de style
 * 2. Vue détail  : en-tête structure + liste des badges + sliders hexagones
 *
 * Two display modes in the side panel:
 * 1. Global view: counters + visible structures list + style selector
 * 2. Detail view: structure header + badge list + hexagon sliders
 */

(function() {
    'use strict';

    // Styles de carte disponibles (CARTO, compatible MapLibre)
    // Available map styles (CARTO, MapLibre compatible)
    const STYLES_CARTE = {
        dark: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        light: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
        streets: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json'
    };

    // Palette de couleurs pour les hexagones (jaune → orange → rouge)
    // Color palette for hexagons (yellow → orange → red)
    const PALETTE = [
        [255, 255, 0],
        [255, 215, 0],
        [255, 165, 0],
        [255, 69, 0],
        [255, 0, 0],
        [180, 0, 0],
        [128, 0, 0]
    ];

    // Couleurs CSS correspondant aux niveaux de badges
    // CSS colors matching badge levels
    const COULEURS_NIVEAUX = {
        1: '#FFD600',  // Débutant / Beginner — Jaune
        2: '#FF6D00',  // Intermédiaire / Intermediate — Orange
        3: '#B71C1C'   // Expert — Rouge foncé / Dark red
    };

    class ApplicationMap3D {
        constructor(config) {
            console.log("Initialisation Map3D...");

            this.containerId = config.containerId || 'map-container';
            this.apiUrl = config.apiUrl;
            this.structuresUrl = config.structuresUrl;

            // Structure actuellement sélectionnée (null = vue globale)
            // Currently selected structure (null = global view)
            this.structureSelectionnee = null;

            // Configuration des hexagones de badges
            // Badge hexagon configuration
            this.configHexagones = {
                radius: 5,
                elevationScale: 1,
                opacity: 0.8
            };

            // Vue initiale (sera recalculée après chargement des données)
            // Initial view (will be recalculated after data loading)
            this.viewState = {
                longitude: config.centerLng || 4.8795,
                latitude: config.centerLat || 45.7665,
                zoom: 12,
                pitch: 0,
                bearing: 0
            };

            this.data = {
                badges: [],
                structures: []
            };
            this.deck = null;

            // Timer pour le debounce de la mise à jour de la liste
            // Timer for debouncing the list update
            this._debounceTimer = null;

            this.initialiser();
        }

        async initialiser() {
            // Créer l'instance Deck.gl
            // Create the Deck.gl instance
            this.deck = new window.deck.DeckGL({
                container: this.containerId,
                initialViewState: this.viewState,
                controller: true,
                mapStyle: STYLES_CARTE.streets,
                mapLib: window.maplibregl,
                layers: [],
                onViewStateChange: ({viewState}) => {
                    this.viewState = viewState;
                    this._debounceListeStructures();
                }
            });

            // Charger les données puis centrer la carte
            // Load data then center the map
            await this.chargerDonnees();
        }

        async chargerDonnees() {
            try {
                const response = await fetch(this.apiUrl);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                this.data = await response.json();
                console.log(this.data.badges.length + ' badges et ' + this.data.structures.length + ' structures chargés.');

                // Mettre à jour les compteurs du panneau
                // Update the panel counters
                this.mettreAJourCompteurs();

                // Centrer la carte pour afficher toutes les structures
                // Center the map to show all structures
                this.calculerVueInitiale();
                this.mettreAJourCouche();
            } catch (error) {
                console.error("Erreur lors du chargement des données:", error);
                var vueGlobale = document.getElementById('vue-globale');
                if (vueGlobale) {
                    vueGlobale.innerHTML = '<div class="alert alert-danger small m-2">Erreur de chargement des données.</div>';
                }
            }
        }

        /**
         * Met à jour les compteurs en haut du panneau.
         * Updates the counters at the top of the panel.
         */
        mettreAJourCompteurs() {
            var elStructures = document.getElementById('compteur-structures');
            var elBadges = document.getElementById('compteur-badges');
            if (elStructures) elStructures.textContent = this.data.structures.length;
            if (elBadges) elBadges.textContent = this.data.badges.length;
        }

        /**
         * Calcule le zoom et le centre pour afficher toutes les structures.
         * Calculates the zoom and center to show all structures.
         */
        calculerVueInitiale() {
            var structures = this.data.structures;
            if (structures.length === 0) return;

            // Trouver les limites géographiques (bounding box)
            // Find geographic bounds (bounding box)
            var minLat = Infinity;
            var maxLat = -Infinity;
            var minLng = Infinity;
            var maxLng = -Infinity;

            for (var i = 0; i < structures.length; i++) {
                var s = structures[i];
                if (s.lat < minLat) minLat = s.lat;
                if (s.lat > maxLat) maxLat = s.lat;
                if (s.lng < minLng) minLng = s.lng;
                if (s.lng > maxLng) maxLng = s.lng;
            }

            // Ajouter un padding de 10% autour des limites
            // Add 10% padding around the bounds
            var paddingLat = (maxLat - minLat) * 0.1 || 0.005;
            var paddingLng = (maxLng - minLng) * 0.1 || 0.005;
            minLat -= paddingLat;
            maxLat += paddingLat;
            minLng -= paddingLng;
            maxLng += paddingLng;

            var centerLat = (minLat + maxLat) / 2;
            var centerLng = (minLng + maxLng) / 2;

            // Zoom le plus contraignant entre latitude et longitude
            // Most constraining zoom between latitude and longitude
            var latDiff = maxLat - minLat;
            var lngDiff = maxLng - minLng;
            var zoomLat = Math.log2(180 / latDiff) + 1;
            var zoomLng = Math.log2(360 / lngDiff) + 1;
            var zoom = Math.min(zoomLat, zoomLng, 18);

            this.deck.setProps({
                initialViewState: {
                    longitude: centerLng,
                    latitude: centerLat,
                    zoom: Math.max(zoom - 1, 2),
                    pitch: 0,
                    bearing: 0,
                    transitionDuration: 1000,
                    transitionInterpolator: new window.deck.FlyToInterpolator()
                }
            });
        }

        // =============================================
        //  GESTION DES COUCHES DECK.GL
        //  DECK.GL LAYERS MANAGEMENT
        // =============================================

        mettreAJourCouche() {
            var layers = [];

            // Couleur en fonction du poids/niveau du badge
            // Color based on badge weight/level
            var getFillColor = function(d) {
                if (d.weight <= 1) return PALETTE[0]; // Jaune / Yellow
                if (d.weight <= 2) return PALETTE[3]; // Orange
                return PALETTE[6]; // Rouge / Red
            };

            // --- Couche des badges (ColumnLayer) ---
            // Visible uniquement en vue détail (structure sélectionnée)
            // Only visible in detail view (structure selected)
            if (this.structureSelectionnee) {
                var columnLayer = new window.deck.ColumnLayer({
                    id: 'badge-layer',
                    data: this.data.badges,
                    getPosition: function(d) { return [d.lng, d.lat]; },
                    getFillColor: getFillColor,
                    getElevation: function(d) { return d.weight; },
                    elevationScale: this.configHexagones.elevationScale,
                    radius: this.configHexagones.radius,
                    diskResolution: 6,
                    extruded: true,
                    pickable: true,
                    opacity: this.configHexagones.opacity,
                    coverage: 0.9,
                    onHover: info => this.afficherTooltip(info)
                });
                layers.push(columnLayer);
            }

            // --- Couche des icônes de structures (IconLayer) ---
            // Toujours visible : les marqueurs des lieux
            // Always visible: location markers
            var selectedId = this.structureSelectionnee ? this.structureSelectionnee.structure_id : null;
            var iconLayer = new window.deck.IconLayer({
                id: 'structure-icons',
                data: this.data.structures,
                getPosition: function(d) { return [d.lng, d.lat]; },
                getIcon: function(d) {
                    return {
                        url: d.icon_url,
                        width: 48,
                        height: 72,
                        anchorY: 72,
                        mask: false
                    };
                },
                getSize: function(d) {
                    // Icône plus grande pour la structure sélectionnée
                    // Bigger icon for the selected structure
                    return (selectedId && d.structure_id === selectedId) ? 72 : 48;
                },
                sizeScale: 1,
                pickable: true,
                onClick: info => {
                    if (info.object) {
                        this.selectionnerStructure(info.object);
                    }
                },
                onHover: info => this.afficherTooltip(info),
                updateTriggers: {
                    getSize: selectedId
                }
            });
            layers.push(iconLayer);

            this.deck.setProps({ layers: layers });
        }

        // =============================================
        //  SÉLECTION / DÉSÉLECTION DE STRUCTURE
        //  STRUCTURE SELECTION / DESELECTION
        // =============================================

        /**
         * Sélectionne une structure : bascule en vue détail.
         * Selects a structure: switches to detail view.
         */
        selectionnerStructure(structure) {
            this.structureSelectionnee = structure;

            // Basculer le panneau : masquer vue globale, afficher vue détail
            // Switch panel: hide global view, show detail view
            this.afficherVueDetail(structure);

            // Zoomer sur la structure avec une vue isométrique
            // Zoom to the structure with an isometric view
            this.deck.setProps({
                initialViewState: {
                    longitude: structure.lng,
                    latitude: structure.lat,
                    zoom: 17,
                    pitch: 55,
                    bearing: 0,
                    transitionDuration: 1000,
                    transitionInterpolator: new window.deck.FlyToInterpolator()
                }
            });

            this.mettreAJourCouche();
        }

        /**
         * Revient à la vue globale.
         * Returns to the global view.
         */
        deselectionner() {
            this.structureSelectionnee = null;

            // Basculer le panneau : masquer vue détail, afficher vue globale
            // Switch panel: hide detail view, show global view
            var vueGlobale = document.getElementById('vue-globale');
            var vueDetail = document.getElementById('vue-detail');
            if (vueGlobale) vueGlobale.classList.remove('d-none');
            if (vueDetail) vueDetail.classList.add('d-none');

            this.calculerVueInitiale();
            this.mettreAJourCouche();
        }

        // =============================================
        //  RENDU DU PANNEAU LATÉRAL
        //  SIDE PANEL RENDERING
        // =============================================

        /**
         * Affiche la vue détail dans le panneau : header + badges + sliders.
         * Shows the detail view in the panel: header + badges + sliders.
         */
        afficherVueDetail(structure) {
            var vueGlobale = document.getElementById('vue-globale');
            var vueDetail = document.getElementById('vue-detail');
            if (!vueGlobale || !vueDetail) return;

            // Les badges uniques sont déjà dans les données de la structure
            // Unique badges are already in the structure data
            var badges = structure.badges || [];

            // --- En-tête de la structure ---
            // --- Structure header ---
            var headerHtml = '';
            headerHtml += '<div class="structure-header">';
            headerHtml += '  <div class="structure-header-icon">📍</div>';
            headerHtml += '  <div class="structure-header-nom">' + structure.name + '</div>';
            headerHtml += '  <div class="structure-header-type">' + (structure.type_display || '') + '</div>';

            // Description de la structure (si elle existe)
            // Structure description (if it exists)
            if (structure.description) {
                headerHtml += '  <div class="structure-header-description">' + structure.description + '</div>';
            }

            // Compteurs : badges uniques + personnes badgées
            // Counters: unique badges + badged people
            headerHtml += '  <div class="structure-header-compteur">';
            headerHtml += badges.length + ' badge' + (badges.length > 1 ? 's' : '');
            headerHtml += ' · ' + (structure.holders_count || 0) + ' personne' + ((structure.holders_count || 0) > 1 ? 's' : '') + ' badgée' + ((structure.holders_count || 0) > 1 ? 's' : '');
            headerHtml += '</div>';

            headerHtml += '</div>';

            var detailHeader = document.getElementById('detail-header');
            if (detailHeader) detailHeader.innerHTML = headerHtml;

            // --- Liste des badges uniques avec bordure colorée ---
            // --- Unique badge list with colored border ---
            var badgesHtml = '';
            badgesHtml += '<div class="section-sep">🏅 Badges forgés</div>';

            if (badges.length === 0) {
                badgesHtml += '<div class="structure-vide fst-italic">Aucun badge forgé ici.</div>';
            } else {
                badgesHtml += '<div class="d-flex flex-column gap-2">';
                for (var i = 0; i < badges.length; i++) {
                    var badge = badges[i];
                    // Couleur de la bordure gauche selon le niveau
                    // Left border color based on level
                    var couleur = COULEURS_NIVEAUX[badge.weight] || COULEURS_NIVEAUX[1];

                    badgesHtml += '<div class="badge-card" style="border-left-color:' + couleur + '">';
                    badgesHtml += '  <div class="badge-card-nom">' + badge.name + '</div>';
                    badgesHtml += '  <div class="badge-card-niveau">' + badge.level_display;
                    badgesHtml += '    <span class="badge-card-holders"> · ' + badge.holders_count + ' détenteur' + (badge.holders_count > 1 ? 's' : '') + '</span>';
                    badgesHtml += '  </div>';
                    badgesHtml += '</div>';
                }
                badgesHtml += '</div>';
            }

            var detailBadges = document.getElementById('detail-badges');
            if (detailBadges) detailBadges.innerHTML = badgesHtml;

            // Basculer la visibilité des vues
            // Toggle view visibility
            vueGlobale.classList.add('d-none');
            vueDetail.classList.remove('d-none');
        }

        // =============================================
        //  CONTRÔLES UI
        //  UI CONTROLS
        // =============================================

        setRadius(r) {
            this.configHexagones.radius = parseFloat(r);
            this.mettreAJourCouche();
        }

        setElevation(e) {
            this.configHexagones.elevationScale = parseFloat(e);
            this.mettreAJourCouche();
        }

        setOpacity(o) {
            this.configHexagones.opacity = parseFloat(o) / 100;
            this.mettreAJourCouche();
        }

        setStyle(s) {
            if (STYLES_CARTE[s]) {
                this.deck.setProps({ mapStyle: STYLES_CARTE[s] });
            }
        }

        /**
         * Navigation vers un lieu sur la carte.
         * Fly to a location on the map.
         */
        flyTo(lng, lat) {
            this.deck.setProps({
                initialViewState: {
                    longitude: lng,
                    latitude: lat,
                    zoom: 17,
                    pitch: 45,
                    transitionDuration: 1000,
                    transitionInterpolator: new window.deck.FlyToInterpolator()
                }
            });
        }

        // =============================================
        //  TOOLTIP
        // =============================================

        afficherTooltip(info) {
            var x = info.x;
            var y = info.y;
            var object = info.object;
            var layer = info.layer;
            var tooltip = document.getElementById('tooltip');

            if (object) {
                tooltip.style.display = 'block';
                tooltip.style.left = x + 'px';
                tooltip.style.top = y + 'px';

                if (layer.id === 'badge-layer') {
                    tooltip.innerHTML =
                        '<div style="font-weight:bold;color:#fb923c;margin-bottom:4px">' + object.structure + '</div>' +
                        '<div style="font-size:11px">• ' + object.name + ' (' + object.level_display + ')</div>';
                } else if (layer.id === 'structure-icons') {
                    var badgeText = object.badge_count > 0
                        ? object.badge_count + ' badge' + (object.badge_count > 1 ? 's' : '')
                        : 'Aucun badge';
                    tooltip.innerHTML =
                        '<div style="font-weight:bold;margin-bottom:4px">' + object.name + '</div>' +
                        '<div style="font-size:11px">' + badgeText + '</div>';
                }
            } else {
                tooltip.style.display = 'none';
            }
        }

        // =============================================
        //  MISE À JOUR DYNAMIQUE DE LA LISTE
        //  DYNAMIC LIST UPDATE
        // =============================================

        /**
         * Calcule les limites géographiques du viewport actuel.
         * Calculates the geographic bounds of the current viewport.
         */
        getBounds() {
            var lat = this.viewState.latitude;
            var lng = this.viewState.longitude;
            var zoom = this.viewState.zoom;

            var latRange = 180 / Math.pow(2, zoom);
            var lngRange = 360 / Math.pow(2, zoom);

            return {
                west: lng - lngRange / 2,
                east: lng + lngRange / 2,
                south: lat - latRange / 2,
                north: lat + latRange / 2
            };
        }

        /**
         * Debounce : attend 500ms avant de rafraîchir la liste.
         * Debounce: wait 500ms before refreshing the list.
         */
        _debounceListeStructures() {
            clearTimeout(this._debounceTimer);
            this._debounceTimer = setTimeout(() => {
                this.mettreAJourListeStructures();
            }, 500);
        }

        /**
         * Met à jour la liste des structures visibles sur la carte.
         * Updates the list of structures visible on the map.
         */
        mettreAJourListeStructures() {
            // Ne pas mettre à jour si on est en vue détail
            // Don't update if in detail view
            if (this.structureSelectionnee) return;

            var bounds = this.getBounds();
            var boundsParam = bounds.west + ',' + bounds.south + ',' + bounds.east + ',' + bounds.north;

            var container = document.getElementById('structure-list-container');
            if (!container) return;

            if (window.htmx) {
                window.htmx.ajax('GET', this.structuresUrl + '?bounds=' + boundsParam, {
                    target: '#structure-list-container',
                    swap: 'innerHTML'
                });
            }
        }
    }

    // =============================================
    //  DÉLÉGATION D'ÉVÉNEMENTS
    //  EVENT DELEGATION
    // =============================================

    // Clic sur une carte de structure → sélectionner
    // Click on a structure card → select
    document.addEventListener('click', function(event) {
        var card = event.target.closest('.structure-card');
        if (card && window.app) {
            var lng = parseFloat(card.dataset.lng);
            var lat = parseFloat(card.dataset.lat);
            var structureId = card.dataset.structureId;

            if (!isNaN(lng) && !isNaN(lat) && structureId) {
                var structure = window.app.data.structures.find(function(s) {
                    return s.structure_id === structureId;
                });
                if (structure) {
                    window.app.selectionnerStructure(structure);
                } else {
                    window.app.flyTo(lng, lat);
                }
            }
        }
    });

    // Exposer à la fenêtre globale
    // Expose to global window
    window.ApplicationMap3D = ApplicationMap3D;

})();
