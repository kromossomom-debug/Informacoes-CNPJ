# ============================================================
# CONSULTA DE CNPJ - STREAMLIT
# API pública da CNPJá
#
# O próprio arquivo:
# 1. Verifica as bibliotecas necessárias;
# 2. Instala somente as bibliotecas ausentes;
# 3. Inicia automaticamente o Streamlit;
# 4. Mantém a validação HTTPS habilitada.
# ============================================================


# ============================================================
# INICIALIZADOR E INSTALAÇÃO AUTOMÁTICA
# Este bloco utiliza somente bibliotecas nativas do Python.
# ============================================================

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


# Bibliotecas utilizadas pelo aplicativo.
#
# Formato:
# "nome usado no import": "nome usado pelo pip"
DEPENDENCIAS = {
    "streamlit": "streamlit",
    "requests": "requests",
    "pandas": "pandas",
    "truststore": "truststore",
    "openpyxl": "openpyxl",
}


def biblioteca_instalada(nome_importacao):
    """
    Verifica se uma biblioteca está disponível no Python atual.
    """

    try:
        return importlib.util.find_spec(nome_importacao) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def instalar_dependencias():
    """
    Instala somente as bibliotecas que ainda não estão disponíveis.

    O comando utiliza sys.executable para garantir que o pip seja
    executado pelo mesmo Python utilizado para abrir este arquivo.
    """

    bibliotecas_ausentes = []

    for nome_importacao, nome_pip in DEPENDENCIAS.items():
        if not biblioteca_instalada(nome_importacao):
            bibliotecas_ausentes.append(nome_pip)

    if not bibliotecas_ausentes:
        return

    print()
    print("=" * 65)
    print("PREPARANDO O APLICATIVO DE CONSULTA DE CNPJ")
    print("=" * 65)
    print()
    print("As bibliotecas abaixo precisam ser instaladas:")

    for biblioteca in bibliotecas_ausentes:
        print(f"  - {biblioteca}")

    print()
    print("Iniciando a instalação automática...")
    print("Aguarde até a conclusão.")
    print()

    comando = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        *bibliotecas_ausentes,
    ]

    try:
        subprocess.run(
            comando,
            check=True,
        )

        print()
        print("=" * 65)
        print("BIBLIOTECAS INSTALADAS COM SUCESSO")
        print("=" * 65)
        print()

    except subprocess.CalledProcessError as erro:
        print()
        print("=" * 65)
        print("ERRO NA INSTALAÇÃO DAS BIBLIOTECAS")
        print("=" * 65)
        print()
        print(
            "Não foi possível instalar uma ou mais bibliotecas."
        )
        print()
        print(
            "Verifique a conexão com a internet, a VPN, o proxy "
            "corporativo ou as permissões do seu computador."
        )
        print()
        print(f"Código de saída do pip: {erro.returncode}")

        try:
            input("\nPressione Enter para encerrar...")
        except EOFError:
            pass

        raise SystemExit(1) from erro

    except OSError as erro:
        print()
        print("=" * 65)
        print("NÃO FOI POSSÍVEL EXECUTAR O PIP")
        print("=" * 65)
        print()
        print(f"Detalhes técnicos: {erro}")

        try:
            input("\nPressione Enter para encerrar...")
        except EOFError:
            pass

        raise SystemExit(1) from erro


def iniciar_streamlit():
    """
    Inicia este mesmo arquivo utilizando o servidor do Streamlit.

    Quando o arquivo já estiver sendo executado pelo Streamlit,
    a função simplesmente permite que o restante do código continue.
    """

    ja_iniciado_pelo_streamlit = (
        os.environ.get("CONSULTA_CNPJ_STREAMLIT") == "1"
    )

    if ja_iniciado_pelo_streamlit:
        return

    arquivo_atual = Path(__file__).resolve()

    ambiente = os.environ.copy()
    ambiente["CONSULTA_CNPJ_STREAMLIT"] = "1"

    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(arquivo_atual),
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]

    print()
    print("=" * 65)
    print("INICIANDO O APLICATIVO DE CONSULTA DE CNPJ")
    print("=" * 65)
    print()
    print(f"Arquivo: {arquivo_atual}")
    print()
    print("O aplicativo será aberto no navegador.")
    print("Para encerrar, pressione Ctrl+C neste terminal.")
    print()

    try:
        processo = subprocess.run(
            comando,
            env=ambiente,
            check=False,
        )

        raise SystemExit(processo.returncode)

    except KeyboardInterrupt:
        print()
        print("Aplicativo encerrado pelo usuário.")
        raise SystemExit(0)

    except OSError as erro:
        print()
        print("Não foi possível iniciar o Streamlit.")
        print(f"Detalhes técnicos: {erro}")

        try:
            input("\nPressione Enter para encerrar...")
        except EOFError:
            pass

        raise SystemExit(1) from erro


# Primeiro, instala as bibliotecas ausentes.
instalar_dependencias()

# Depois, inicia corretamente o Streamlit.
iniciar_streamlit()


# ============================================================
# IMPORTAÇÕES DO APLICATIVO
# Estas importações são executadas somente depois da instalação.
# ============================================================

# O truststore deve ser carregado antes do requests.
import truststore

truststore.inject_into_ssl()

import io
import re
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Consulta de CNPJ",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURAÇÕES DA API
# ============================================================

API_BASE_URL = "https://open.cnpja.com/office"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Consulta-CNPJ-Streamlit/1.0",
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_cnpj(cnpj):
    """
    Remove todos os caracteres que não sejam números.
    """

    if not cnpj:
        return ""

    return re.sub(r"\D", "", str(cnpj))


def formatar_cnpj(cnpj):
    """
    Formata um CNPJ com 14 números.
    """

    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14:
        return cnpj

    return (
        f"{cnpj[0:2]}."
        f"{cnpj[2:5]}."
        f"{cnpj[5:8]}/"
        f"{cnpj[8:12]}-"
        f"{cnpj[12:14]}"
    )


def validar_cnpj(cnpj):
    """
    Valida o formato e os dois dígitos verificadores do CNPJ.
    """

    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14:
        return False

    # Elimina sequências repetidas, como 00.000.000/0000-00.
    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(base, pesos):
        soma = sum(
            int(numero) * peso
            for numero, peso in zip(base, pesos)
        )

        resto = soma % 11

        if resto < 2:
            return "0"

        return str(11 - resto)

    primeiro_digito = calcular_digito(
        cnpj[:12],
        [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    segundo_digito = calcular_digito(
        cnpj[:12] + primeiro_digito,
        [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    return cnpj[-2:] == primeiro_digito + segundo_digito


def valor_seguro(valor, padrao="Não informado"):
    """
    Retorna um texto padrão quando o valor estiver vazio.
    """

    if valor is None:
        return padrao

    if isinstance(valor, str) and not valor.strip():
        return padrao

    return valor


def formatar_data(data):
    """
    Converte datas comuns da API para o formato brasileiro.
    """

    if not data:
        return "Não informado"

    formatos = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for formato in formatos:
        try:
            data_convertida = datetime.strptime(
                str(data),
                formato,
            )

            return data_convertida.strftime("%d/%m/%Y")

        except (ValueError, TypeError):
            continue

    return str(data)


def formatar_sim_nao(valor):
    """
    Converte valores booleanos em Sim ou Não.
    """

    if valor is True:
        return "Sim"

    if valor is False:
        return "Não"

    return valor_seguro(valor)


def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira.
    """

    if valor is None or valor == "":
        return "Não informado"

    try:
        numero = float(valor)

        valor_formatado = (
            f"R$ {numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return valor_formatado

    except (ValueError, TypeError):
        return str(valor)


def montar_endereco(dados):
    """
    Monta o endereço completo da empresa.
    """

    endereco = dados.get("address") or {}

    partes = [
        endereco.get("street"),
        endereco.get("number"),
        endereco.get("details"),
        endereco.get("district"),
        endereco.get("city"),
        endereco.get("state"),
        endereco.get("zip"),
    ]

    partes_validas = []

    for parte in partes:
        if parte is not None and str(parte).strip():
            partes_validas.append(str(parte).strip())

    return ", ".join(partes_validas)


def primeiro_valor(dicionario, *chaves):
    """
    Retorna o primeiro valor encontrado entre várias chaves.
    """

    if not isinstance(dicionario, dict):
        return None

    for chave in chaves:
        valor = dicionario.get(chave)

        if valor is not None and str(valor).strip():
            return valor

    return None


# ============================================================
# CONSULTA DA API
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def consultar_cnpj(cnpj):
    """
    Consulta um CNPJ na API pública da CNPJá.

    O resultado fica em cache por uma hora para evitar consultas
    repetidas e ajudar a respeitar o limite da API pública.
    """

    cnpj_limpo = limpar_cnpj(cnpj)

    if not validar_cnpj(cnpj_limpo):
        raise ValueError(
            "O CNPJ informado é inválido. Confira os 14 números "
            "e os dígitos verificadores."
        )

    url = f"{API_BASE_URL}/{cnpj_limpo}"

    try:
        with requests.Session() as sessao:
            sessao.headers.update(HEADERS)

            resposta = sessao.get(
                url,
                timeout=(10, 30),
            )

    except requests.exceptions.SSLError as erro:
        raise ConnectionError(
            "Não foi possível validar o certificado HTTPS. "
            "A rede corporativa pode estar utilizando inspeção SSL. "
            "Confirme se o truststore foi instalado no mesmo Python "
            "utilizado para executar o aplicativo."
        ) from erro

    except requests.exceptions.ProxyError as erro:
        raise ConnectionError(
            "Não foi possível acessar a API pelo proxy da rede. "
            "Verifique a conexão corporativa, a VPN ou as "
            "configurações de proxy."
        ) from erro

    except requests.exceptions.ConnectTimeout as erro:
        raise ConnectionError(
            "O tempo para estabelecer conexão com a API foi excedido."
        ) from erro

    except requests.exceptions.ReadTimeout as erro:
        raise ConnectionError(
            "A API demorou mais que o esperado para responder."
        ) from erro

    except requests.exceptions.ConnectionError as erro:
        raise ConnectionError(
            "Não foi possível conectar à API. Verifique a internet, "
            "a VPN, o proxy ou o firewall."
        ) from erro

    except requests.exceptions.RequestException as erro:
        raise ConnectionError(
            f"Falha ao realizar a consulta: {erro}"
        ) from erro

    if resposta.status_code == 200:
        try:
            return resposta.json()

        except requests.exceptions.JSONDecodeError as erro:
            raise ValueError(
                "A API respondeu, mas o conteúdo retornado "
                "não é um JSON válido."
            ) from erro

    if resposta.status_code == 400:
        raise ValueError(
            "A API recusou a consulta porque o CNPJ está "
            "em formato inválido."
        )

    if resposta.status_code == 404:
        raise ValueError(
            "O CNPJ não foi encontrado na base consultada."
        )

    if resposta.status_code == 429:
        raise ValueError(
            "O limite de consultas da API foi atingido. "
            "Aguarde um minuto antes de tentar novamente."
        )

    if resposta.status_code >= 500:
        raise ConnectionError(
            "A API está temporariamente indisponível. "
            f"Código HTTP: {resposta.status_code}."
        )

    raise ValueError(
        "Não foi possível concluir a consulta. "
        f"Código HTTP retornado: {resposta.status_code}."
    )


# ============================================================
# EXPORTAÇÃO PARA EXCEL
# ============================================================

def gerar_excel(dados, cnpj_pesquisado):
    """
    Gera um arquivo Excel em memória com os dados consultados.
    """

    empresa = dados.get("company") or {}
    status = dados.get("status") or {}
    natureza = empresa.get("nature") or {}
    porte = empresa.get("size") or {}
    endereco = dados.get("address") or {}
    atividade_principal = dados.get("mainActivity") or {}
    simples = dados.get("simples") or {}

    dados_gerais = {
        "Campo": [
            "CNPJ",
            "Razão social",
            "Nome fantasia",
            "Situação cadastral",
            "Data da situação",
            "Data de abertura",
            "Natureza jurídica",
            "Porte",
            "Capital social",
            "CNAE principal",
            "Descrição do CNAE principal",
            "Logradouro",
            "Número",
            "Complemento",
            "Bairro",
            "Município",
            "UF",
            "CEP",
            "Endereço completo",
            "Optante pelo Simples",
            "Optante pelo MEI",
        ],
        "Valor": [
            formatar_cnpj(
                dados.get("taxId") or cnpj_pesquisado
            ),
            valor_seguro(empresa.get("name")),
            valor_seguro(dados.get("alias")),
            valor_seguro(status.get("text")),
            formatar_data(dados.get("statusDate")),
            formatar_data(dados.get("founded")),
            valor_seguro(natureza.get("text")),
            valor_seguro(porte.get("text")),
            formatar_moeda(empresa.get("equity")),
            valor_seguro(atividade_principal.get("id")),
            valor_seguro(atividade_principal.get("text")),
            valor_seguro(endereco.get("street")),
            valor_seguro(endereco.get("number")),
            valor_seguro(endereco.get("details")),
            valor_seguro(endereco.get("district")),
            valor_seguro(endereco.get("city")),
            valor_seguro(endereco.get("state")),
            valor_seguro(endereco.get("zip")),
            valor_seguro(montar_endereco(dados)),
            formatar_sim_nao(simples.get("optant")),
            formatar_sim_nao(simples.get("mei")),
        ],
    }

    dataframe_geral = pd.DataFrame(dados_gerais)

    atividades_secundarias = dados.get("sideActivities") or []

    dataframe_atividades = pd.DataFrame(
        [
            {
                "Código": atividade.get("id", ""),
                "Descrição": atividade.get("text", ""),
            }
            for atividade in atividades_secundarias
        ]
    )

    telefones = dados.get("phones") or []

    dataframe_telefones = pd.DataFrame(
        [
            {
                "Tipo": telefone.get("type", ""),
                "DDD": telefone.get("area", ""),
                "Número": telefone.get("number", ""),
            }
            for telefone in telefones
        ]
    )

    emails = dados.get("emails") or []

    dataframe_emails = pd.DataFrame(
        [
            {
                "E-mail": email.get("address", ""),
                "Domínio": email.get("domain", ""),
            }
            for email in emails
        ]
    )

    socios = empresa.get("members") or []

    dataframe_socios = pd.DataFrame(
        [
            {
                "Nome": (
                    socio.get("person") or {}
                ).get("name", ""),
                "Qualificação": (
                    socio.get("role") or {}
                ).get("text", ""),
                "Data de entrada": formatar_data(
                    socio.get("since")
                ),
            }
            for socio in socios
        ]
    )

    arquivo_excel = io.BytesIO()

    with pd.ExcelWriter(
        arquivo_excel,
        engine="openpyxl",
    ) as escritor:

        dataframe_geral.to_excel(
            escritor,
            sheet_name="Dados Gerais",
            index=False,
        )

        if not dataframe_atividades.empty:
            dataframe_atividades.to_excel(
                escritor,
                sheet_name="CNAEs Secundários",
                index=False,
            )

        if not dataframe_telefones.empty:
            dataframe_telefones.to_excel(
                escritor,
                sheet_name="Telefones",
                index=False,
            )

        if not dataframe_emails.empty:
            dataframe_emails.to_excel(
                escritor,
                sheet_name="Emails",
                index=False,
            )

        if not dataframe_socios.empty:
            dataframe_socios.to_excel(
                escritor,
                sheet_name="Sócios",
                index=False,
            )

        # Ajuste simples da largura das colunas.
        for planilha in escritor.book.worksheets:
            for coluna in planilha.columns:
                maior_tamanho = 0
                letra_coluna = coluna[0].column_letter

                for celula in coluna:
                    valor = celula.value

                    if valor is not None:
                        maior_tamanho = max(
                            maior_tamanho,
                            len(str(valor)),
                        )

                planilha.column_dimensions[
                    letra_coluna
                ].width = min(maior_tamanho + 3, 60)

            planilha.freeze_panes = "A2"

    arquivo_excel.seek(0)

    return arquivo_excel.getvalue()


# ============================================================
# ESTILO DA INTERFACE
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border: 1px solid #e6e9ef;
            border-radius: 10px;
            padding: 14px;
        }

        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🏢 Consulta de CNPJ")

st.caption(
    "Consulta de dados cadastrais utilizando a API pública da CNPJá."
)


# ============================================================
# FORMULÁRIO
# ============================================================

with st.form("formulario_consulta"):
    cnpj_digitado = st.text_input(
        "Digite o CNPJ",
        placeholder="00.000.000/0000-00",
        max_chars=18,
        help="O CNPJ pode ser informado com ou sem pontuação.",
    )

    consultar = st.form_submit_button(
        "Consultar CNPJ",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# CONSULTA E APRESENTAÇÃO DO RESULTADO
# ============================================================

if consultar:

    if not cnpj_digitado.strip():
        st.warning(
            "Informe um CNPJ para realizar a consulta."
        )
        st.stop()

    try:
        with st.spinner("Consultando o CNPJ..."):
            dados = consultar_cnpj(cnpj_digitado)

    except ValueError as erro:
        st.error(str(erro))
        st.stop()

    except ConnectionError as erro:
        st.error(str(erro))

        st.info(
            "A validação de segurança HTTPS continua habilitada. "
            "Não altere o código para utilizar verify=False."
        )

        st.stop()

    except Exception as erro:
        st.error(
            "Ocorreu um erro inesperado durante a consulta."
        )

        with st.expander("Detalhes técnicos do erro"):
            st.code(str(erro))

        st.stop()

    st.success("Consulta realizada com sucesso.")

    empresa = dados.get("company") or {}
    situacao = dados.get("status") or {}
    natureza = empresa.get("nature") or {}
    porte = empresa.get("size") or {}

    cnpj_resultado = (
        dados.get("taxId")
        or limpar_cnpj(cnpj_digitado)
    )

    # --------------------------------------------------------
    # INDICADORES PRINCIPAIS
    # --------------------------------------------------------

    coluna1, coluna2, coluna3 = st.columns(3)

    with coluna1:
        st.metric(
            "CNPJ",
            formatar_cnpj(cnpj_resultado),
        )

    with coluna2:
        st.metric(
            "Situação cadastral",
            valor_seguro(situacao.get("text")),
        )

    with coluna3:
        st.metric(
            "Data de abertura",
            formatar_data(dados.get("founded")),
        )

    st.divider()

    # --------------------------------------------------------
    # DADOS DA EMPRESA
    # --------------------------------------------------------

    coluna_empresa, coluna_cadastro = st.columns(2)

    with coluna_empresa:
        st.subheader("Dados da empresa")

        st.write(
            "**Razão social:**",
            valor_seguro(empresa.get("name")),
        )

        st.write(
            "**Nome fantasia:**",
            valor_seguro(dados.get("alias")),
        )

        st.write(
            "**Natureza jurídica:**",
            valor_seguro(natureza.get("text")),
        )

        st.write(
            "**Porte:**",
            valor_seguro(porte.get("text")),
        )

        st.write(
            "**Capital social:**",
            formatar_moeda(empresa.get("equity")),
        )

    with coluna_cadastro:
        st.subheader("Situação cadastral")

        st.write(
            "**Situação:**",
            valor_seguro(situacao.get("text")),
        )

        st.write(
            "**Data da situação:**",
            formatar_data(dados.get("statusDate")),
        )

        motivo = dados.get("reason") or {}

        st.write(
            "**Motivo da situação:**",
            valor_seguro(motivo.get("text")),
        )

        st.write(
            "**Tipo da unidade:**",
            valor_seguro(dados.get("type")),
        )

    st.divider()

    # --------------------------------------------------------
    # ENDEREÇO
    # --------------------------------------------------------

    st.subheader("Endereço")

    endereco = dados.get("address") or {}

    endereco_coluna1, endereco_coluna2 = st.columns(2)

    with endereco_coluna1:
        st.write(
            "**Logradouro:**",
            valor_seguro(endereco.get("street")),
        )

        st.write(
            "**Número:**",
            valor_seguro(endereco.get("number")),
        )

        st.write(
            "**Complemento:**",
            valor_seguro(endereco.get("details")),
        )

        st.write(
            "**Bairro:**",
            valor_seguro(endereco.get("district")),
        )

    with endereco_coluna2:
        st.write(
            "**Município:**",
            valor_seguro(endereco.get("city")),
        )

        st.write(
            "**UF:**",
            valor_seguro(endereco.get("state")),
        )

        st.write(
            "**CEP:**",
            valor_seguro(endereco.get("zip")),
        )

        st.write(
            "**País:**",
            valor_seguro(endereco.get("country")),
        )

    st.write(
        "**Endereço completo:**",
        valor_seguro(montar_endereco(dados)),
    )

    st.divider()

    # --------------------------------------------------------
    # CNAE PRINCIPAL
    # --------------------------------------------------------

    atividade_principal = dados.get("mainActivity") or {}

    if atividade_principal:
        st.subheader("CNAE principal")

        cnae_coluna1, cnae_coluna2 = st.columns(
            [1, 3]
        )

        with cnae_coluna1:
            st.write(
                "**Código:**",
                valor_seguro(
                    atividade_principal.get("id")
                ),
            )

        with cnae_coluna2:
            st.write(
                "**Descrição:**",
                valor_seguro(
                    atividade_principal.get("text")
                ),
            )

    # --------------------------------------------------------
    # CNAES SECUNDÁRIOS
    # --------------------------------------------------------

    atividades_secundarias = (
        dados.get("sideActivities") or []
    )

    if atividades_secundarias:
        st.subheader("CNAEs secundários")

        dataframe_atividades = pd.DataFrame(
            [
                {
                    "Código": atividade.get("id", ""),
                    "Descrição": atividade.get("text", ""),
                }
                for atividade in atividades_secundarias
            ]
        )

        st.dataframe(
            dataframe_atividades,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # TELEFONES
    # --------------------------------------------------------

    telefones = dados.get("phones") or []

    if telefones:
        st.subheader("Telefones")

        dataframe_telefones = pd.DataFrame(
            [
                {
                    "Tipo": telefone.get("type", ""),
                    "DDD": telefone.get("area", ""),
                    "Número": telefone.get("number", ""),
                }
                for telefone in telefones
            ]
        )

        st.dataframe(
            dataframe_telefones,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # E-MAILS
    # --------------------------------------------------------

    emails = dados.get("emails") or []

    if emails:
        st.subheader("E-mails")

        dataframe_emails = pd.DataFrame(
            [
                {
                    "E-mail": email.get("address", ""),
                    "Domínio": email.get("domain", ""),
                }
                for email in emails
            ]
        )

        st.dataframe(
            dataframe_emails,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # QUADRO SOCIETÁRIO
    # --------------------------------------------------------

    socios = empresa.get("members") or []

    if socios:
        st.subheader("Quadro societário")

        dataframe_socios = pd.DataFrame(
            [
                {
                    "Nome": (
                        socio.get("person") or {}
                    ).get("name", ""),
                    "Qualificação": (
                        socio.get("role") or {}
                    ).get("text", ""),
                    "Data de entrada": formatar_data(
                        socio.get("since")
                    ),
                }
                for socio in socios
            ]
        )

        st.dataframe(
            dataframe_socios,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # SIMPLES NACIONAL
    # --------------------------------------------------------

    simples = dados.get("simples") or {}

    if simples:
        st.subheader("Simples Nacional")

        simples_coluna1, simples_coluna2 = st.columns(2)

        with simples_coluna1:
            st.write(
                "**Optante pelo Simples:**",
                formatar_sim_nao(
                    simples.get("optant")
                ),
            )

            st.write(
                "**Data de opção pelo Simples:**",
                formatar_data(simples.get("since")),
            )

        with simples_coluna2:
            st.write(
                "**Optante pelo MEI:**",
                formatar_sim_nao(simples.get("mei")),
            )

    st.divider()

    # --------------------------------------------------------
    # EXPORTAÇÃO
    # --------------------------------------------------------

    st.subheader("Exportação")

    try:
        arquivo_excel = gerar_excel(
            dados,
            cnpj_resultado,
        )

        nome_arquivo = (
            f"consulta_cnpj_"
            f"{limpar_cnpj(cnpj_resultado)}.xlsx"
        )

        st.download_button(
            label="📥 Baixar resultado em Excel",
            data=arquivo_excel,
            file_name=nome_arquivo,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

    except Exception as erro:
        st.warning(
            "A consulta foi concluída, mas não foi possível "
            "preparar o arquivo Excel."
        )

        with st.expander("Detalhes do erro de exportação"):
            st.code(str(erro))

    # --------------------------------------------------------
    # JSON COMPLETO
    # --------------------------------------------------------

    with st.expander("Visualizar resposta JSON completa"):
        st.json(dados)