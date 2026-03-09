/**
 * home_map.js — Carte MapLibre pour la page d'accueil.
 * Expose initHomeMap(onReady) et updateHomeMap(pks, query).
 *
 * home_map.js — MapLibre map for the home page.
 * Exposes initHomeMap(onReady) and updateHomeMap(pks, query).
 */
(function () {
    'use strict';

    var map = null;
    var mapReady = false;
    var sourceAdded = false;

    // Panneau liste / List panel
    var panelBody = null;
    var panelTitle = null;

    /**
     * Initialiser la carte. Appelle onReady quand la carte est prête.
     * Initialize the map. Calls onReady when the map is ready.
     */
    window.initHomeMap = function (onReady) {
        if (map) return;

        map = new maplibregl.Map({
            container: 'home-map',
            style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
            center: [4.88, 45.77],
            zoom: 5,
        });

        map.on('load', function () {
            mapReady = true;

            // Curseur pointer sur les marqueurs / Pointer cursor on markers
            map.on('mouseenter', 'structures-circles', function () {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'structures-circles', function () {
                map.getCanvas().style.cursor = '';
            });

            // Popup au clic / Popup on click
            map.on('click', 'structures-circles', function (e) {
                if (!e.features || e.features.length === 0) return;
                var feature = e.features[0];
                new maplibregl.Popup({ offset: 12, maxWidth: '280px' })
                    .setLngLat(feature.geometry.coordinates.slice())
                    .setHTML(buildPopupHtml(feature.properties))
                    .addTo(map);
            });

            // Créer le panneau liste / Create list panel
            createListPanel(document.getElementById('home-map').parentElement);

            if (onReady) onReady();
        });
    };

    /**
     * Charger/mettre à jour les marqueurs.
     * Load/update markers.
     */
    window.updateHomeMap = function (structurePks, searchQuery) {
        if (!map || !mapReady) return;

        // Recalculer la taille (le conteneur était peut-être hidden)
        // Recalculate size (container may have been hidden)
        map.resize();

        var url = '/map-data/';
        if (structurePks) {
            url += '?pks=' + structurePks;
        } else if (searchQuery && searchQuery.length >= 4) {
            url += '?q=' + encodeURIComponent(searchQuery);
        }

        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (geojson) {
                // Mettre à jour ou créer la source
                // Update or create the source
                if (sourceAdded) {
                    map.getSource('structures').setData(geojson);
                } else {
                    map.addSource('structures', { type: 'geojson', data: geojson });
                    map.addLayer({
                        id: 'structures-circles',
                        type: 'circle',
                        source: 'structures',
                        paint: {
                            'circle-radius': 8,
                            'circle-color': '#5b8def',
                            'circle-stroke-width': 2,
                            'circle-stroke-color': '#ffffff',
                            'circle-opacity': 0.9,
                        },
                    });
                    sourceAdded = true;
                }

                renderListPanel(geojson);

                // Recentrer / Fit bounds
                if (geojson.features && geojson.features.length > 0) {
                    var bounds = new maplibregl.LngLatBounds();
                    for (var i = 0; i < geojson.features.length; i++) {
                        bounds.extend(geojson.features[i].geometry.coordinates);
                    }
                    map.fitBounds(bounds, { padding: 60, maxZoom: 12 });
                }
            });
    };

    // --- Popup ---

    function buildPopupHtml(props) {
        var badges = [];
        try { badges = JSON.parse(props.badges); } catch (e) { badges = []; }

        var html = '<div class="home-map-popup">';
        html += '<a href="/structure-focus/' + props.pk + '/" class="home-map-popup-title">' + props.name + '</a>';

        if (badges.length > 0) {
            html += '<div class="home-map-popup-badges">';
            for (var i = 0; i < badges.length; i++) {
                html += '<span class="home-map-popup-badge"><span aria-hidden="true">&#9733;</span> ' + badges[i].name + '</span>';
            }
            if (props.badge_count > 10) {
                html += '<span class="home-map-popup-more text-muted">\u2026 et ' + (props.badge_count - 10) + ' autres</span>';
            }
            html += '</div>';
        }
        html += '</div>';
        return html;
    }

    // --- Panneau liste / List panel ---

    function createListPanel(mapParent) {
        var listBtn = document.createElement('button');
        listBtn.className = 'home-map-list-btn';
        listBtn.setAttribute('aria-label', 'Afficher la liste');
        listBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="2" width="14" height="2" rx="0.5"/><rect x="1" y="7" width="14" height="2" rx="0.5"/><rect x="1" y="12" width="14" height="2" rx="0.5"/></svg>';
        mapParent.appendChild(listBtn);

        var listPanel = document.createElement('div');
        listPanel.className = 'home-map-list-panel';
        listPanel.innerHTML = '<div class="home-map-list-panel-inner"><div class="home-map-list-panel-header"><span class="home-map-list-panel-title">Lieux</span><button class="home-map-list-panel-close" aria-label="Fermer la liste">&times;</button></div><div class="home-map-list-panel-body"></div></div>';
        mapParent.appendChild(listPanel);

        panelBody = listPanel.querySelector('.home-map-list-panel-body');
        panelTitle = listPanel.querySelector('.home-map-list-panel-title');

        listBtn.addEventListener('click', function () {
            listPanel.classList.add('open');
            listBtn.classList.add('hidden');
        });
        listPanel.querySelector('.home-map-list-panel-close').addEventListener('click', function () {
            listPanel.classList.remove('open');
            listBtn.classList.remove('hidden');
        });
    }

    function renderListPanel(geojson) {
        if (!panelBody || !geojson || !geojson.features) return;

        var count = geojson.features.length;
        panelTitle.textContent = 'Lieux (' + count + ')';

        if (count === 0) {
            panelBody.innerHTML = '<p class="home-empty-message text-muted" style="padding: 0.5rem;">Aucun lieu trouvé.</p>';
            return;
        }

        var html = '';
        for (var i = 0; i < geojson.features.length; i++) {
            var props = geojson.features[i].properties;
            var badges = [];
            try { badges = JSON.parse(props.badges); } catch (e) { badges = []; }

            html += '<a href="/structure-focus/' + props.pk + '/" class="home-map-list-item">';
            html += '<div class="home-map-list-item-header">';
            html += '<span class="home-map-list-item-icon"><svg width="12" height="12" viewBox="0 0 16 16" fill="var(--home-color-structures)"><path d="M8 1C5.2 1 3 3.7 3 6.5C3 10.5 8 15 8 15s5-4.5 5-8.5C13 3.7 10.8 1 8 1zm0 7.5a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/></svg></span>';
            html += '<span class="home-map-list-item-name">' + props.name + '</span>';
            html += '<span class="home-map-list-item-count">' + (props.badge_count || 0) + '</span>';
            html += '</div>';

            if (badges.length > 0) {
                html += '<div class="home-map-list-item-badges">';
                var maxShow = Math.min(badges.length, 3);
                for (var j = 0; j < maxShow; j++) {
                    html += '<span class="home-map-list-item-badge">&#9733; ' + badges[j].name + '</span>';
                }
                if (props.badge_count > 3) {
                    html += '<span class="home-map-list-item-badge home-map-list-item-badge-more">+' + (props.badge_count - 3) + '</span>';
                }
                html += '</div>';
            }
            html += '</a>';
        }
        panelBody.innerHTML = html;
    }

})();
