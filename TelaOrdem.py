from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog
import sqlite3
import pandas as pd
from datetime import datetime
from random import seed, randint
seed(42)  # Para gerar cores consistentes

class FiltroAvancadoDialog(QDialog):
        def __init__(self, colunas, permissao, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Filtro Avançado")
            # Ajusta o tamanho da janela no cento da tela
            screen = QtWidgets.QDesktopWidget().screenGeometry()
            self.move((screen.width() - 300) // 2, (screen.height() - 300) // 2)
            self.setFixedSize(300, 300)
            self.permissao = permissao

            # Limita as colunas disponíveis para usuários com permissão limitada
            if self.permissao == "limitado":
                self.colunas = ["Cliente", "Ordem Service"]
            else:
                self.colunas = colunas

            self.setup_ui()

        def setup_ui(self):
            layout = QtWidgets.QVBoxLayout(self)

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

            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            layout.addWidget(button_box)

        def get_filter(self):
            coluna = self.coluna_combobox.currentText()
            operador = self.operador_combobox.currentText()
            valor = self.valor_input.text().strip()
            return coluna, operador, valor

class TelaOrdem(QtWidgets.QMainWindow):
    def __init__(self, username, permissao):
        super().__init__()
        self.setWindowTitle("Manipulação de Banco de Dados e Filtros")
        self.setGeometry(100, 100, 1400, 800)
        
        self.username = username
        self.permissao = permissao
        
        self.conn = sqlite3.connect("dados.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela()
        
        self.colunas = [
            "Cliente", "Modelo", "Part Number", "Serial Number", "Versao SO",
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
        CREATE TABLE IF NOT EXISTS ordem (
            Cliente TEXT NOT NULL,
            Modelo TEXT NOT NULL,
            PartNumber TEXT,
            SerialNumber TEXT NOT NULL,
            VersaoSO TEXT NOT NULL,
            VersaoBoot TEXT,
            ModoDebugRelease TEXT,
            PUK TEXT,
            VersaoRadio TEXT,
            VersaoApp TEXT,
            Configurador TEXT,
            PerfilChave TEXT,
            Preparador TEXT NOT NULL,
            Obs TEXT,
            OrdemService TEXT,
            Status TEXT,
            DataEnvio TEXT
        )
        """)
        self.conn.commit()

    def setup_ui(self):
        # Criação do layout principal
        print("Inicializando a interface...")
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Label do usuário
        user_label = QtWidgets.QLabel(f"Usuário logado: {self.username}")
        user_label.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
        layout.addWidget(user_label)

        # Layout para o botão "Exportar Dados" acima da tabela
        if self.permissao == "total":
            export_layout = QtWidgets.QHBoxLayout()
            export_button = QtWidgets.QPushButton("Exportar Dados")
            export_button.clicked.connect(self.exportar_dados)
            export_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            export_layout.addWidget(export_button)
            export_layout.addStretch()  
            layout.addLayout(export_layout)  # Adiciona o layout com o botão acima da tabela

        # Layout para os botões de filtro acima da tabela e alinhados à direita
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addStretch()  # Adiciona espaço flexível para empurrar os botões para a direita

        filter_advanced_button = QtWidgets.QPushButton("Filtro Avançado")
        filter_advanced_button.clicked.connect(self.abrir_filtro_avancado)
        filter_advanced_button.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        filter_advanced_button.setFont(QtGui.QFont("Helvetica", 11, QtGui.QFont.Bold))
        filter_layout.addWidget(filter_advanced_button)

        clear_advanced_filter_button = QtWidgets.QPushButton("Limpar Filtro")
        clear_advanced_filter_button.clicked.connect(self.limpar_filtro_avancado)
        clear_advanced_filter_button.setStyleSheet("background-color: #6495ED; color: white; font-weight: bold;")
        clear_advanced_filter_button.setFont(QtGui.QFont("Helvetica", 11, QtGui.QFont.Bold))
        filter_layout.addWidget(clear_advanced_filter_button)

        layout.addLayout(filter_layout)  # Adiciona o layout com os botões de filtro acima da tabela

        # Criação do QTableWidget
        self.table = QtWidgets.QTableWidget()
        print("Tabela inicializada:", self.table)
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self.colorir_status)  # Adiciona o evento para colorir dinamicamente
        layout.addWidget(self.table)

        # Frame para os campos de entrada
        self.frame_inputs = QtWidgets.QFrame(self)
        self.frame_inputs.setLayout(QtWidgets.QVBoxLayout())
        layout.addWidget(self.frame_inputs)

        # Layout para os botões de ações gerais
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(35)  # Define o espaçamento entre os botões como 10px
        actions_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens adicionais

        if self.permissao == "total":
            save_button = QtWidgets.QPushButton("Salvar Dados")
            save_button.clicked.connect(self.salvar_dados)
            save_button.setStyleSheet("background-color: #228B22; color: white; font-weight: bold;")
            save_button.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
            actions_layout.addWidget(save_button)

            add_row_button = QtWidgets.QPushButton("Adicionar +campos Registro")
            add_row_button.clicked.connect(self.adicionar_linha)
            add_row_button.setStyleSheet("background-color: #2F4F4F; color: white; font-weight: bold;")
            add_row_button.setFont(QtGui.QFont("Helvetica", 10, QtGui.QFont.Bold))
            actions_layout.addWidget(add_row_button)

            remove_row_button = QtWidgets.QPushButton("Remover Linha")
            remove_row_button.clicked.connect(self.remover_linha)
            remove_row_button.setStyleSheet("background-color: #DC143C; color: white; font-weight: bold;")
            remove_row_button.setFont(QtGui.QFont("Helvetica", 10, QtGui.QFont.Bold))
            actions_layout.addWidget(remove_row_button)

            update_status_button = QtWidgets.QPushButton("Atualizar Status para CONCLUÍDO")
            update_status_button.clicked.connect(self.atualizar_status)
            update_status_button.setStyleSheet("background-color: #3CB371; color: white; font-weight: bold;")
            update_status_button.setFont(QtGui.QFont("Helvetica", 10, QtGui.QFont.Bold))
            actions_layout.addWidget(update_status_button)

        ultimo_registro_button = QtWidgets.QPushButton("Ultimo Registro")
        ultimo_registro_button.clicked.connect(self.ir_para_ultimo_registro)
        ultimo_registro_button.setStyleSheet("background-color: #00008B; color: white; font-weight: bold;")
        ultimo_registro_button.setFont(QtGui.QFont("Helvetica", 10, QtGui.QFont.Bold))
        actions_layout.addWidget(ultimo_registro_button)

        sair_button = QtWidgets.QPushButton("Sair")
        sair_button.clicked.connect(self.validar_saida)
        sair_button.setStyleSheet("background-color: #A52A2A; color: white; font-weight: bold;")
        sair_button.setFont(QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold))
        actions_layout.addWidget(sair_button)

        # Adiciona o layout dos botões ao layout principal
        layout.addLayout(actions_layout)

        # Define o widget central
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

    def abrir_filtro_avancado(self):
        """Abre o modal de filtro avançado."""
        dialog = FiltroAvancadoDialog(self.colunas, self.permissao, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            filtros = [dialog.get_filter()]  # Obtém o filtro como uma lista de tuplas
            if not filtros[0][2]:  # Verifica se o valor do filtro está vazio
                QMessageBox.warning(self, "Aviso", "Digite pelo menos um valor para filtrar.")
                return

            # Verificar se todos os filtros têm exatamente três elementos
            for filtro in filtros:
                if len(filtro) != 3:
                    QMessageBox.critical(self, "Erro", "Formato de filtro inválido. Cada filtro deve conter exatamente três elementos: coluna, operador e valor.")
                    return

            self.aplicar_filtro_avancado(filtros)
    def aplicar_filtro_avancado(self, filtros):
        """Aplica os filtros na tabela com base nos filtros fornecidos."""
        try:
            query = "SELECT * FROM ordem WHERE "
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
            self.atualizar_table(dados_filtrados)
        except sqlite3.OperationalError as e:
            QMessageBox.critical(self, "Erro", f"Erro na consulta SQL: {e}. Verifique se o nome da coluna está correto.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar o filtro: {e}")

    def limpar_filtro_avancado(self):
        """Limpa o filtro avançado e restaura todos os dados na tabela."""
        try:
            # Limpa a entrada de filtro avançado, se houver
            self.dados_filtrados = []
            self.carregar_dados()
            QMessageBox.information(self, "Sucesso", "Filtro avançado limpo com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao limpar o filtro avançado: {e}")

    def gerar_cor(self, cliente):
        """Gera uma cor única baseada no nome do cliente."""
        hash_cliente = sum(ord(char) for char in cliente)
        r = (hash_cliente * 37) % 255
        g = (hash_cliente * 73) % 255
        b = (hash_cliente * 53) % 255
        return QtGui.QColor(r, g, b)

    def carregar_dados(self):
        """Carrega os dados do banco na tabela, aplica cores aos clientes e ao status."""
        self.table.setRowCount(0)
        self.cursor.execute("SELECT * FROM ordem")
        for row_data in self.cursor.fetchall():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Obtém o cliente da linha (assumindo que é a primeira coluna)
            cliente = row_data[0]
            cor_cliente = self.gerar_cor(cliente)

            for col_num, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                self.table.setItem(row_position, col_num, item)

                # Aplica a cor ao cliente
                if col_num == 0:  # Coluna 'Cliente'
                    item.setBackground(cor_cliente)
                    item.setForeground(QtGui.QColor("white"))

                # Aplica a cor ao status
                if col_num == 15:  # Coluna 'Status'
                    self.aplicar_cor_status(item)

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
                # Seleciona e foca no último registro
                self.table.setCurrentCell(ultimo_id, 0)
                self.table.scrollToItem(self.table.item(ultimo_id, 0))
            else:
                QMessageBox.information(self, "Informação", "Não há registros no QTableWidget.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao navegar para o último registro: {e}")

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
                QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso:\n{file}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar os dados: {e}")

    def salvar_dados(self):
        """Salva os dados do formulário no banco de dados."""
        try:
            registros_para_salvar = []

            # Itera sobre as linhas do formulário dinâmico
            for frame_linha, inputs_linha in self.input_rows:
                registro = []
                for widget in inputs_linha:
                    if isinstance(widget, QtWidgets.QLineEdit):
                        registro.append(widget.text().strip())
                    elif isinstance(widget, QtWidgets.QComboBox):
                        registro.append(widget.currentText().strip())
                
                # especificar os campos obrigatórios e mostrar um aviso Cliente, Modelo, SerialNumber Preparador
                if not registro[0] or not registro[1] or not registro[3] or not registro[12]:
                    # mostrar os camppos obrigatórios
                    campos_obrigatorios = ["Cliente", "Modelo", "SerialNumber", "Preparador"]
                    QMessageBox.warning(self, "Aviso", f"Por favor, preencha os campos obrigatórios: {', '.join(campos_obrigatorios)}!")
                    return

                # Adiciona a data atual como DataEnvio
                registro.append(datetime.now().strftime("%d/%m/%Y"))
                registros_para_salvar.append(registro)

            # Insere os registros no banco de dados
            for registro in registros_para_salvar:
                self.cursor.execute("""
                    INSERT INTO ordem (
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

    def adicionar_linha(self):
        """Adiciona uma linha de campos de entrada com rótulos acima."""
        if len(self.input_rows) >= 8:
            QtWidgets.QMessageBox.warning(self, "Limite atingido", "O número máximo de 8 linhas foi atingido.")
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
                frame_campo.layout().addWidget(entry)
                input_widget = entry

            if self.input_rows:
                _, ultima_linha_inputs = self.input_rows[-1]
                if placeholder not in ["Part Number", "Serial Number"]:
                    if isinstance(input_widget, QtWidgets.QLineEdit):
                        input_widget.setText(ultima_linha_inputs[index].text())
                    elif isinstance(input_widget, QtWidgets.QComboBox):
                        input_widget.setCurrentText(ultima_linha_inputs[index].currentText())

            inputs_linha.append(input_widget)

        self.input_rows.append((frame_linha, inputs_linha))

    def remover_linha(self):
        """Remove a última linha de campos de entrada."""
        if self.input_rows:
            frame_linha, _ = self.input_rows.pop()
            frame_linha.deleteLater()
        else:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Não há mais linhas para remover.")

    
    def atualizar_status(self):
        """Atualiza o status da linha selecionada para CONCLUÍDO e salva no banco de dados."""
        try:
            # Obtém a linha selecionada na tabela
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Aviso", "Selecione uma linha para atualizar o status.")
                return
            
            # Obter os dados necessários para identificar o registro
            serial_number_item = self.table.item(selected_row, 3)  # Coluna 'Serial Number'
            status_item = self.table.item(selected_row, 15)  # Coluna 'Status'

            if not serial_number_item or not status_item:
                QMessageBox.warning(self, "Aviso", "Não foi possível identificar o registro.")
                return

            serial_number = serial_number_item.text()
            current_status = status_item.text()

            # Verificar se o status já está "CONCLUÍDO"
            if current_status == "CONCLUIDO":
                QMessageBox.information(self, "Informação", "O status já está definido como CONCLUIDO.")
                return

            # Atualizar a célula da tabela
            self.table.setItem(selected_row, 15, QtWidgets.QTableWidgetItem("CONCLUIDO"))

            # Atualizar o status no banco de dados
            self.cursor.execute("""
                UPDATE ordem
                SET Status = ?
                WHERE SerialNumber = ?
            """, ("CONCLUIDO", serial_number))
            self.conn.commit()

            QMessageBox.information(self, "Sucesso", "Status atualizado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar o status: {e}")

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
    main = TelaOrdem("username", "total")  # Passe os parâmetros desejados
    main.show()
    sys.exit(app.exec_())