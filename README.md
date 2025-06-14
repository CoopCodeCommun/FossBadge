# FossBadge

[English](#english) | [Français](#français)

<a name="english"></a>
## 🏆 FossBadge - Open Badge Platform

FossBadge is a free and open source platform for creating, managing, and sharing digital badges. It allows organizations to recognize skills and achievements through a simple, accessible interface.

### 📋 Features

- Create and manage digital badges with different skill levels (beginner, intermediate, expert)
- User profiles to showcase earned badges
- Organization/structure profiles to display available badges
- Accessible interface following FALC principles (Facile à Lire et à Comprendre / Easy to Read and Understand)
- Mobile-responsive design
- QR codes for badge verification

### 🔧 Technologies

- Django 5.2+
- Bootstrap 5
- HTMX for dynamic interactions
- SQLite database (development)
- Crispy Forms with Bootstrap 5 template pack

### 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fossbadge.git
   cd fossbadge
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Apply migrations:
   ```bash
   poetry run python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   poetry run python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   poetry run python manage.py runserver
   ```

6. Access the application at http://127.0.0.1:8000/

### 📁 Project Structure

- `core/`: Main application with views, models, and templates
- `fossbadge/`: Project settings and configuration
- `static/`: Static files (CSS, JavaScript, images)
- `templates/`: HTML templates
- `media/`: User-uploaded files (badge icons, profile pictures)

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the AGPLv3 License - see the LICENSE file for details.

---

<a name="français"></a>
## 🏆 FossBadge - Plateforme de Badges Ouverts

FossBadge est une plateforme libre et open source pour créer, gérer et partager des badges numériques. Elle permet aux organisations de reconnaître les compétences et les réalisations à travers une interface simple et accessible.

### 📋 Fonctionnalités

- Création et gestion de badges numériques avec différents niveaux de compétence (débutant, intermédiaire, expert)
- Profils utilisateurs pour présenter les badges obtenus
- Profils d'organisations/structures pour afficher les badges disponibles
- Interface accessible suivant les principes FALC (Facile à Lire et à Comprendre)
- Design responsive pour mobile
- Codes QR pour la vérification des badges

### 🔧 Technologies

- Django 5.2+
- Bootstrap 5
- HTMX pour les interactions dynamiques
- Base de données SQLite (développement)
- Crispy Forms avec le pack de templates Bootstrap 5

### 🚀 Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/yourusername/fossbadge.git
   cd fossbadge
   ```

2. Installer les dépendances avec Poetry :
   ```bash
   poetry install
   ```

3. Appliquer les migrations :
   ```bash
   poetry run python manage.py migrate
   ```

4. Créer un superutilisateur (optionnel) :
   ```bash
   poetry run python manage.py createsuperuser
   ```

5. Lancer le serveur de développement :
   ```bash
   poetry run python manage.py runserver
   ```

6. Accéder à l'application à l'adresse http://127.0.0.1:8000/

### 📁 Structure du Projet

- `core/` : Application principale avec les vues, modèles et templates
- `fossbadge/` : Paramètres et configuration du projet
- `static/` : Fichiers statiques (CSS, JavaScript, images)
- `templates/` : Templates HTML
- `media/` : Fichiers téléchargés par les utilisateurs (icônes de badges, photos de profil)

### 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

### 📄 Licence

Ce projet est sous licence AGPLv3 - voir le fichier LICENSE pour plus de détails.