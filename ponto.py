from datetime import timedelta
import sqlite3
import datetime
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

# Conectar ao banco de dados SQLite
conexao = sqlite3.connect('ponto.db')

# Criar a tabela "registro_ponto" no banco de dados, se ainda não existir
cursor = conexao.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS registro_ponto
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tipo TEXT,
                  horario TEXT)''')
conexao.commit()

# Criar a tabela "horas_trabalhadas" no banco de dados, se ainda não existir
cursor.execute('''CREATE TABLE IF NOT EXISTS horas_trabalhadas
                  (dia TEXT PRIMARY KEY,
                  horas REAL)''')
conexao.commit()

# Função para exibir os registros na caixa de listagem
def atualizar_registros():
    lista_registros.delete(0, END)
    cursor.execute("SELECT * FROM registro_ponto")
    registros = cursor.fetchall()

    for registro in registros:
        lista_registros.insert(END, registro)

# Função para registrar o horário no banco de dados
def registrar_horario():
    tipo = opcao_var.get()
    horario = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if tipo == "":
        # Nenhuma opção selecionada, exibir uma mensagem de erro
        messagebox.showerror("Erro", "Selecione um tipo de horário")
        return    
    
    cursor.execute("INSERT INTO registro_ponto (tipo, horario) VALUES (?, ?)", (tipo, horario))
    conexao.commit()

    if tipo == "Saída":
        # Consulta SQL para recuperar registros do dia atual
        cursor.execute("SELECT horario, tipo FROM registro_ponto WHERE DATE(horario) = DATE('now') ORDER BY horario")
        registros = cursor.fetchall()

        # Variáveis para calcular as horas trabalhadas
        entrada = None
        saida = None
        horas_trabalhadas = timedelta()

        # Percorrer os registros
        for registro in registros:
            horario = datetime.datetime.strptime(registro[0], "%Y-%m-%d %H:%M:%S")
            tipo_registro = registro[1]

            if tipo_registro == "Entrada":
                entrada = horario
            elif tipo_registro == "Saída":
                saida = horario
            elif tipo_registro not in ["Almoço_E", "Almoço_S", "Café_E", "Café_S"]:
                # Calcular as horas trabalhadas apenas se não for um intervalo não trabalhado
                if entrada and saida:
                    horas_trabalhadas += saida - entrada
                entrada = None
                saida = None

        # Calcular as horas trabalhadas
        if entrada and saida:
            horas_trabalhadas += saida - entrada

        # Converter a diferença de tempo em horas (float)
        horas_trabalhadas = horas_trabalhadas.total_seconds() / 3600

        # Inserir as horas trabalhadas na tabela "horas_trabalhadas"
        dia = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO horas_trabalhadas (dia, horas) VALUES (?, ?)", (dia, horas_trabalhadas))
        conexao.commit()

# Função para gerar o relatório em um arquivo de texto
def gerar_relatorio():
    # Consulta SQL para recuperar as horas trabalhadas
    cursor.execute("SELECT * FROM horas_trabalhadas")
    registros = cursor.fetchall()

    # Criar o conteúdo do relatório
    conteudo = "Relatório de Horas Trabalhadas\n\n"
    for registro in registros:
        dia = registro[0]
        horas = registro[1]
        conteudo += f"Dia: {dia}\nHoras trabalhadas: {horas:.2f}\n\n"

    # Abrir uma caixa de diálogo para salvar o arquivo
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        # Salvar o conteúdo no arquivo
        with open(file_path, "w") as file:
            file.write(conteudo)
            messagebox.showinfo("Relatório", "Relatório gerado com sucesso!")
    else:
        messagebox.showinfo("Relatório", "Operação cancelada pelo usuário.")

# Criar janela principal
janela = Tk()
janela.title("Controle de Ponto")

# Criar variável para armazenar a opção selecionada
opcao_var = StringVar(value="")

# Criar rótulo e opções
rotulo = Label(janela, text="Selecione o tipo de horário:")
rotulo.grid(row=0, column=0, columnspan=2)

opcao_entrada = Radiobutton(janela, text="Entrada", variable=opcao_var, value="Entrada")
opcao_entrada.grid(row=1, column=0)

opcao_saida = Radiobutton(janela, text="Saída", variable=opcao_var, value="Saída")
opcao_saida.grid(row=1, column=1)

opcao_almoco_e = Radiobutton(janela, text="Almoço_E", variable=opcao_var, value="Almoço_E")
opcao_almoco_e.grid(row=2, column=0)

opcao_almoco_s = Radiobutton(janela, text="Almoço_S", variable=opcao_var, value="Almoço_S")
opcao_almoco_s.grid(row=2, column=1)

opcao_cafe_e = Radiobutton(janela, text="Café_E", variable=opcao_var, value="Café_E")
opcao_cafe_e.grid(row=3, column=0)

opcao_cafe_s = Radiobutton(janela, text="Café_S", variable=opcao_var, value="Café_S")
opcao_cafe_s.grid(row=3, column=1)

# Criar botão de registro
botao_registrar = Button(janela, text="Registrar", command=registrar_horario)
botao_registrar.grid(row=4, column=0, columnspan=2)

# Criar botão para exibir registros
botao_exibir_registros = Button(janela, text="Exibir Registros", command=atualizar_registros)
botao_exibir_registros.grid(row=5, column=0, columnspan=2)

# Criar lista de registros
lista_registros = Listbox(janela)
lista_registros.grid(row=6, column=0, columnspan=2)

# Criar botão para gerar relatório
botao_relatorio = Button(janela, text="Relatório", command=gerar_relatorio)
botao_relatorio.grid(row=7, column=0, columnspan=2)

# Iniciar a janela
janela.mainloop()

# Fechar a conexão com o banco de dados
conexao.close()