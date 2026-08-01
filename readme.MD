# Projeto MatScholar
## Descrição do projeto💡
<p>Um sistema que permite o gerenciamento de uma instituição de ensino, de maneira a possibilitar a criação de salas,
  atribuição de notas, visualização de notas pelos alunos, geração de boletim/histórico das matérias,etc.</p>

## Tecnologias utilizadas🛠️
 -Python;<br>
 -Django;<br>
 -PostgreSQL;<br>
 -Docker;<br>
 -Redis;<br>
 -HTML e CSS;<br>
 -JavaScript.
### Outras tecnologias e bibliotecas essenciais
-Psycopg;<br>
-Argon2.<br>

## Como executar na sua máquina
### 1-Instalar requisitos
```bash
python install -r requirements.txt
```
### 2-Ativar o servidor
```bash
python manage.py runserver
```
### 3- Abrir o link gerado(geralmente 'localhost' )
```bash
System check identified no issues (0 silenced).
May 24, 2026 - 07:42:27
Django version 6.0.3, using settings 'app_clima.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
### 4- Banco de dados
```bash
python manage.py makemigrations
```
e depois
```bash
python manage.py migrate
```
Após isso,crie uma instituição e um usuário com permissão de SUPER via o seu SGBD de preferência.
Entre no usuário SUPER e execute as criações de diretor e professor.
Depois, utilize esses perfis para criar salas,alunos,tarefas,etc.
### 5- Precauções
Lembre-se de criar um arquivo 'local_settings.py' no formato:
```bash
SECRET_KEY = 'chave django'
DEBUG = True
ALLOWED_HOSTS = [HOSTS PERMITIDOS]
```
Com uma SECRET_KEY válida, por isso talvez seja necessário inicializar um app Django e sobrescrever ele com o Projeto MatScholar, atentando-se a deixar a SECRET_KEY intacta.

## Imagens
### Tela de login
<img src="https://github.com/Gmt-santos/Projeto_MatScholar/blob/main/static_files/images/example5.png?raw=true">

### Dashboard do diretor
<img src="https://github.com/Gmt-santos/Projeto_MatScholar/blob/main/static_files/images/example1.png?raw=true">

### Administração de aulas
<img src="https://github.com/Gmt-santos/Projeto_MatScholar/blob/main/static_files/images/example2.png?raw=true">

### Adição e visualização de tarefas
<img src="https://github.com/Gmt-santos/Projeto_MatScholar/blob/main/static_files/images/example3.png?raw=true">

### Status de uma matéria visto pelo estudante
<img src="https://github.com/Gmt-santos/Projeto_MatScholar/blob/main/static_files/images/example4.png?raw=true">