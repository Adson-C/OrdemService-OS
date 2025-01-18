from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QMenuBar, QToolBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sqlite3
import sys
import pandas as pd
from datetime import datetime
from random import seed, randint
seed(42)  # Para gerar cores consistentes


class FiltroAvancadoDialog(QDialog):
    def __init__(self, colunas, permissao, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtro Avançado")
         # Definir tamanho mínimo e máximo da janela
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1920, 1080)
        # Ajusta o tamanho da janela no cento da tela
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((screen.width() - 300) // 2, (screen.height() - 300) // 2)
        self.setFixedSize(300, 300)
        self.permissao = permissao

        # Limita as colunas disponíveis para usuários com permissão limitada
        if self.permissao == "operacaopax":
            self.colunas = ["Cliente", "Ordem Service"]
        else:
            # tirar o ID da filtragem
            colunas = [coluna for coluna in colunas if coluna != "id"]
            self.colunas = colunas

        self.setup_ui()
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Aplicar estilo CSS para o texto dos widgets
        style = """
        QComboBox, QLabel, QLineEdit {
            font-size: 20px;
        }
        """
        self.setStyleSheet(style)

        self.coluna_combobox = QtWidgets.QComboBox()
        self.coluna_combobox.addItems(self.colunas)
        layout.addWidget(QtWidgets.QLabel("Selecionar Coluna:"))
        layout.addWidget(self.coluna_combobox)

        self.operador_combobox = QtWidgets.QComboBox()
        self.operador_combobox.addItems(["=", "LIKE"])
        layout.addWidget(QtWidgets.QLabel("Selecionar Operador:"))
        layout.addWidget(self.operador_combobox)

        self.valor_input = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Valor para Filtrar:"))
        layout.addWidget(self.valor_input)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_filter(self):
        coluna = self.coluna_combobox.currentText()
        operador = self.operador_combobox.currentText()
        valor = self.valor_input.text().strip()
        return coluna, operador, valor
    
class EditarModal(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Editar Registros")
        self.layout = QtWidgets.QVBoxLayout(self)

        self.inputs_por_linha = []

        # Lista das colunas editáveis
        self.colunas_editaveis = [
            "Modelo", "Part Number", "Serial Number", "Versao SO", "Versao Boot",
            "DebugOuRelease", "PUK", "Versao Radio", "Versao App", "Configurador",
            "Perfil Chaves", "Preparador", "Obs", "Status"
        ]

        # Carregar sugestões de autocomplete do banco de dados
        self.sugestoes = self.carregar_sugestoes()

    def carregar_sugestoes(self):
        """Carrega sugestões de autocomplete para cada coluna do banco de dados."""
        sugestoes = {col: set() for col in self.colunas_editaveis}
        try:
            self.parent.cursor.execute("SELECT * FROM appordem")
            registros = self.parent.cursor.fetchall()
            colunas = self.parent.colunas

            for registro in registros:
                for i, valor in enumerate(registro):
                    coluna = colunas[i]
                    if coluna in sugestoes and valor is not None:
                        sugestoes[coluna].add(str(valor).strip().upper())
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar sugestões: {e}")

        return {col: sorted(list(valores)) for col, valores in sugestoes.items()}

    # def set_data_multiplas_linhas(self, dados_linhas):
    #     """Configura os placeholders com os dados de múltiplas linhas."""
    #     for dados in dados_linhas:
    #         inputs = []
    #         linha_layout = QtWidgets.QHBoxLayout()

    #         for col, valor in zip(self.colunas_editaveis, dados):
    #             valor_tooltip = valor if valor and valor.strip().lower() not in {"null", "none"} else "Valor não definido"

    #             if col == "DebugOuRelease":
    #                 # Configuração do combobox para Debug/Release
    #                 combobox = QtWidgets.QComboBox()
    #                 combobox.addItems(["DEBUG", "RELEASE"])
    #                 combobox.setCurrentText(valor)
    #                 combobox.setToolTip(valor_tooltip)  # Tooltip com valor completo
    #                 combobox.setFixedWidth(60)  # Define largura fixa
    #                 linha_layout.addWidget(combobox)
    #                 inputs.append(combobox)
                
    #             elif col == "Status":
    #                 # Configuração do combobox para Status
    #                 combobox = QtWidgets.QComboBox()
    #                 combobox.addItems(["PENDENTE", "CONCLUIDO"])
    #                 combobox.setCurrentText(valor)
    #                 combobox.setToolTip(valor_tooltip)  # Tooltip com valor completo
    #                 combobox.setFixedWidth(80)  # Define largura fixa
    #                 linha_layout.addWidget(combobox)
    #                 inputs.append(combobox)
                
    #             else:
    #                 # Configuração do QLineEdit para campos editáveis
    #                 input_field = QtWidgets.QLineEdit(valor if valor else "")
                    
    #                 if not valor or valor.strip().lower() in {"null", "none"}:
    #                     input_field.clear()  # Limpa valores inválidos
    #                     input_field.setPlaceholderText(f"{col.lower()}")  # Placeholder com o nome da coluna
                    
    #                 # Configuração do autocomplete
    #                 if col in self.sugestoes:
    #                     completer = QtWidgets.QCompleter(self.sugestoes[col])
    #                     completer.setCaseSensitivity(Qt.CaseInsensitive)
                        
    #                     # Ajustar o tamanho do menu de autocomplete
    #                     popup = completer.popup()
    #                     popup.setStyleSheet("font-size: 12px;")  # Fonte maior no popup
    #                     popup.setMinimumWidth(400)  # Largura mínima do autocomplete

    #                     input_field.setCompleter(completer)

    #                 # Tooltip com valor completo
    #                 input_field.setToolTip(valor_tooltip)

    #                 # Define a largura fixa do campo de entrada
    #                 input_field.setFixedWidth(90)  # Ajuste para campos maiores
    #                 linha_layout.addWidget(input_field)
    #                 inputs.append(input_field)

    #         self.layout.addLayout(linha_layout)
    #         self.inputs_por_linha.append(inputs)

    #     # Botão Salvar
    #     self.save_button = QtWidgets.QPushButton("Salvar")
    #     self.save_button.clicked.connect(self.accept)
    #     self.save_button.setFixedSize(200, 30)
    #     self.save_button.setStyleSheet(
    #         "background-color: #228B22; color: white; font-weight: bold;"
    #     )
    #     self.save_button.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
    #     self.layout.addWidget(self.save_button)

    def set_data_multiplas_linhas(self, dados_linhas):
        """Configura os placeholders com os dados de múltiplas linhas."""
        for dados in dados_linhas:
            inputs = []
            linha_layout = QtWidgets.QHBoxLayout()

            for col, valor in zip(self.colunas_editaveis, dados):
                
                if col == "DebugOuRelease":
                    # Configuração do combobox para Debug/Release
                    combobox = QtWidgets.QComboBox()
                    combobox.addItems(["DEBUG", "RELEASE"])
                    combobox.setFixedWidth(60)  # Define largura fixa
                    linha_layout.addWidget(combobox)
                    inputs.append(combobox)
                
                elif col == "Status":
                    # Configuração do combobox para Status
                    combobox = QtWidgets.QComboBox()
                    combobox.addItems(["PENDENTE", "CONCLUIDO"])
                    combobox.setFixedWidth(80)  # Define largura fixa
                    linha_layout.addWidget(combobox)
                    inputs.append(combobox)
                
                else:
                    # Configuração do QLineEdit para campos editáveis
                    input_field = QtWidgets.QLineEdit(valor if valor else "")
                    
                    if not valor or valor.strip().lower() in {"null", "none"}:
                        input_field.clear()  # Limpa valores inválidos
                        input_field.setPlaceholderText(f"{col.lower()}")  # Placeholder com o nome da coluna
                    
                    # Configuração do autocomplete
                    if col in self.sugestoes:
                        completer = QtWidgets.QCompleter(self.sugestoes[col])
                        completer.setCaseSensitivity(Qt.CaseInsensitive)
                        
                        # Ajustar o tamanho do menu de autocomplete
                        popup = completer.popup()
                        popup.setStyleSheet("font-size: 12px;")  # Fonte maior no popup
                        popup.setMinimumWidth(400)  # Largura mínima do autocomplete

                        input_field.setCompleter(completer)

                    # Tooltip com valor completo ou mensagem padrão
                    # Define a largura fixa do campo de entrada
                    input_field.setFixedWidth(90)  # Ajuste para campos maiores
                    linha_layout.addWidget(input_field)
                    inputs.append(input_field)

            self.layout.addLayout(linha_layout)
            self.inputs_por_linha.append(inputs)

        # Botão Salvar
        self.save_button = QtWidgets.QPushButton("Salvar")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setFixedSize(200, 30)
        self.save_button.setStyleSheet(
            "background-color: #228B22; color: white; font-weight: bold;"
        )
        self.save_button.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
        self.layout.addWidget(self.save_button)

    def get_data_multiplas_linhas(self):
        """Retorna os dados editados de todas as linhas."""
        return [
            [
                input_field.currentText().strip() if isinstance(input_field, QtWidgets.QComboBox)
                else input_field.text().strip()
                for input_field in inputs
            ]
            for inputs in self.inputs_por_linha
        ]


class TelaOrdem(QtWidgets.QMainWindow):
    def __init__(self, username, permissao):
        super().__init__()
        self.setWindowTitle("Manipulação de Banco de Dados e Filtros")

        # Obter a geometria da tela
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.height()

        # Define o tamanho inicial da janela com base na resolução
        window_width, window_height = 1890, 820  # Dimensões iniciais padrão
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Configura a geometria inicial da janela
        self.setGeometry(x_position, y_position, window_width, window_height)

        # Permitir que a janela seja redimensionada manualmente
        self.setMinimumSize(640, 480)  # Define um tamanho mínimo razoável

        # Oculta somente o botão de fechar
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.CustomizeWindowHint
        )

    
        self.username = username
        self.permissao = permissao

        self.conn = sqlite3.connect("dados.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela()

        self.colunas = [
            "id","Cliente", "Modelo", "Part Number", "Serial Number", "Versao SO",
            "Versao Boot", "DebugOuRelease", "PUK", "Versao Radio",
            "Versao App", "Configurador", "Perfil Chaves", "Preparador",
            "Obs", "Ordem Service", "Status", "Data Envio"
        ]

        self.placeholders = [
            "Cliente", "Modelo", "Part Number", "Serial Number",
            "Versão SO", "Versão Boot", "De/Re", "PUK",
            "Versão Radio", "Versão App", "Configurador",
            "Perfil Chaves", "Preparador", "Obs", "Ordem Service", "Status"
        ]

        self.dados_filtrados = []  # Lista para armazenar dados filtrados
        self.input_rows = []
        self.setup_ui()
        self.carregar_dados()

    def criar_tabela(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appordem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Cliente TEXT,
            Modelo TEXT,
            PartNumber TEXT,
            SerialNumber TEXT,
            VersaoSO TEXT,
            VersaoBoot TEXT,
            ModoDebugRelease TEXT,
            PUK TEXT,
            VersaoRadio TEXT,
            VersaoApp TEXT,
            Configurador TEXT,
            PerfilChave TEXT,
            Preparador TEXT,
            Obs TEXT,
            OrdemService TEXT,
            Status TEXT,
            DataEnvio TEXT
        )
        """)
        self.conn.commit()
    
    def setup_ui(self):
        # Criação do widget central e layout principal
        central_widget = QtWidgets.QWidget()
        self.layout_principal = QtWidgets.QVBoxLayout(central_widget)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)

        # Label do usuário
        # user_label = QtWidgets.QLabel(f"Usuário logado: {self.username}")
        user_label = QtWidgets.QLabel(f"Usuário logado: {self.username} ({self.permissao.upper()})")
        user_label.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
        self.layout_principal.addWidget(user_label)

        # Layout para o botão "Exportar Dados" acima da tabela
        if self.permissao == "suporte":
            export_layout = QtWidgets.QHBoxLayout()
            export_button = QtWidgets.QPushButton("Exportar Dados")
            export_button.clicked.connect(self.exportar_dados)
            export_button.setStyleSheet(
                "background-color: #3498db; color: white; font-weight: bold;")
            export_layout.addWidget(export_button)
            export_layout.addStretch()
            # Adiciona o layout com o botão acima da tabela
            self.layout_principal.addLayout(export_layout)

        # Layout para os botões de filtro acima da tabela e alinhados à direita
        filter_layout = QtWidgets.QHBoxLayout()
        # Adiciona espaço flexível para empurrar os botões para a direita
        filter_layout.addStretch()
        
       # Botão "Ir para Último Registro"
        ultimo_registro_button = QtWidgets.QPushButton("Ir para Último Registro")
        ultimo_registro_button.setIcon(QtGui.QIcon("icons/down-arrow.png"))  # Substitua pelo caminho do seu ícone
        ultimo_registro_button.setIconSize(QtCore.QSize(28, 30))  # Define o tamanho do ícone
        ultimo_registro_button.clicked.connect(self.ir_para_ultimo_registro)
        ultimo_registro_button.setFont(QtGui.QFont("sans-serif", 10))
        filter_layout.addWidget(ultimo_registro_button)

        # Botão "Filtro Avançado"
        filter_advanced_button = QtWidgets.QPushButton("Filtro")
        filter_advanced_button.setIcon(QtGui.QIcon("icons/filter.png"))  # Substitua pelo caminho do seu ícone
        filter_advanced_button.setIconSize(QtCore.QSize(28, 30))  # Define o tamanho do ícone
        filter_advanced_button.clicked.connect(self.abrir_filtro_avancado)
        filter_advanced_button.setFont(QtGui.QFont("sans-serif", 10))
        filter_layout.addWidget(filter_advanced_button)

        # Botão "Limpar Filtro"
        clear_advanced_filter_button = QtWidgets.QPushButton("Limpar Filtro")
        clear_advanced_filter_button.setIcon(QtGui.QIcon("icons/clear-filter.png"))  # Substitua pelo caminho do seu ícone
        clear_advanced_filter_button.setIconSize(QtCore.QSize(28, 30))  # Define o tamanho do íconefilter_advanced_button
        clear_advanced_filter_button.clicked.connect(self.limpar_filtro_avancado)
        clear_advanced_filter_button.setFont(QtGui.QFont("sans-serif", 10))
        filter_layout.addWidget(clear_advanced_filter_button)

        # Adiciona o layout com os botões de filtro acima da tabela
        self.layout_principal.addLayout(filter_layout)

        # Criação do QTableWidget
        self.table = QtWidgets.QTableWidget()
        print("Tabela inicializada:", self.table)
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        self.table.setAlternatingRowColors(True)
        # self.table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # Permitir edição
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers if self.permissao == "suporte" else QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableView.MultiSelection)
        # Adiciona o evento para colorir dinamicamente
        self.table.itemChanged.connect(self.colorir_status)
        self.layout_principal.addWidget(self.table)
        self.table.hideColumn(0)

        # Frame para os campos de entrada
        self.frame_inputs = QtWidgets.QFrame(self)
        self.frame_inputs.setLayout(QtWidgets.QVBoxLayout())
        self.layout_principal.addWidget(self.frame_inputs)

         # Adicionar uma linha inicial automaticamente
        if self.permissao == "operacaopax":
            self.configurar_campos_fixos()
        else:
            self.adicionar_linha()

        # Configuração do painel inferior com menu fixo
        self.configurar_painel_inferior_com_menu()

        # Definir o widget central
        self.setCentralWidget(central_widget)

     # Define cores para os títulos das colunas
        header = self.table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)
    def configurar_painel_inferior_com_menu(self):
        """Configura o painel inferior com um menu fixo de botões."""
        painel_inferior = QtWidgets.QFrame(self)
        painel_inferior.setStyleSheet("background-color: #f0f0f0;")
        painel_inferior.setFixedHeight(60)
        painel_layout = QtWidgets.QHBoxLayout(painel_inferior)
        painel_layout.setContentsMargins(10, 10, 10, 10)
        painel_layout.setSpacing(20)

        if self.permissao == "suporte":
            # Botão "Salvar Dados"
            salvar_button = QtWidgets.QPushButton("Salvar Dados")
            salvar_button.setIcon(QtGui.QIcon("icons/save.png"))  # Substitua pelo caminho do ícone
            salvar_button.setIconSize(QtCore.QSize(28, 30))  # Define o tamanho do ícone
            salvar_button.setToolTip("Clique para salvar os dados.")  # Dica de ferramenta
            salvar_button.clicked.connect(self.salvar_dados)
            salvar_button.setFont(QtGui.QFont("Helvetica", 10))
            salvar_button.setFixedSize(200, 40)  # Define o tamanho fixo do botão
            painel_layout.addWidget(salvar_button)

            # Botão "Editar Linhas"
            editar_button = QtWidgets.QPushButton("Editar Linhas")
            editar_button.setIcon(QtGui.QIcon("icons/edit.png"))
            editar_button.setIconSize(QtCore.QSize(28, 30))
            editar_button.setToolTip("Clique para editar linhas.")
            editar_button.clicked.connect(self.editar_linha)  # Conectando o clique
            editar_button.setFont(QtGui.QFont("Helvetica", 10))
            editar_button.setFixedSize(200, 40)  # Define o tamanho fixo do botão
            painel_layout.addWidget(editar_button)

            # Botão "Adicionar Registro"
            adicionar_button = QtWidgets.QPushButton("Add + campos registro")
            adicionar_button.setIcon(QtGui.QIcon("icons/buttonadd.png"))
            adicionar_button.setIconSize(QtCore.QSize(28, 30))
            adicionar_button.setToolTip("Clique para adicionar campos.")
            adicionar_button.clicked.connect(self.adicionar_linha)  # Conectando o clique
            adicionar_button.setFont(QtGui.QFont("Helvetica", 10))
            adicionar_button.setFixedSize(200, 40)  # Define o tamanho fixo do botão
            painel_layout.addWidget(adicionar_button)

            # Botão "Remover Registro"
            remover_button = QtWidgets.QPushButton("Remover - campos registro")
            remover_button.setIcon(QtGui.QIcon("icons/buttonadd2.png"))
            remover_button.setIconSize(QtCore.QSize(28, 30))
            remover_button.setToolTip("Clique para remover campos.")
            remover_button.clicked.connect(self.remover_linha)  # Conectando o clique
            remover_button.setFont(QtGui.QFont("Helvetica", 10))
            remover_button.setFixedSize(200, 40)
            painel_layout.addWidget(remover_button)

            # Botão "Sair"
            sair_button = QtWidgets.QPushButton("Sair")
            sair_button.setIcon(QtGui.QIcon("icons/exit.png"))  # Substitua pelo caminho do ícone
            sair_button.setIconSize(QtCore.QSize(28, 30))  # Define o tamanho do ícone
            sair_button.setToolTip("Sair do sistema.")  # Dica de ferramenta
            sair_button.clicked.connect(self.validar_saida)
            sair_button.setFont(QtGui.QFont("Helvetica", 10))
            sair_button.setFixedSize(200, 40)
            painel_layout.addWidget(sair_button)

        if self.permissao == "operacaopax":
            # Botão "Salvar Dados"
            salvar_button = QtWidgets.QPushButton("Salvar")
            salvar_button.setIcon(QtGui.QIcon("icons/save.png"))  # Substitua pelo caminho do ícone
            salvar_button.setIconSize(QtCore.QSize(28, 30))  # Define um tamanho menor para o ícone
            salvar_button.setToolTip("Clique para salvar os dados.")  # Dica de ferramenta
            salvar_button.clicked.connect(self.salvar_registro_multiplas_vezes)
            salvar_button.setFont(QtGui.QFont("Helvetica", 10))  # Fonte menor
            salvar_button.setFixedSize(300, 40)  # Define o tamanho fixo do botão
            painel_layout.addWidget(salvar_button)

            # Botão "Sair"
            sair_button = QtWidgets.QPushButton("Sair")
            sair_button.setIcon(QtGui.QIcon("icons/exit.png"))  # Substitua pelo caminho do ícone
            sair_button.setIconSize(QtCore.QSize(28, 30))  # Define um tamanho menor para o ícone
            sair_button.setToolTip("Sair do sistema.")  # Dica de ferramenta
            sair_button.clicked.connect(self.validar_saida)
            sair_button.setFont(QtGui.QFont("Helvetica", 10))  # Fonte menor
            sair_button.setFixedSize(300, 40)  # Define o tamanho fixo do botão
            painel_layout.addWidget(sair_button)

        self.layout_principal.addWidget(painel_inferior)

    def abrir_filtro_avancado(self):
        """Abre o modal de filtro avançado."""
        dialog = FiltroAvancadoDialog(self.colunas, self.permissao, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            # Obtém o filtro como uma lista de tuplas
            filtros = [dialog.get_filter()]
            if not filtros[0][2]:  # Verifica se o valor do filtro está vazio
                QMessageBox.warning(
                    self, "Aviso", "Digite pelo menos um valor para filtrar."
                )
                return

            # Verificar se todos os filtros têm exatamente três elementos
            for filtro in filtros:
                if len(filtro) != 3:
                    QMessageBox.critical(
                        self,
                        "Erro",
                        "Formato de filtro inválido. Cada filtro deve conter exatamente três elementos: coluna, operador e valor."
                    )
                    return

            self.aplicar_filtro_avancado(filtros)

    def aplicar_filtro_avancado(self, filtros):
        """Aplica os filtros na tabela com base nos filtros fornecidos."""
        try:
            query = "SELECT * FROM appordem WHERE "
            parametros = []
            for coluna, operador, valor in filtros:
                coluna_db = coluna.replace(" ", "")
                if operador == "LIKE":
                    valor = f"%{valor.lower()}%"
                query += f"LOWER({coluna_db}) {operador} ? AND "
                parametros.append(valor.lower())
            query = query[:-4]  # Remove o último " AND "

            self.cursor.execute(query, parametros)
            dados_filtrados = self.cursor.fetchall()

            if not dados_filtrados:  # Verificar se nenhum registro foi encontrado
                QMessageBox.information(
                    self,
                    "Pesquisa",
                    "Nenhum registro encontrado para os filtros aplicados."
                )
            else:
                self.atualizar_table(dados_filtrados)

        except sqlite3.OperationalError as e:
            QMessageBox.critical(
                self, "Erro", f"Erro na consulta SQL: {e}. Verifique se o nome da coluna está correto."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar o filtro: {e}")

    def limpar_filtro_avancado(self):
        """Limpa o filtro avançado e restaura todos os dados na tabela."""
        try:
            # Limpa a entrada de filtro avançado, se houver
            self.dados_filtrados = []
            self.carregar_dados()
            QMessageBox.information(
                self, "Sucesso", "Filtro avançado limpo com sucesso!")
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao limpar o filtro avançado: {e}")

    def gerar_cor(self, cliente):
        """Gera uma cor única baseada no nome do cliente."""
        hash_cliente = sum(ord(char) for char in cliente)
        r = (hash_cliente * 37) % 255
        g = (hash_cliente * 73) % 255
        b = (hash_cliente * 53) % 255
        return QtGui.QColor(r, g, b)

    #                 self.aplicar_cor_status(item)
    def carregar_dados(self):
        """Carrega os dados do banco na tabela, aplica cores aos clientes e ao status."""
        try:
            self.table.setRowCount(0)  # Limpa a tabela antes de carregar novos dados
            self.table.setUpdatesEnabled(False)  # Desabilita atualizações da tabela temporariamente

            self.cursor.execute("SELECT * FROM appordem")
            dados = self.cursor.fetchall()

            self.table.setRowCount(len(dados))  # Define o número de linhas da tabela

            for row_position, row_data in enumerate(dados):
                # Obtém o cliente da linha (assumindo que é a primeira coluna)
                cliente = row_data[1]
                cor_cliente = self.gerar_cor(cliente)

                for col_num, data in enumerate(row_data):
                    # Converte valores em string para exibição e tooltip
                    valor = str(data) if data is not None else "Valor não definido"
                    item = QtWidgets.QTableWidgetItem(str(valor))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # Desabilita edição
                    item.setToolTip(valor)  # Adiciona o tooltip ao item
                    self.table.setItem(row_position, col_num, item)

                    # Aplica a cor ao cliente
                    if col_num == 1:  # Coluna 'Cliente'
                        item.setBackground(cor_cliente)
                        item.setForeground(QtGui.QColor("white"))

                    # Aplica a cor ao status
                    if col_num == 16:  # Coluna 'Status'
                        self.aplicar_cor_status(item)

            self.table.setUpdatesEnabled(True)  # Reabilita atualizações da tabela
            # Ajusta o tamanho das colunas
            # self.table.resizeColumnsToContents()  

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar os dados: {e}")

    def aplicar_cor_status(self, item):
        """Define as cores das células com base no valor de status."""
        if item.text() == "PENDENTE":
            item.setBackground(QtGui.QColor("#e74c3c"))  # Vermelho
            item.setForeground(QtGui.QColor("white"))
        elif item.text() == "CONCLUIDO":
            item.setBackground(QtGui.QColor("#2ecc71"))  # Verde
            item.setForeground(QtGui.QColor("white"))

    def colorir_status(self, item):
        """Aplica as cores às células com base no valor de status."""
        if self.table.columnCount() > 15 and item.column() == 15:
            self.aplicar_cor_status(item)

    def ir_para_ultimo_registro(self):
        """Navega para o último registro do QTableWidget."""
        try:
            # Obtém o número de todas as linhas no QTableWidget
            todas_linhas = self.table.rowCount()
            if todas_linhas > 0:
                # Pega o índice da última linha
                ultimo_id = todas_linhas - 1
                # Seleciona e foca no último registro na segunda coluna (índice 1)
                self.table.setCurrentCell(ultimo_id, 1)
                self.table.scrollToItem(self.table.item(ultimo_id, 1))
            else:
                QMessageBox.information(
                    self, "Informação", "Não há registros no QTableWidget.")
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao navegar para o último registro: {e}")

    def exportar_dados(self):
        dados = []
        for row in range(self.table.rowCount()):
            linha = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                linha.append(item.text() if item else "")
            dados.append(linha)

        if not dados:
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
            return

        df = pd.DataFrame(dados, columns=self.colunas)
        options = QFileDialog.Options()
        file, _ = QFileDialog.getSaveFileName(self, "Salvar Dados Exportados", "",
                                              "Excel files (*.xlsx);;CSV files (*.csv)", options=options)
        if file:
            try:
                if file.endswith(".xlsx"):
                    df.to_excel(file, index=False)
                else:
                    df.to_csv(file, index=False, sep=";")
                QMessageBox.information(
                    self, "Sucesso", f"Dados exportados com sucesso:\n{file}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao exportar os dados: {e}")

    def salvar_dados(self):
        """Salva os dados do formulário no banco de dados."""
        try:
            registros_para_salvar = []

            # Itera sobre as linhas do formulário dinâmico
            for frame_linha, inputs_linha in self.input_rows:
                registro = []
                valores_obrigatorios = {"Modelo": "", "Serial Number": "", "Preparador": ""}

                for widget, coluna in zip(inputs_linha, self.placeholders):
                    if isinstance(widget, QtWidgets.QLineEdit):
                        valor = widget.text().strip()
                    elif isinstance(widget, QtWidgets.QComboBox):
                        valor = widget.currentText().strip()
                    else:
                        valor = ""

                    # Verificar campos obrigatórios
                    if coluna in valores_obrigatorios:
                        valores_obrigatorios[coluna] = valor

                    registro.append(valor)

                # Verificar se algum campo obrigatório está vazio
                campos_vazios = [col for col, val in valores_obrigatorios.items() if not val]
                if campos_vazios:
                    QMessageBox.warning(
                        self,
                        "Campos Obrigatórios Vazios",
                        f"Os seguintes campos obrigatórios estão vazios: {', '.join(campos_vazios)}",
                    )
                    return  # Interrompe o processo de salvamento

                # Adiciona a data atual como DataEnvio
                registro.append(datetime.now().strftime("%d/%m/%Y"))
                registros_para_salvar.append(registro)

            # Insere os registros no banco de dados
            for registro in registros_para_salvar:
                self.cursor.execute("""
                    INSERT INTO appordem (
                        Cliente, Modelo, PartNumber, SerialNumber, VersaoSO,
                        VersaoBoot, ModoDebugRelease, PUK, VersaoRadio, VersaoApp,
                        Configurador, PerfilChave, Preparador, Obs, OrdemService, Status, DataEnvio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, registro)

            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Dados salvos com sucesso!")

            # Atualiza a tabela no layout
            self.carregar_dados()

            # Limpa o formulário após salvar
            for frame_linha, inputs_linha in self.input_rows:
                for widget in inputs_linha:
                    if isinstance(widget, QtWidgets.QLineEdit):
                        widget.clear()
                    elif isinstance(widget, QtWidgets.QComboBox):
                        widget.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar os dados: {e}")


    def configurar_campos_fixos(self):
        """Configura os campos fixos para entrada de dados."""
        colunas_permitidas = ["Cliente", "Ordem Service", "Status", "Data Envio"]

        self.frame_campos = QtWidgets.QFrame(self.frame_inputs)
        self.frame_campos.setLayout(QtWidgets.QHBoxLayout())
        self.frame_inputs.layout().addWidget(self.frame_campos)

        self.inputs_campos = []

        for coluna in colunas_permitidas:
            frame_campo = QtWidgets.QFrame(self.frame_campos)
            frame_campo.setLayout(QtWidgets.QVBoxLayout())
            self.frame_campos.layout().addWidget(frame_campo)

            label = QtWidgets.QLabel(coluna)
            # Aplicar estilo para reduzir o tamanho do QLabel e aumentar o texto
            label.setStyleSheet(
                "font-size: 15px; height: 15px; margin-bottom: 5px; font-weight: bold; color: #333;"
            )
            frame_campo.layout().addWidget(label)

            if coluna == "Status":
                combobox = QtWidgets.QComboBox()
                combobox.addItems(["PENDENTE"])  # Apenas "PENDENTE"
                combobox.setEnabled(False)  # Desabilitar interação do usuário
                combobox.setFixedSize(120, 30)  # Dimensão reduzida
                frame_campo.layout().addWidget(combobox)
                self.inputs_campos.append(combobox)
            elif coluna == "Data Envio":
                entry = QtWidgets.QLineEdit(datetime.now().strftime("%d/%m/%Y"))
                entry.setEnabled(False)  # Bloqueia edição manual
                entry.setFixedSize(120, 30)  # Dimensão reduzida
                entry.setStyleSheet("font-size: 16px; padding: 2px;")  # Ajustar texto interno
                frame_campo.layout().addWidget(entry)
                self.inputs_campos.append(entry)
            elif coluna == "Ordem Service":
                entry = QtWidgets.QLineEdit()
                entry.setFixedSize(150, 30)  # Dimensão reduzida para Ordem Service
                entry.setStyleSheet("font-size: 16px; padding: 2px;")  # Ajustar texto interno
                frame_campo.layout().addWidget(entry)
                entry.textChanged.connect(self.convert_to_uppercase)
                self.inputs_campos.append(entry)
            else:
                entry = QtWidgets.QLineEdit()
                entry.setStyleSheet("font-size: 16px; padding: 2px;")  # Ajustar texto interno
                frame_campo.layout().addWidget(entry)
                entry.textChanged.connect(self.convert_to_uppercase)
                self.inputs_campos.append(entry)

        # Campo para quantidade de registros
        frame_quantidade = QtWidgets.QFrame(self.frame_inputs)
        frame_quantidade.setLayout(QtWidgets.QVBoxLayout())
        self.frame_inputs.layout().addWidget(frame_quantidade)


        label_quantidade = QtWidgets.QLabel("Quantidade de Terminal (1-50)")
        label_quantidade.setStyleSheet(
            "font-size: 15px; height: 15px; margin-bottom: 5px; font-weight: bold; color: #333;"
        )
        frame_quantidade.layout().addWidget(label_quantidade)

        self.quantidade_input = QtWidgets.QSpinBox()
        self.quantidade_input.setRange(1, 50)
        self.quantidade_input.setValue(1)  # Valor padrão
        self.quantidade_input.setFixedSize(80, 25)  # Dimensões menores
        self.quantidade_input.setStyleSheet(
            "font-size: 16px; padding: 2px;"
        )
        frame_quantidade.layout().addWidget(self.quantidade_input)


    def salvar_registro_multiplas_vezes(self):
        """Salva o registro fixo no banco de dados a quantidade de vezes especificada."""
        try:
            quantidade = self.quantidade_input.value()  # Quantidade de vezes a persistir
            registro = {}

            # Obter os valores dos campos fixos
            for coluna, widget in zip(["Cliente", "Ordem Service", "Status", "Data Envio"], self.inputs_campos):
                if isinstance(widget, QtWidgets.QLineEdit):
                    valor = widget.text().strip()
                elif isinstance(widget, QtWidgets.QComboBox):
                    valor = widget.currentText().strip()
                else:
                    valor = ""

                # Verificar se "Cliente" e "Ordem Service" estão preenchidos
                if coluna in ["Cliente", "Ordem Service"] and not valor:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Campo Obrigatório",
                        f"O campo {coluna} é obrigatório."
                    )
                    return

                registro[coluna] = valor

            # Persistir os registros no banco de dados
            for _ in range(quantidade):
                self.cursor.execute("""
                    INSERT INTO appordem (Cliente, OrdemService, Status, DataEnvio)
                    VALUES (?, ?, ?, ?)
                """, (registro["Cliente"], registro["Ordem Service"], registro["Status"], registro["Data Envio"]))

            self.conn.commit()
            QtWidgets.QMessageBox.information(self, "Sucesso", "Registros salvos com sucesso!")

            # Atualizar tabela após salvar
            self.carregar_dados()

            # Limpar os campos de entrada
            for widget in self.inputs_campos:
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.clear()
                elif isinstance(widget, QtWidgets.QComboBox):
                    widget.setCurrentIndex(0)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar os dados: {e}")

    def adicionar_linha(self):
        """Adiciona uma linha de campos de entrada com rótulos acima."""
        if len(self.input_rows) >= 8:
            QtWidgets.QMessageBox.warning(
                self, "Limite atingido", "O número máximo de 8 linhas foi atingido.")
            return

        frame_linha = QtWidgets.QFrame(self.frame_inputs)
        frame_linha.setLayout(QtWidgets.QHBoxLayout())
        self.frame_inputs.layout().addWidget(frame_linha)

        inputs_linha = []

        for index, placeholder in enumerate(self.placeholders):
            frame_campo = QtWidgets.QFrame(frame_linha)
            frame_campo.setLayout(QtWidgets.QVBoxLayout())
            frame_linha.layout().addWidget(frame_campo)

            label = QtWidgets.QLabel(placeholder)
            frame_campo.layout().addWidget(label)

            if placeholder == "De/Re":
                combobox = QtWidgets.QComboBox()
                combobox.addItems(["DEBUG", "RELEASE"])
                combobox.setCurrentIndex(0)
                frame_campo.layout().addWidget(combobox)
                input_widget = combobox
                # implementar combo box para Status
            elif placeholder == "Status":
                combobox = QtWidgets.QComboBox()
                combobox.addItems(["PENDENTE", "CONCLUIDO"])
                combobox.setCurrentIndex(0)
                frame_campo.layout().addWidget(combobox)
                input_widget = combobox
            else:
                entry = QtWidgets.QLineEdit()
                entry.textChanged.connect(self.convert_to_uppercase)
                frame_campo.layout().addWidget(entry)
                input_widget = entry

            if self.input_rows:
                _, ultima_linha_inputs = self.input_rows[-1]
                if placeholder not in ["Part Number", "Serial Number"]:
                    if isinstance(input_widget, QtWidgets.QLineEdit):
                        input_widget.setText(ultima_linha_inputs[index].text())
                    elif isinstance(input_widget, QtWidgets.QComboBox):
                        input_widget.setCurrentText(
                            ultima_linha_inputs[index].currentText())

            inputs_linha.append(input_widget)

        self.input_rows.append((frame_linha, inputs_linha))
    def convert_to_uppercase(self, text):
        """Converte o texto para letras maiúsculas."""
        sender = self.sender()
        if isinstance(sender, QtWidgets.QLineEdit):
            cursor_position = sender.cursorPosition()
            sender.setText(text.upper())
            sender.setCursorPosition(cursor_position)

    def remover_linha(self):
        """Remove a última linha de campos de entrada."""
        if self.input_rows:
            frame_linha, _ = self.input_rows.pop()
            frame_linha.deleteLater()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Aviso", "Não há mais linhas para remover.")
            
    def editar_linha(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma ou mais linhas para editar.")
            return

        # Colunas editáveis no modal
        colunas_editaveis = [
            "Modelo", "Part Number", "Serial Number", "Versao SO", "Versao Boot",
            "DebugOuRelease", "PUK", "Versao Radio", "Versao App", "Configurador",
            "Perfil Chaves", "Preparador", "Obs", "Status"
        ]

        # Identificar os índices correspondentes em self.colunas
        indices_editaveis = [self.colunas.index(col) for col in colunas_editaveis]

        # Coletar dados das linhas selecionadas
        linhas_dados = []
        for row in selected_rows:
            data = [
                self.table.item(row.row(), col).text() if self.table.item(row.row(), col) else ""
                for col in indices_editaveis
            ]
            linhas_dados.append(data)

        # Abrir o modal para editar dados
        modal = EditarModal(self)
        modal.set_data_multiplas_linhas(linhas_dados)

        if modal.exec_() == QDialog.Accepted:
            updated_linhas_dados = modal.get_data_multiplas_linhas()

            # Convertendo todos os dados para maiúsculas antes de salvar
            updated_linhas_dados = [
                [value.upper() if isinstance(value, str) else value for value in linha]
                for linha in updated_linhas_dados
            ]

            # Atualizar os dados na tabela visual e no banco de dados
            for row, updated_data in zip(selected_rows, updated_linhas_dados):
                self.atualizar_registro(row.row(), updated_data, indices_editaveis)

    def atualizar_registro(self, row, updated_data, indices_editaveis):
        try:
            # Obter o ID do registro para atualizar no banco
            record_id = self.table.item(row, 0).text()  # Supondo que a coluna 'id' é a primeira
            # Obter a data e hora atual
            data_envio_atual = datetime.now().strftime('%d/%m/%Y')
            # Atualiza o banco de dados
            self.cursor.execute("""
                UPDATE appordem SET
                    Modelo=?, PartNumber=?, SerialNumber=?, VersaoSO=?, VersaoBoot=?, 
                    ModoDebugRelease=?, PUK=?, VersaoRadio=?, VersaoApp=?, Configurador=?, PerfilChave=?, 
                    Preparador=?, Obs=?, Status=?, DataEnvio=?
                WHERE id=?
            """, (*updated_data, data_envio_atual, record_id))

            # Confirma a transação
            self.conn.commit()

            # Atualizar a tabela visual
            for col, value in zip(indices_editaveis, updated_data):
                self.table.setItem(row, col, QtWidgets.QTableWidgetItem(value))
            # Atualizar a coluna Data Envio na tabela visual (supondo que ela exista)
            col_data_envio = self.colunas.index("Data Envio")  # Certifique-se de que a coluna exista
            self.table.setItem(row, col_data_envio, QtWidgets.QTableWidgetItem(data_envio_atual))
            QMessageBox.information(self, "Sucesso", f"Cliente de ID {record_id} atualizado com sucesso!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar os dados: {e}")
            self.conn.rollback()  # Descomente se estiver usando transações
    

    def atualizar_table(self, dados):
        """Atualiza os dados da tabela com os resultados fornecidos."""
        self.table.setRowCount(0)
        for row_data in dados:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_position, col_num, QtWidgets.QTableWidgetItem(str(data)))

    def validar_saida(self):
        if QMessageBox.question(self, "Confirmação", "Tem certeza que deseja sair?") == QMessageBox.Yes:
            self.conn.close()
            self.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = TelaOrdem("username", "suporte")  # Passe os parâmetros desejados
    main.show()
    sys.exit(app.exec_())
