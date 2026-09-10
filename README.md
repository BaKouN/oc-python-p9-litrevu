# LITRevu

Application web de critiques de livres et d'articles, réalisée pour le projet 9 du parcours
Développeur d'application Python d'OpenClassrooms. Un utilisateur publie des **billets**
(demandes de critique), rédige des **critiques** en réponse, et **suit** d'autres utilisateurs
pour composer son flux.

Django 6.1 · Python 3.14 · SQLite · rendu côté serveur (MVT), sans API ni framework JS.

## Installation

```bash
git clone https://github.com/BaKouN/oc-python-p9-litrevu.git
cd oc-python-p9-litrevu
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Ouvrir <http://127.0.0.1:8000/>. La base SQLite fournie contient déjà les données de test :
aucune migration ni création de compte n'est nécessaire.

Pour repartir d'une base vide :

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Identifiants de test

| Utilisateur | Mot de passe   | Rôle                        |
|-------------|----------------|-----------------------------|
| `bakoon`    | `Litrevu-2026` | superutilisateur (`/admin/`) |
| `irina`     | `Litrevu-2026` | utilisateur standard         |

## Fonctionnalités

- Inscription, connexion, déconnexion
- Billets : créer (avec image), modifier, supprimer — réservé à l'auteur
- Critiques : créer en réponse à un billet, ou billet + critique en une fois ; modifier, supprimer — réservé à l'auteur
- Une seule critique par utilisateur et par billet
- À venir : flux combiné billets + critiques, abonnements

## Structure

```
litrevu/     configuration du projet (settings, urls racine)
reviews/     application : modèles, formulaires, vues, urls, admin
templates/   gabarits HTML (base.html + registration/ + reviews/)
media/       images uploadées (ignoré par git)
```

## Choix techniques

- **Modèle `User` personnalisé** (`AbstractUser`) déclaré avant la première migration.
- **Vues fonctions** pour l'application, vues génériques Django (`LoginView`, `LogoutView`) pour l'authentification.
- **Suppressions en POST uniquement**, avec page de confirmation ; toute modification vérifie `request.user == auteur`.
- **Accessibilité** : `lang="fr"`, lien d'évitement, landmarks, `fieldset`/`legend`, textes alternatifs.
