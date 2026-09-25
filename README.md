# 🏢 Consulta de CNPJ - Streamlit

Aplicação desenvolvida em **Python + Streamlit** para consulta de dados cadastrais de empresas brasileiras através da **API pública da CNPJá**.

O sistema realiza consultas de CNPJ, exibe informações detalhadas da empresa e permite a exportação dos resultados para Excel.

---

## 🚀 Funcionalidades

✅ Consulta de CNPJ em tempo real utilizando a API pública da CNPJá

✅ Validação completa de CNPJ:
- Quantidade de dígitos
- Dígitos verificadores
- Sequências inválidas

✅ Exibição de informações cadastrais:
- Razão Social
- Nome Fantasia
- Situação Cadastral
- Data de Abertura
- Natureza Jurídica
- Porte da Empresa
- Capital Social

✅ Endereço completo:
- Logradouro
- Número
- Complemento
- Bairro
- Município
- UF
- CEP

✅ Informações tributárias:
- Simples Nacional
- MEI

✅ CNAE Principal

✅ CNAEs Secundários

✅ Telefones

✅ E-mails

✅ Quadro societário

✅ Exportação para Excel com múltiplas abas

✅ Cache de consultas por 1 hora para reduzir chamadas à API

✅ Tratamento completo de erros:
- Timeout
- Proxy
- SSL
- Limites da API
- Falhas de conexão

✅ Instalação automática das dependências

✅ Inicialização automática do Streamlit

✅ HTTPS seguro utilizando TrustStore (sem uso de `verify=False`)

---

## 📷 Interface

A aplicação possui interface web desenvolvida em Streamlit contendo:

- Consulta de CNPJ
- Indicadores principais
- Dados cadastrais
- Endereço completo
- CNAEs
- Telefones
- E-mails
- Quadro societário
- Exportação para Excel
- Visualização da resposta JSON

---

## 🛠 Tecnologias Utilizadas

- Python 3.9+
- Streamlit
- Requests
- Pandas
- OpenPyXL
- TrustStore
- API Pública CNPJá

---

## 📦 Dependências

O aplicativo verifica e instala automaticamente as bibliotecas ausentes:

```txt
streamlit
requests
pandas
truststore
openpyxl
```

---

## ⚙️ Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/consulta-cnpj-streamlit.git
```

### 2. Entrar na pasta

```bash
cd consulta-cnpj-streamlit
```

### 3. Executar a aplicação

```bash
python consulta_cnpj.py
```

ou através do arquivo BAT:

```bash
rodar.bat
```

---

## 🔄 Instalação Automática

Ao executar o programa:

1. Verifica as dependências instaladas.
2. Instala apenas as bibliotecas ausentes.
3. Inicia automaticamente o Streamlit.
4. Abre o navegador.
5. Disponibiliza a aplicação para uso.

Não é necessário executar manualmente:

```bash
pip install -r requirements.txt
```

---

## 🔐 Segurança

O projeto mantém a validação HTTPS ativa em todas as consultas.

Para compatibilidade com ambientes corporativos utiliza:

```python
import truststore

truststore.inject_into_ssl()
```

### Boas práticas adotadas

✅ Certificados do sistema operacional utilizados automaticamente

✅ Validação SSL mantida

✅ Compatível com ambientes corporativos

❌ Não utiliza `verify=False`

❌ Não desabilita HTTPS

---

## 📊 Exportação para Excel

Após a consulta é possível baixar um arquivo XLSX contendo:

### Dados Gerais
- CNPJ
- Razão Social
- Nome Fantasia
- Situação Cadastral
- Data de Abertura
- Natureza Jurídica
- Porte
- Capital Social
- Endereço
- Simples Nacional

### CNAEs Secundários

Lista completa das atividades secundárias.

### Telefones

Todos os telefones cadastrados.

### E-mails

Todos os e-mails cadastrados.

### Sócios

Quadro societário da empresa.

---

## 🌐 API Utilizada

Projeto baseado na API Open da CNPJá:

- Site: https://cnpja.com
- Documentação: https://cnpja.com/api/open

---

## ⚠️ Limitações

A API pública possui limites de utilização definidos pela própria CNPJá.

Quando o limite for atingido, a aplicação exibirá a mensagem:

```text
O limite de consultas da API foi atingido.
Aguarde um minuto antes de tentar novamente.
```

---

## 👨‍💻 Autor

**Marcus Vinicius Bernardi Calegari**

Analista Administrativo Pleno

Especialista em:
- Automação de Processos
- Python
- Power BI
- Power Platform
- Inteligência Artificial
- Transformação Digital

LinkedIn:

https://www.linkedin.com/in/marcus-vinicius-calegari

---

## 📄 Licença

Distribuído sob a licença MIT.

Sinta-se à vontade para utilizar, modificar e contribuir com melhorias.