import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

modelos = ['roe_mom_excelente', 'value_mom_long', 'all_factors_long', 'bdr']

modelo_selecionado = st.selectbox("Selecione um modelo:", modelos)

df = pd.read_excel(st.secrets['xlsx'], sheet_name=modelo_selecionado)

st.dataframe(df, height=500)


# botoes laterais
with st.sidebar:
    st.header("⚙️ Ações")
    botao_dicionario = st.button("Mostrar Dicionário")
    botao_grafico = st.button("Mostrar Gráfico Retorno")
    botao_tabela = st.button("Mostrar Tabela Retorno")

# dicionario colunas
if botao_dicionario:
    dicionario_colunas = {
    
    'current_ev_to_t12m_ebitda': 'Relação entre o valor da firma (Enterprise Value) e o EBITDA dos últimos 12 meses. Mede quanto o mercado está pagando pelo lucro operacional da empresa, ajustado por depreciação e amortização.',
    
    'pe_ratio': 'Relação Preço/Lucro (Price to Earnings). Mede quantas vezes o lucro anual a empresa está sendo negociada no mercado. Quanto menor, teoricamente mais barata está a ação em relação ao seu lucro.',
    
    'px_to_book_ratio': 'Relação Preço/Valor Patrimonial (Price to Book). Compara o preço de mercado da ação com o valor contábil do patrimônio líquido por ação. Indica se a ação está sendo negociada acima ou abaixo do seu valor contábil.',
    
    'px_to_sales_ratio': 'Relação Preço/Vendas (Price to Sales). Compara o valor de mercado da empresa com sua receita anual. Útil para empresas com lucros instáveis ou negativos.',
    
    'eqy_dvd_yld_12m_net': 'Yield de Dividendos (últimos 12 meses, líquido). Indica o retorno percentual pago ao acionista em forma de dividendos nos últimos 12 meses, já descontados impostos.',
    
    'tot_debt_to_tot_eqy': 'Relação Dívida Total / Patrimônio Líquido. Mede o grau de alavancagem financeira da empresa. Quanto maior, mais dependente de capital de terceiros.',
    
    'net_debt_to_ebitda': 'Relação Dívida Líquida / EBITDA. Mede quantos anos seriam necessários para pagar a dívida líquida da empresa usando seu EBITDA atual. Indicador de solvência.',
    
    'sales_growth': 'Crescimento das vendas. Indica a variação percentual da receita da empresa em determinado período (ano).'

}
    #st.write(df.columns)
    for coluna, descricao in dicionario_colunas.items():
        st.markdown(f"**🟢{coluna}**🟢: {descricao}")
    #st.success("Botão do lado esquerdo clicado!")


# yfinance preço

df['Ticker_Clean'] = df['Ticker'].str.split().str[0] + '.SA'
tickers = df['Ticker_Clean'].tolist()

end_date = datetime.today()
start_date = end_date - timedelta(days=252)

# Baixar os preços
data = yf.download(tickers, start=start_date, end=end_date)['Close']

# Calcular retorno acumulado
retornos = (data / data.iloc[0]) - 1

if botao_tabela:
    ret_diario = data.pct_change()

    # Criando o novo DataFrame
    retornos_periodos = pd.DataFrame(index=['5d', '21d', '63d', '126d', '252d'], columns=ret_diario.columns)

    # Preenchendo os valores
    retornos_periodos.loc['5d']   = ((1 + ret_diario).tail(5).prod() - 1) *100
    retornos_periodos.loc['21d']   = ((1 + ret_diario).tail(21).prod() - 1) *100
    retornos_periodos.loc['63d']   = ((1 + ret_diario).tail(63).prod() - 1) *100
    retornos_periodos.loc['126d']  = ((1 + ret_diario).tail(126).prod() - 1) *100
    retornos_periodos.loc['252d']  = ((1 + ret_diario).tail(252).prod() - 1) *100

    st.dataframe(retornos_periodos)



# botao grafico
if botao_grafico:
    fig = go.Figure()
    for ticker in retornos.columns:
        fig.add_trace(go.Scatter(x=retornos.index, y=retornos[ticker], name=ticker))

    fig.update_layout(
        title="Retorno Acumulado (252 dias)",
        xaxis_title="Data",
        yaxis_title="Retorno (%)",
        yaxis_tickformat=".1%",
        template="plotly_white"
    )

    st.plotly_chart(fig)




