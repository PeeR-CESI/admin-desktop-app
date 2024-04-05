import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sv_ttk
import requests

class UserManagementApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestion des utilisateurs PeeR")
        sv_ttk.set_theme("light")

        self.token = ""
        self.init_login_ui()  # Commencez par l'interface de connexion
        self.center_window(500, 350)  # Taille initiale de la fenêtre de connexion

    def init_login_ui(self):
        self.clear_widgets()  # Nettoyez l'interface avant d'afficher le nouvel UI

        # Toggle et texte du dark mode en haut à gauche
        self.theme_frame = ttk.Frame(self.master)
        self.theme_frame.pack(side="top", fill="x", expand=False)
        self.theme_toggle = ttk.Checkbutton(self.theme_frame, text="Dark mode", command=self.toggle_theme, style="Switch.TCheckbutton")
        self.theme_toggle.pack(side="left", padx=10, pady=10)

        self.logo_light_path = "admin-desktop-app/logo-light-mode.png"
        self.logo_dark_path = "admin-desktop-app/logo-dark-mode.png"
        self.load_logo_image(self.logo_light_path)  # Chargement initial du logo en mode clair

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
        logo_img = Image.open(logo_path).resize((177, 70))
        self.logo_image = ImageTk.PhotoImage(logo_img)
        if not hasattr(self, 'logo_label'):
            self.logo_label = ttk.Label(self.master, image=self.logo_image)
            self.logo_label.pack(pady=20)
        else:
            self.logo_label.config(image=self.logo_image)

    def toggle_theme(self):
        new_theme = "dark" if sv_ttk.get_theme() == "light" else "light"
        sv_ttk.set_theme(new_theme)
        logo_path = self.logo_dark_path if new_theme == "dark" else self.logo_light_path
        self.load_logo_image(logo_path)
    
    def login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            r = requests.post("http://localhost:5000/auth/login", json={"username": username, "password": password})
            if r.status_code == 200:
                self.token = r.json()['token']
                self.init_user_management_ui()  # Passer à la gestion des utilisateurs après la connexion réussie
            else:
                messagebox.showerror("Erreur", "Identifiants invalides ou vous n'êtes pas administrateur.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à l'API: {e}")

    def init_user_management_ui(self):
        self.clear_widgets()
        self.center_window(1000, 700)

        # Scrollable Treeview Configuration
        tree_scroll_frame = ttk.Frame(self.master)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.user_list = ttk.Treeview(tree_scroll_frame, columns=("Nom", "Prénom", "Email", "Adresse", "Rôle"), show="headings")
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.user_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_list.configure(yscrollcommand=scrollbar.set)

        for col in self.user_list["columns"]:
            self.user_list.heading(col, text=col)
            self.user_list.column(col, width=120)

        # Boutons d'action utilisateur
        action_frame = ttk.Frame(self.master)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="Ajouter", command=self.add_user).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Modifier", command=self.modify_user).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Supprimer", command=self.delete_user).pack(side=tk.LEFT, padx=10)

        self.populate_user_list()  # Peupler avec des données simulées pour l'exemple

    def populate_user_list(self):
        # Exemple de méthode pour peupler le Treeview avec des données
        # Remplacer cette logique par la récupération de vos données utilisateurs
        users = [("Utilisateur" + str(i), "Prénom" + str(i), f"email{i}@exemple.com", "Adresse" + str(i), "Rôle" + str(i % 5)) for i in range(1, 61)]
        for user in users:
            self.user_list.insert('', 'end', values=user)

    def add_user(self):
        # Ici, vous ouvririez un dialogue/formulaire pour ajouter un utilisateur
        messagebox.showinfo("Ajouter un Utilisateur", "Fonctionnalité à implémenter.")

    def modify_user(self):
        # Dialogue/formulaire pour modifier un utilisateur
        messagebox.showinfo("Modifier un Utilisateur", "Fonctionnalité à implémenter.")

    def delete_user(self):
        selected_items = self.user_list.selection()  # Récupère la liste des items sélectionnés
        if selected_items:
            # Construire le message de confirmation basé sur le nombre d'utilisateurs sélectionnés
            if len(selected_items) == 1:
                user = self.user_list.item(selected_items[0], "values")
                confirmation_message = f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user[0]} ?"
            else:
                user_list_str = "\n- ".join([self.user_list.item(item, "values")[0] for item in selected_items])
                confirmation_message = f"Êtes-vous sûr de vouloir supprimer ces utilisateurs ? :\n- {user_list_str}"

            # Afficher la boîte de dialogue de confirmation
            response = messagebox.askyesno("Supprimer Utilisateurs", confirmation_message)
            if response:
                try:
                    # Supprime chaque utilisateur sélectionné de la liste
                    for selected_item in selected_items:
                        self.user_list.delete(selected_item)
                    # Message de confirmation adapté au nombre d'utilisateurs supprimés
                    if len(selected_items) == 1:
                        messagebox.showinfo("Supprimer", f"L'utilisateur {user[0]} a été supprimé.")
                    else:
                        messagebox.showinfo("Supprimer", "Les utilisateurs sélectionnés ont été supprimés.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression des utilisateurs: {e}")
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins un utilisateur à supprimer.")

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()