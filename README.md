-----

## README - Gestionnaire de Données Employés

Ce projet est une application web interactive construite avec Streamlit, conçue pour gérer efficacement les données des employés. Elle se connecte à une base de données MySQL pour permettre aux utilisateurs d'ajouter, de modifier, de supprimer et de visualiser les informations des employés via une interface conviviale. L'application offre également des outils d'analyse avancée et d'exportation de données.

### Fonctionnalités Clés

  * **Tableau de Bord Interactif :** Visualisez les métriques clés et les tendances des données des employés.
  * **Gestion Complète des Employés :** Ajoutez, mettez à jour et supprimez des enregistrements d'employés facilement.
  * **Filtrage et Recherche Avancés :** Trouvez rapidement des informations spécifiques grâce à des options de recherche et de filtrage puissantes.
  * **Analyses et Graphiques :** Obtenez des insights sur la distribution des salaires, la répartition par département, etc., grâce à des graphiques Plotly interactifs.
  * **Exportation CSV :** Téléchargez les données des employés au format CSV pour une utilisation ultérieure.
  * **Validation des Données :** Assure l'intégrité des données avec des validations intégrées pour les emails, numéros de téléphone et salaires.
  * **Mise en Cache Intelligente :** Utilise la mise en cache de Streamlit pour optimiser les performances lors du chargement des données.

### Technologies Utilisées

  * **Streamlit :** Framework Python pour la création d'applications web interactives.
  * **Pandas :** Manipulation et analyse de données.
  * **Plotly Express :** Création de visualisations de données interactives.
  * **MySQL Connector :** Connexion et interaction avec la base de données MySQL.
  * **Python :** Langage de programmation principal.

### Configuration

Pour exécuter cette application, vous aurez besoin de :

1.  **Python 3.x**
2.  **Accès à une base de données MySQL** (les informations de connexion sont codées en dur dans `DatabaseManager.get_connection()`).

#### Installation des Dépendances

Clonez ce dépôt et installez les dépendances Python requises :

```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_DOSSIER_DU_PROJET>
pip install -r requirements.txt
```

Un fichier `requirements.txt` minimal ressemblerait à ceci :

```
streamlit
pandas
mysql-connector-python
plotly
numpy
```

#### Configuration de la Base de Données

Assurez-vous que votre base de données MySQL est configurée et accessible. Le script se connecte à la base de données via les informations fournies dans le code source (hôte, nom de la base de données, utilisateur et mot de passe). Il est fortement recommandé de ne pas coder en dur ces informations sensibles directement dans le code pour un environnement de production. Utilisez plutôt des variables d'environnement ou un fichier de configuration sécurisé.

La table requise s'appelle `employees_codon` et doit avoir les colonnes suivantes : `id`, `Nom`, `Email`, `Téléphone`, `Département`, `Poste`, `Salaire`, `Pays`.

```sql
CREATE TABLE employees_codon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nom VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Téléphone VARCHAR(50),
    Département VARCHAR(100),
    Poste VARCHAR(100),
    Salaire DECIMAL(10, 2),
    Pays VARCHAR(100)
);
```

### Exécution de l'Application

Une fois les dépendances installées et la base de données configurée, exécutez l'application Streamlit depuis votre terminal :

```bash
streamlit run app.py
```

Remplacez `app.py` par le nom de votre fichier Python principal si différent. L'application s'ouvrira automatiquement dans votre navigateur web par défaut.

-----

## README - Employee Data Manager

This project is an interactive web application built with Streamlit, designed for efficient employee data management. It connects to a MySQL database, allowing users to add, modify, delete, and view employee information through a user-friendly interface. The application also provides advanced analytics tools and data export capabilities.

### Key Features

  * **Interactive Dashboard:** Visualize key metrics and trends in employee data.
  * **Comprehensive Employee Management:** Easily add, update, and delete employee records.
  * **Advanced Filtering and Search:** Quickly find specific information using powerful search and filter options.
  * **Analytics and Charts:** Gain insights into salary distribution, departmental breakdown, etc., with interactive Plotly charts.
  * **CSV Export:** Download employee data in CSV format for further use.
  * **Data Validation:** Ensures data integrity with built-in validations for emails, phone numbers, and salaries.
  * **Smart Caching:** Utilizes Streamlit's caching to optimize performance during data loading.

### Technologies Used

  * **Streamlit:** Python framework for creating interactive web applications.
  * **Pandas:** Data manipulation and analysis.
  * **Plotly Express:** Creation of interactive data visualizations.
  * **MySQL Connector:** Connecting and interacting with the MySQL database.
  * **Python:** Primary programming language.

### Setup

To run this application, you will need:

1.  **Python 3.x**
2.  **Access to a MySQL database** (connection details are hardcoded in `DatabaseManager.get_connection()`).

#### Installing Dependencies

Clone this repository and install the required Python dependencies:

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_FOLDER_NAME>
pip install -r requirements.txt
```

A minimal `requirements.txt` file would look like this:

```
streamlit
pandas
mysql-connector-python
plotly
numpy
```

#### Database Configuration

Ensure your MySQL database is set up and accessible. The script connects to the database using the information provided in the source code (host, database name, user, and password). It is highly recommended not to hardcode these sensitive details directly into the code for a production environment. Instead, use environment variables or a secure configuration file.

The required table is named `employees_codon` and should have the following columns: `id`, `Nom`, `Email`, `Téléphone`, `Département`, `Poste`, `Salaire`, `Pays`.

```sql
CREATE TABLE employees_codon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nom VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Téléphone VARCHAR(50),
    Département VARCHAR(100),
    Poste VARCHAR(100),
    Salaire DECIMAL(10, 2),
    Pays VARCHAR(100)
);
```

### Running the Application

Once the dependencies are installed and the database is configured, run the Streamlit application from your terminal:

```bash
streamlit run app.py
```

Replace `app.py` with the name of your main Python file if different. The application will automatically open in your default web browser.