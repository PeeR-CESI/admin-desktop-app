import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sv_ttk
import requests
import hashlib

class UserManagementApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestion des utilisateurs PeeR")
        sv_ttk.set_theme("light")
        
        self.dark_theme = tk.BooleanVar(value=False)
        
        self.logo_light_path = "admin-desktop-app/logo-light-mode.png"
        self.logo_dark_path = "admin-desktop-app/logo-dark-mode.png"

        self.access_token = None
        self.refresh_token = None
        
        self.init_login_ui()  # Commencez par l'interface de connexion
        self.center_window(500, 350)  # Taille initiale de la fenêtre de connexion

    def init_login_ui(self):
        self.clear_widgets()

        # Toggle et texte du dark mode en haut
        self.theme_frame = ttk.Frame(self.master)
        self.theme_frame.pack(side="top", fill="x", expand=False)
        self.theme_toggle = ttk.Checkbutton(self.theme_frame, text="Dark mode", command=self.toggle_theme, style="Switch.TCheckbutton", variable=self.dark_theme)
        self.theme_toggle.pack(side="left", padx=10, pady=10)

        # Cadre dédié pour le logo, placé en dessous de la frame du toggle du dark mode
        self.logo_frame = ttk.Frame(self.master)
        self.logo_frame.pack(side="top", fill="x", expand=False)
        self.load_logo_image(self.logo_dark_path if self.dark_theme.get() else self.logo_light_path)

        # Configuration du cadre de connexion
        self.login_frame = ttk.Frame(self.master)
        self.login_frame.pack(expand=True)
        ttk.Label(self.login_frame, text="Nom d'utilisateur : ").grid(row=0, column=0, pady=10)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        ttk.Label(self.login_frame, text="Mot de passe : ").grid(row=1, column=0, pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        self.login_button = ttk.Button(self.login_frame, text="Connexion", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Ajustements pour le centrage
        for child in self.login_frame.winfo_children():
            child.grid_configure(sticky="ew")
        self.login_frame.grid_columnconfigure(1, weight=1)

        self.username_entry.focus_set()
        self.username_entry.bind("<Return>", self.login)
        self.password_entry.bind("<Return>", self.login)
        
    def init_user_management_ui(self):
        self.clear_widgets()
        self.center_window(1000, 700)

        # Cadre pour le dark mode et le bouton de déconnexion
        top_frame = ttk.Frame(self.master)
        top_frame.pack(side="top", fill="x", pady=(0, 0), padx=0)

        # Bouton switch pour le dark mode à gauche
        self.theme_toggle = ttk.Checkbutton(top_frame, text="Dark mode", command=self.toggle_theme, style="Switch.TCheckbutton", variable=self.dark_theme)
        self.theme_toggle.pack(side="left", padx=10)

        # Bouton de Déconnexion à droite
        logout_button = ttk.Button(top_frame, text="Déconnexion", command=self.logout)
        logout_button.pack(side="right", pady=(10, 0), padx=10)

        # Nouvelle frame spécifiquement pour le logo, placée en dessous des boutons et au-dessus de la liste des utilisateurs
        logo_frame = ttk.Frame(self.master)
        logo_frame.pack(side="top", fill="x", pady=(0, 0))  # Espacement pour séparer visuellement du reste
        self.logo_frame = logo_frame  # Mise à jour de la référence de self.logo_frame
        # Chargement et affichage du logo au centre
        self.load_logo_image(self.logo_dark_path if self.dark_theme.get() else self.logo_light_path)

        # Configuration du cadre principal pour la liste des utilisateurs et les scrollbars
        tree_scroll_frame = ttk.Frame(self.master)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.user_list = ttk.Treeview(tree_scroll_frame, columns=("ID", "Username", "Nom", "Prénom", "Email", "Adresse", "Rôle"), show="headings")
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.user_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_list.configure(yscrollcommand=scrollbar.set)

        for col in self.user_list["columns"]:
            self.user_list.heading(col, text=col)
            self.user_list.column(col, width=120)
            self.user_list.column("ID", width=10)
            self.user_list.column("ID", width=50)
            self.user_list.column("Nom", width=50)
            self.user_list.column("Prénom", width=50)
            self.user_list.column("Rôle", width=50)

        # Boutons d'action utilisateur et bouton Rafraîchir en bas
        action_frame = ttk.Frame(self.master)
        action_frame.pack(fill=tk.X, pady=10, side="bottom")

        refresh_button = ttk.Button(action_frame, text="Rafraîchir", command=self.refresh_user_list)
        refresh_button.pack(side="right", padx=10)

        ttk.Button(action_frame, text="Ajouter", command=self.init_add_user_ui, width=15).pack(side="left", padx=10)
        ttk.Button(action_frame, text="Modifier", command=self.init_modify_user_ui, width=15).pack(side="left", padx=10)
        ttk.Button(action_frame, text="Supprimer", command=self.delete_user, width=15).pack(side="left", padx=10)

        self.populate_user_list()


    def init_add_user_ui(self):
        self.clear_widgets()
        self.center_window(700, 400)

        fields = ["Nom", "Prénom", "Email", "Adresse", "Rôle", "Username", "Password"]
        self.user_fields = {}
        row = 0
        roles = ["admin", "demandeur", "presta", "dev"]  # Les rôles disponibles

        for field in fields:
            ttk.Label(self.master, text=f"{field}:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
            if field == "Rôle":
                combobox = ttk.Combobox(self.master, values=roles, state='readonly')  # Ajout de l'option state='readonly'
                combobox.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = combobox
            elif field == "Password":
                entry = ttk.Entry(self.master, show="*")
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = entry
            else:
                entry = ttk.Entry(self.master)
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = entry
            row += 1

        # Cadre pour les boutons d'action
        action_frame = ttk.Frame(self.master)
        action_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=20)

        # Boutons d'action dans le cadre action_frame avec tailles variables
        validate_button = ttk.Button(action_frame, text="Valider", command=self.validate_add_user, width=15)
        validate_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(action_frame, text="Annuler", command=self.init_user_management_ui, width=15)
        cancel_button.pack(side="left", padx=5)

        self.master.grid_columnconfigure(1, weight=1)
        
    def init_modify_user_ui(self):
        selected_item = self.user_list.selection()
        if not selected_item:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un utilisateur à modifier.")
            return

        user_id = self.user_list.item(selected_item, "values")[0]
        username = self.user_list.item(selected_item, "values")[1]

        try:
            response = requests.get(f"http://peer.cesi/api/user/find/{user_id}", headers={"Authorization": f"Bearer {self.access_token}"})
            if response.status_code == 200:
                user_details = response.json()
            else:
                messagebox.showerror("Erreur", "Impossible de récupérer les informations de l'utilisateur.")
                return
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à l'API : {e}")
            return

        self.clear_widgets()
        self.center_window(700, 450)

        ttk.Label(self.master, text="ID:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(self.master, text=user_id).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        fields = ["Nom", "Prenom", "Email", "Adresse", "Role", "Username", "Password"]
        roles = ["admin", "demandeur", "presta", "dev"]  # Les rôles disponibles
        self.user_fields = {}
        row = 1  # Commencer à la deuxième ligne pour les autres champs

        for field in fields:
            ttk.Label(self.master, text=f"{field}:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
            if field == "Role":
                combobox = ttk.Combobox(self.master, values=roles, state='readonly')
                combobox.set(user_details.get("role", ""))  # Préremplir avec le rôle actuel de l'utilisateur
                combobox.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = combobox
            elif field == "Password":
                entry = ttk.Entry(self.master, show="*")
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = entry
            else:
                entry = ttk.Entry(self.master)
                entry_value = user_details.get(field.lower(), "")
                entry.insert(0, entry_value)
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                self.user_fields[field] = entry
            row += 1

        action_frame = ttk.Frame(self.master)
        action_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=20)

        validate_button = ttk.Button(action_frame, text="Mettre à jour", command=lambda: self.submit_modifications(user_id), width=15)
        validate_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(action_frame, text="Annuler", command=self.init_user_management_ui, width=15)
        cancel_button.pack(side="left", padx=5)

        self.master.grid_columnconfigure(1, weight=1)

    def center_window(self, width=500, height=350):
        # Obtenir la largeur et la hauteur de l'écran
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculer la position x et y pour centrer la fenêtre
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        # Mettre à jour la géométrie de la fenêtre pour centrer
        self.master.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def load_logo_image(self, logo_path):
        # Assurez-vous que logo_frame existe et est valide avant de continuer
        if not hasattr(self, 'logo_frame') or not self.logo_frame.winfo_exists():
            self.logo_frame = ttk.Frame(self.master)
            self.logo_frame.pack(side="top", fill="x", expand=False)
            
        # Détruire le widget de logo existant s'il existe et est valide
        if hasattr(self, 'logo_label') and self.logo_label.winfo_exists():
            self.logo_label.destroy()

        # Charger l'image du logo
        logo_img = Image.open(logo_path).resize((177, 70))
        self.logo_image = ImageTk.PhotoImage(logo_img)

        # Essayer de créer un nouveau widget de logo avec l'image chargée
        try:
            self.logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
            self.logo_label.pack(pady=10)  # Centrer le logo dans le cadre.
        except tk.TclError as e:
            print(f"Erreur lors de la mise à jour du logo : {e}")

    def toggle_theme(self):
        sv_ttk.set_theme("light" if not self.dark_theme.get() else "dark", )
        self.load_logo_image(self.logo_dark_path if self.dark_theme.get() else self.logo_light_path)
    
    def login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            response = requests.post("http://peer.cesi/api/auth/login", json={"username": username, "password": password})
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                self.refresh_token = response_data.get('refresh_token')
                self.user_role = response_data.get('role')  # Stockez le rôle de l'utilisateur
                
                if self.user_role == "admin":
                    self.init_user_management_ui()  # Passer à la gestion des utilisateurs après la connexion réussie
                else:
                    messagebox.showerror("Accès refusé", "Vous n'avez pas les droits d'administrateur nécessaires pour accéder à cette section.")
            elif response.status_code == 404:
                messagebox.showerror("Erreur de connexion", "Nom d'utilisateur invalide.")
            elif response.status_code == 401:
                messagebox.showerror("Erreur de connexion", "Mot de passe incorrect.")
            else:
                messagebox.showerror("Erreur", "Erreur inconnue, veuillez réessayer.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à l'API: {e}")

    def populate_user_list(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.get("http://peer.cesi/api/user/all", headers=headers)
            if response.status_code == 200:
                users_data = response.json()
                for user in users_data:
                    self.user_list.insert('', tk.END, values=(
                        user["id"],
                        user["username"],  # Assurez-vous que ceci correspond au champ renvoyé par votre API
                        user["nom"], 
                        user["prenom"], 
                        user["email"], 
                        user["adresse"], 
                        user["role"]
                    ))
            else:
                messagebox.showerror("Erreur", f"Impossible de récupérer la liste des utilisateurs. Code d'erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur lors de la connexion à l'API : {e}")

    def refresh_user_list(self):
        # Effacer les données actuelles du Treeview
        for i in self.user_list.get_children():
            self.user_list.delete(i)
        # Recharger les données
        self.populate_user_list()

    def validate_add_user(self):
        # Récupération des valeurs saisies dans les champs du formulaire
        user_data = {
            "adresse": self.user_fields["Adresse"].get(),
            "email": self.user_fields["Email"].get(),
            "nom": self.user_fields["Nom"].get(),
            "password": self.user_fields["Password"].get(),
            "prenom": self.user_fields["Prénom"].get(),
            "role": self.user_fields["Rôle"].get(),
            "username": self.user_fields["Username"].get()
        }

        # Vérification que tous les champs sont remplis
        if not all(user_data.values()):
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return

        # Préparer les headers pour inclure le token d'authentification
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            # Effectuer la requête POST à l'API pour ajouter l'utilisateur
            response = requests.post("http://peer.cesi/api/user/create", json=user_data, headers=headers)

            if response.status_code == 200 or response.status_code == 201:
                # Si l'utilisateur est ajouté avec succès, rafraîchir la liste des utilisateurs
                messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
                self.init_user_management_ui()  # Retour à la page de gestion des utilisateurs
            else:
                # Gérer les erreurs potentielles (comme les données non valides ou les problèmes de serveur)
                messagebox.showerror("Erreur", f"Échec de l'ajout de l'utilisateur. Code d'erreur : {response.status_code}, Message : {response.json().get('message')}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à l'API : {e}")

    def submit_modifications(self, user_id):
        # Construction du dictionnaire des données à partir des champs de saisie
        updated_data = {
            "adresse": self.user_fields["Adresse"].get(),
            "email": self.user_fields["Email"].get(),
            "nom": self.user_fields["Nom"].get(),
            "prenom": self.user_fields["Prenom"].get(),
            "role": self.user_fields["Role"].get(), 
            "username": self.user_fields["Username"].get(),
        }

        # Vérifier si le champ mot de passe est rempli
        password = self.user_fields["Password"].get()
        if password.strip():  # Si le champ n'est pas vide
            # Hashage du mot de passe
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            updated_data["password"] = hashed_password

        # Préparer les headers pour inclure le token d'authentification
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            # Envoi de la requête PUT
            response = requests.put(f"http://peer.cesi/api/user/update/{user_id}", json=updated_data, headers=headers)

            if response.status_code in [200, 204]:  # Succès de la mise à jour
                messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
                self.init_user_management_ui()  # Retour à la page de gestion des utilisateurs
            else:
                messagebox.showerror("Erreur", f"Échec de la mise à jour. Code d'erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à l'API : {e}")

    def delete_user(self):
        selected_items = self.user_list.selection()  # Récupère la liste des items sélectionnés
        if not selected_items:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins un utilisateur à supprimer.")
            return

        # Construire le message de confirmation basé sur le nombre d'utilisateurs sélectionnés
        if len(selected_items) == 1:
            user = self.user_list.item(selected_items[0], "values")
            confirmation_message = f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user[1]} ?"  # Assumer que user[1] est le nom
        else:
            user_names = "\n- ".join([self.user_list.item(item, "values")[1] for item in selected_items])  # Assumer que user[1] est le nom
            confirmation_message = f"Êtes-vous sûr de vouloir supprimer ces utilisateurs ? :\n- {user_names}"

        # Afficher la boîte de dialogue de confirmation
        response = messagebox.askyesno("Supprimer Utilisateurs", confirmation_message)
        if response:
            for selected_item in selected_items:
                user_id = self.user_list.item(selected_item, "values")[0]  # Assumer que user[0] est l'ID
                try:
                    # Suppression de l'utilisateur via l'API
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    response = requests.delete(f"http://peer.cesi/api/user/delete/{user_id}", headers=headers)
                    if response.status_code == 200:
                        self.user_list.delete(selected_item)  # Supprimer de l'affichage si la suppression est réussie
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à l'API : {e}")

            # Affichage du message de succès adapté au nombre d'utilisateurs supprimés
            if len(selected_items) == 1:
                messagebox.showinfo("Supprimer", "L'utilisateur a été supprimé avec succès.")
            else:
                messagebox.showinfo("Supprimer", "Les utilisateurs sélectionnés ont été supprimés avec succès.")

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    child.destroy()
            widget.destroy()
            
    def logout(self):
        self.access_token = None
        self.refresh_token = None
        self.clear_widgets()
        self.center_window(500, 350) 
        self.init_login_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()