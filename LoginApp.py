from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
import sqlite3
import sys
from TelaOrdem import TelaOrdem  # Importação da TelaOrdem


class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tela de Login")
        self.setGeometry(400, 200, 400, 350)
        self.setFixedSize(400, 350)

        # Conexão com o banco de dados SQLite
        self.conn = sqlite3.connect("//172.16.17.18/depto/Suporte/Geral/Usuarios/Adson/usuario.db")
        self.criar_tabela_usuarios()

        # Layout principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # Título
        self.title_label = QLabel("Bem-Vindo", self)
        self.title_label.setStyleSheet("font-size: 30px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Campo de usuário
        self.username_label = QLabel("Usuário:", self,styleSheet="font-weight: bold; font-size: 20px;")
        self.username_entry = QLineEdit(self, styleSheet="font-size: 20px;")
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)

        # Campo de senha
        self.password_label = QLabel("Senha:", self, styleSheet="font-weight: bold; font-size: 20px;")
        self.password_entry = QLineEdit(self, styleSheet="font-size: 20px;")
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)

        # Botão de login
        self.login_button = QPushButton("Entrar", self)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 22px;")
        self.login_button.clicked.connect(self.validate_login)
        layout.addWidget(self.login_button)

    def criar_tabela_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                permissao TEXT NOT NULL CHECK(permissao IN ('total', 'limitado'))
            )
        ''')
        self.conn.commit()

    def validate_login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT permissao FROM usuario WHERE nome=? AND senha=?", (username, password))
            user = cursor.fetchone()
            if user:
                permissao = user[0]
                QMessageBox.information(self, "Sucesso", f"Bem-vindo, {username}!")
                if username.lower() == "admin":
                    self.open_admin_panel()
                else:
                    self.open_tela_ordem(username, permissao)
            else:
                QMessageBox.critical(self, "Erro", "Usuário ou senha incorretos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao validar login: {e}")

    def open_tela_ordem(self, username, permissao):
        """Abre a tela TelaOrdem com base no usuário e permissão."""
        try:
            # Cria uma nova instância de TelaOrdem
            self.tela_ordem = TelaOrdem(username, permissao)
            
            # Exibe a nova janela
            self.tela_ordem.show()

            # Exibe mensagem de confirmação
            QMessageBox.information(self, "Ação", f"Entrando na TelaOrdem com permissão: {permissao}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir TelaOrdem: {e}")

        # fecha a janale de login
        self.close()
        

    def open_admin_panel(self):
        """Abre a janela de cadastro de novos usuários."""
        admin_panel = QMainWindow(self)  # Define como janela filha para modalidade
        admin_panel.setWindowTitle("Admin - Cadastro de Usuário")
        admin_panel.setGeometry(400, 480, 400, 480)

        # Widget central e layout
        central_widget = QWidget()
        admin_layout = QVBoxLayout(central_widget)
        admin_panel.setCentralWidget(central_widget)

        # Título
        title_label = QLabel("Cadastrar Novo Usuário")
        title_label.setStyleSheet("font-size: 25px; font-weight: bold;")
        admin_layout.addWidget(title_label)

        # Campos de entrada para cadastro
        username_label = QLabel("Nome do Usuário:", styleSheet="font-weight: bold; font-size: 20px;")
        username_entry = QLineEdit(self, styleSheet="font-size: 18px;")
        admin_layout.addWidget(username_label)
        admin_layout.addWidget(username_entry)

        password_label = QLabel("Senha:", styleSheet="font-weight: bold; font-size: 20px;")
        password_entry = QLineEdit(self, styleSheet="font-size: 18px;")
        password_entry.setEchoMode(QLineEdit.Password)
        admin_layout.addWidget(password_label)
        admin_layout.addWidget(password_entry)

        permissao_label = QLabel("Permissão:", styleSheet="font-weight: bold; font-size: 20px;")
        permissao_combobox = QComboBox(self, styleSheet="font-size: 16px;")
        permissao_combobox.addItems(["total", "limitado"])
        admin_layout.addWidget(permissao_label)
        admin_layout.addWidget(permissao_combobox)

        # Botão de cadastro
        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 22px;")
        cadastrar_button.clicked.connect(lambda: self.cadastrar_usuario(username_entry.text(), password_entry.text(), permissao_combobox.currentText()))
        admin_layout.addWidget(cadastrar_button)

        # Botão de sair
        sair_button = QPushButton("Sair")
        sair_button.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold; font-size: 22px;")
        sair_button.clicked.connect(admin_panel.close)
        admin_layout.addWidget(sair_button)

        # Exibe a janela como modal
        admin_panel.setWindowModality(Qt.ApplicationModal)
        admin_panel.show()

    def cadastrar_usuario(self, username, password, permissao):
        if not username or not password or not permissao:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO usuario (nome, senha, permissao) VALUES (?, ?, ?)", (username, password, permissao))
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", f"Usuário '{username}' cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erro", "Usuário já existe.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar usuário: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_app = LoginApp()
    login_app.show()
    sys.exit(app.exec_())