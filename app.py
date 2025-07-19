import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, Any

# Configuration de la page
st.set_page_config(
    page_title="Excel Data Manager Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look professionnel
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Classes pour la gestion des données
class DatabaseManager:
    @staticmethod
    def get_connection(host=st.secrets["db_host"], user=st.secrets["db_user"],
                       password=st.secrets["db_password"], database=st.secrets["db_name"]):
        """Créer une nouvelle connexion à chaque appel"""
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                autocommit=True,
                connection_timeout=10
            )
            return conn
        except mysql.connector.Error as e:
            st.error(f"Erreur de connexion à la base de données : {str(e)}")
            return None
    
    @staticmethod
    @st.cache_data(ttl=30)  # Cache pendant 30 secondes seulement
    def load_data():
        """Charger les données avec gestion d'erreur"""
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            if conn is None:
                return pd.DataFrame()
            
            query = "SELECT * FROM employees_codon;"
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            return pd.DataFrame()
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch: bool = False):
        """Exécuter une requête avec gestion robuste des connexions"""
        conn = None
        cursor = None
        try:
            conn = DatabaseManager.get_connection()
            if conn is None:
                return False
                
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return True
                
        except mysql.connector.Error as e:
            st.error(f"Erreur de base de données : {str(e)}")
            return False
        except Exception as e:
            st.error(f"Erreur inattendue : {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

class DataValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        # Pattern simple pour téléphone
        pattern = r'^[\+]?[1-9][\d]{0,15}$'
        return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None
    
    @staticmethod
    def validate_salary(salary: float) -> bool:
        return salary > 0 and salary <= 1000000000

class EmployeeManager:
    @staticmethod
    def add_employee(nom: str, email: str, tel: str, departement: str, poste: str, salaire: float, pays: str) -> Dict[str, Any]:
        # Validation des données
        errors = []
        if not nom or len(nom) < 2:
            errors.append("Le nom doit contenir au moins 2 caractères")
        if not DataValidator.validate_email(email):
            errors.append("Format d'email invalide")
        if not DataValidator.validate_phone(tel):
            errors.append("Format de téléphone invalide")
        if not DataValidator.validate_salary(salaire):
            errors.append("Le salaire doit être entre 0 et 1 000 000 000 FCFA")
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Vérifier l'unicité de l'email
        existing = DatabaseManager.execute_query(
            "SELECT id FROM employees_codon WHERE Email=%s", (email,), fetch=True
        )
        if existing:
            return {"success": False, "errors": ["Cet email est déjà utilisé"]}
        
        # Insérer l'employé
        success = DatabaseManager.execute_query(
            """INSERT INTO employees_codon (Nom, Email, Téléphone, Département, Poste, Salaire, Pays)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (nom, email, tel, departement, poste, salaire, pays)
        )
        
        if success:
            st.cache_data.clear()  # Vider le cache pour actualiser les données
            return {"success": True, "message": "✅ Employé ajouté avec succès ✅"}
        else:
            return {"success": False, "errors": ["❌ Erreur lors de l'ajout ❌"]}
    
    @staticmethod
    def update_employee(emp_id: int, nom: str, email: str, tel: str, departement: str, poste: str, salaire: float, pays: str) -> Dict[str, Any]:
        # Même validation que pour l'ajout
        errors = []
        if not nom or len(nom) < 2:
            errors.append("Le nom doit contenir au moins 2 caractères")
        if not DataValidator.validate_email(email):
            errors.append("Format d'email invalide")
        if not DataValidator.validate_phone(tel):
            errors.append("Format de téléphone invalide")
        if not DataValidator.validate_salary(salaire):
            errors.append("Le salaire doit être entre 0 et 1 000 000 000 FCFA")
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Vérifier l'unicité de l'email (sauf pour l'employé actuel)
        existing = DatabaseManager.execute_query(
            "SELECT id FROM employees_codon WHERE Email=%s AND id != %s", (email, emp_id), fetch=True
        )
        if existing:
            return {"success": False, "errors": ["❌ Cet email est déjà utilisé par un autre employé ❌"]}
        
        success = DatabaseManager.execute_query(
            """UPDATE employees_codon SET Nom=%s, Email=%s, Téléphone=%s, Département=%s, Poste=%s, Salaire=%s, Pays=%s
               WHERE id=%s""",
            (nom, email, tel, departement, poste, salaire, pays, emp_id)
        )
        
        if success:
            st.cache_data.clear()
            return {"success": True, "message": "✅ Employé mis à jour avec succès ✅"}
        else:
            return {"success": False, "errors": ["❌ Erreur lors de la mise à jour ❌"]}
    
    @staticmethod
    def delete_employee(emp_id: int) -> Dict[str, Any]:
        success = DatabaseManager.execute_query("DELETE FROM employees_codon WHERE id=%s", (emp_id,))
        if success:
            st.cache_data.clear()
            return {"success": True, "message": f"✅ Employé ID {emp_id} supprimé avec succès ✅"}
        else:
            return {"success": False, "errors": ["❌ Erreur lors de la suppression ❌"]}

def display_message(result: Dict[str, Any]):
    if result["success"]:
        st.success(result["message"])
    else:
        for error in result["errors"]:
            st.error(error)

def create_advanced_dashboard(df: pd.DataFrame):
    """Créer un dashboard avancé avec graphiques interactifs"""
    
    # Métriques principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(df):,}</h3>
            <p>Total Employés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_salary = df['Salaire'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{avg_salary:,.0f} FCFA</h3>
            <p>Salaire Moyen</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{df['Département'].nunique()}</h3>
            <p>Départements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{df['Pays'].nunique()}</h3>
            <p>Pays</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{df['Poste'].nunique()}</h3>
            <p>Postes</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques avancés
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des salaires par département
        fig_salary = px.box(df, x='Département', y='Salaire', 
                           title='Distribution des Salaires par Département',
                           color='Département')
        fig_salary.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_salary, use_container_width=True)
    
    with col2:
        # Répartition géographique
        country_counts = df['Pays'].value_counts().head(10)
        fig_geo = px.pie(values=country_counts.values, names=country_counts.index,
                        title='Répartition Géographique (Top 10)')
        fig_geo.update_layout(height=400)
        st.plotly_chart(fig_geo, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Analyse par poste
        poste_salary = df.groupby('Poste')['Salaire'].agg(['mean', 'count']).reset_index()
        poste_salary = poste_salary[poste_salary['count'] >= 3]  # Filtrer les postes avec au moins 3 employés
        
        fig_poste = px.scatter(poste_salary, x='count', y='mean', 
                              text='Poste', title='Salaire Moyen vs Nombre d\'Employés par Poste',
                              labels={'count': 'Nombre d\'Employés', 'mean': 'Salaire Moyen'})
        fig_poste.update_traces(textposition="top center")
        fig_poste.update_layout(height=400)
        st.plotly_chart(fig_poste, use_container_width=True)
    
    with col4:
        # Top 10 des salaires
        top_salaries = df.nlargest(10, 'Salaire')[['Nom', 'Salaire', 'Poste']]
        fig_top = px.bar(top_salaries, x='Salaire', y='Nom', 
                        title='Top 10 des Salaires les Plus Élevés',
                        orientation='h', color='Poste')
        fig_top.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

def create_filtered_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Créer un DataFrame filtré avec options de recherche avancée"""
    
    # Vérifier si le DataFrame est vide
    if df.empty:
        st.sidebar.warning("Aucune donnée disponible pour le filtrage")
        return df
    
    # Sidebar pour les filtres
    st.sidebar.markdown("### 🔍 Filtres et Recherche")
    
    # Recherche textuelle
    search_term = st.sidebar.text_input("🔎 Recherche globale", 
                                       placeholder="Nom, email, département...")
    
    # Filtres par catégories avec gestion d'erreur
    try:
        departments = ['Tous'] + sorted(df['Département'].dropna().unique().tolist())
        selected_dept = st.sidebar.selectbox("🏢 Département", departments)
        
        countries = ['Tous'] + sorted(df['Pays'].dropna().unique().tolist())
        selected_country = st.sidebar.selectbox("🌍 Pays", countries)
        
        # Filtre par salaire avec validation
        salary_values = df['Salaire'].dropna()
        if len(salary_values) > 0:
            min_salary, max_salary = st.sidebar.slider(
                "💶 Plage de salaire", 
                min_value=int(salary_values.min()),
                max_value=int(salary_values.max()),
                value=(int(salary_values.min()), int(salary_values.max())),
                format="%d FCFA"
            )
        else:
            min_salary, max_salary = 0, 100000
            
    except Exception as e:
        st.sidebar.error(f"❌ Erreur lors de la création des filtres : {str(e)} ❌")
        return df
    
    # Application des filtres
    try:
        filtered_df = df.copy()
        
        if search_term:
            mask = (
                filtered_df['Nom'].astype(str).str.contains(search_term, case=False, na=False) |
                filtered_df['Email'].astype(str).str.contains(search_term, case=False, na=False) |
                filtered_df['Département'].astype(str).str.contains(search_term, case=False, na=False) |
                filtered_df['Poste'].astype(str).str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if selected_dept != 'Tous':
            filtered_df = filtered_df[filtered_df['Département'] == selected_dept]
        
        if selected_country != 'Tous':
            filtered_df = filtered_df[filtered_df['Pays'] == selected_country]
        
        filtered_df = filtered_df[
            (filtered_df['Salaire'] >= min_salary) & 
            (filtered_df['Salaire'] <= max_salary)
        ]
        
        return filtered_df
        
    except Exception as e:
        st.sidebar.error(f"❌ Erreur lors de l'application des filtres : {str(e)} ❌")
        return df

def main():
    # En-tête principal
    st.markdown('<h1 class="main-header">📊 Excel Data Manager Pro</h1>', unsafe_allow_html=True)
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "👥 Gestion des Employés", "➕ Ajouter Employé", "📈 Analytics Avancés", "🚀 Export CSV"])
    
    # Chargement des données avec gestion d'erreur
    try:
        df = DatabaseManager.load_data()
        if df.empty:
            st.error("⚠️ Impossible de charger les données ou base de données vide")
            st.info("Vérifiez votre connexion à la base de données")
            return
    except Exception as e:
        st.error(f"❌ Erreur fatale lors du chargement des données : {str(e)}")
        st.info("L'application ne peut pas continuer sans données")
        return
    
    with tab1:
        st.markdown("## 📊 Vue d'ensemble")
        
        if len(df) == 0:
            st.warning("Aucune donnée disponible")
        else:
            create_advanced_dashboard(df)
            
            # Section des données récentes
            st.markdown("---")
            st.markdown("### 🆕 Derniers Employés Ajoutés")
            recent_employees = df.nlargest(5, 'id')[['Nom', 'Email', 'Département', 'Poste', 'Pays']]
            st.dataframe(recent_employees, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("## 👥 Gestion des Employés")
        
        if len(df) == 0:
            st.warning("Aucune donnée disponible")
        else:
            filtered_df = create_filtered_dataframe(df)
            
            st.markdown(f"### Résultats: {len(filtered_df)} employé(s) trouvé(s)")
            
            # Options d'affichage
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                items_per_page = st.selectbox("Employés par page", [10, 25, 50, 100], index=1)
            with col2:
                sort_by = st.selectbox("Trier par", ['Nom', 'Salaire', 'Département', 'Pays'])
            with col3:
                ascending = st.checkbox("Croissant", value=True)
            
            # Pagination
            total_items = len(filtered_df)
            total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
            else:
                page = 0
            
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            
            # Tri et affichage
            sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            page_df = sorted_df.iloc[start_idx:end_idx]
            
            # Tableau interactif avec options d'action
            if len(page_df) > 0:
                st.dataframe(
                    page_df,
                    use_container_width=True,
                    column_config={
                        "Salaire": st.column_config.NumberColumn(
                            "Salaire",
                            help="Salaire mensuel en FCFA",
                            format="%d FCFA"
                        ),
                        "Email": st.column_config.TextColumn(
                            "Email",
                            help="Adresse email de l'employé"
                        )
                    },
                    hide_index=True
                )
                
                # Actions sur les employés
                st.markdown("### ⚙️ Actions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ✏️ Modifier un Employé")
                    with st.form("update_employee_form"):
                        emp_ids = page_df['id'].tolist()
                        selected_emp_id = st.selectbox("Sélectionner un employé", emp_ids, 
                                                      format_func=lambda x: f"ID {x} - {page_df[page_df['id']==x]['Nom'].iloc[0]}")
                        
                        if selected_emp_id:
                            emp_data = page_df[page_df['id'] == selected_emp_id].iloc[0]
                            
                            nom = st.text_input("Nom", value=emp_data['Nom'])
                            email = st.text_input("Email", value=emp_data['Email'])
                            tel = st.text_input("Téléphone", value=emp_data['Téléphone'])
                            departement = st.text_input("Département", value=emp_data['Département'])
                            poste = st.text_input("Poste", value=emp_data['Poste'])
                            salaire = st.number_input("Salaire", min_value=0, value=int(emp_data['Salaire']))
                            pays = st.text_input("Pays", value=emp_data['Pays'])
                            
                            if st.form_submit_button("💾 Mettre à jour"):
                                result = EmployeeManager.update_employee(
                                    selected_emp_id, nom, email, tel, departement, poste, salaire, pays
                                )
                                display_message(result)
                                if result["success"]:
                                    st.rerun()
                
                with col2:
                    st.markdown("#### 🗑️ Supprimer un Employé")
                    with st.form("delete_employee_form"):
                        emp_ids = page_df['id'].tolist()
                        delete_emp_id = st.selectbox("Sélectionner un employé à supprimer", emp_ids,
                                                    format_func=lambda x: f"ID {x} - {page_df[page_df['id']==x]['Nom'].iloc[0]}")
                        
                        st.warning("⚠️ Cette action est irréversible!")
                        confirm = st.checkbox("Je confirme vouloir supprimer cet employé")
                        
                        if st.form_submit_button("🗑️ Supprimer") and confirm:
                            result = EmployeeManager.delete_employee(delete_emp_id)
                            display_message(result)
                            if result["success"]:
                                st.rerun()
            else:
                st.info("Aucun employé ne correspond aux critères de filtrage")
    
    with tab3:
        st.markdown("## ➕ Ajouter un Nouvel Employé")
        
        with st.form("add_employee_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("👤 Nom complet *", placeholder="Paul Engone")
                email = st.text_input("📧 Email *", placeholder="paul.engone@email.com")
                tel = st.text_input("📱 Téléphone *", placeholder="+241 60 00 00 00")
                departement = st.text_input("🏢 Département *", placeholder="IT, RH, Finance, Marketing...")
            
            with col2:
                poste = st.text_input("💼 Poste *", placeholder="Développeur, Manager...")
                salaire = st.number_input("💰 Salaire mensuel (FCFA) *", min_value=0, value=1125000, step=1000)
                pays = st.text_input("🌍 Pays *", placeholder="Gabon")
                
                st.markdown("*Champs obligatoires")
            
            submitted = st.form_submit_button("➕ Ajouter l'Employé", use_container_width=True)
            
            if submitted:
                if all([nom, email, tel, departement, poste, pays]) and salaire > 0:
                    result = EmployeeManager.add_employee(nom, email, tel, departement, poste, salaire, pays)
                    display_message(result)
                    if result["success"]:
                        st.balloons()
                        st.rerun()
                else:
                    st.error(" ❌ Veuillez remplir tous les champs obligatoires ❌")
    
    with tab4:
        st.markdown("## 📈 Analytics Avancés")
        
        if len(df) == 0:
            st.warning("Aucune donnée disponible pour l'analyse")
        else:
            # Analyse comparative
            col1, col2 = st.columns(2)
            
            with col1:
                # Analyse des salaires par département et pays
                dept_country = df.groupby(['Département', 'Pays'])['Salaire'].agg(['mean', 'count']).reset_index()
                dept_country = dept_country[dept_country['count'] >= 2]
                
                fig_heatmap = px.density_heatmap(df, x='Département', y='Pays', z='Salaire',
                                               title='Heatmap: Somme des salaires par Département et Pays')
                fig_heatmap.update_layout(height=500)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                # Distribution des salaires
                fig_hist = px.histogram(df, x='Salaire', nbins=30, 
                                       title='Distribution des Salaires',
                                       labels={'count': 'Nombre d\'Employés'})
                fig_hist.add_vline(x=df['Salaire'].mean(), line_dash="dash", 
                                  annotation_text=f"Moyenne: {df['Salaire'].mean():.0f} FCFA")
                fig_hist.update_layout(height=500)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Tableau de bord détaillé
            st.markdown("### 📊 Statistiques Détaillées")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🏢 Par Département")
                dept_stats = df.groupby('Département').agg({
                    'Salaire': ['mean', 'min', 'max', 'count']
                }).round(0)
                dept_stats.columns = ['Moy.', 'Min.', 'Max.', 'Nb.']
                st.dataframe(dept_stats, use_container_width=True)
            
            with col2:
                st.markdown("#### 🌍 Par Pays")
                country_stats = df.groupby('Pays').agg({
                    'Salaire': ['mean', 'count']
                }).round(0)
                country_stats.columns = ['Salaire Moy.', 'Employés']
                country_stats = country_stats.sort_values('Employés', ascending=False).head(10)
                st.dataframe(country_stats, use_container_width=True)
            
            with col3:
                st.markdown("#### 💼 Par Poste")
                poste_stats = df.groupby('Poste').agg({
                    'Salaire': ['mean', 'count']
                }).round(0)
                poste_stats.columns = ['Salaire Moy.', 'Employés']
                poste_stats = poste_stats.sort_values('Salaire Moy.', ascending=False).head(10)
                st.dataframe(poste_stats, use_container_width=True)
    with tab5:
        st.markdown("## 🚀 Exporter les Données")
        
        if len(df) == 0:
            st.warning("Aucune donnée disponible pour l'export")
        else:
            st.markdown("### 📥 Exporter en CSV")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv,
                file_name='employes_export.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            st.markdown("### 📊 Visualiser les Données")
            st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()