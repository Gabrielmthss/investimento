import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurações iniciais
st.title('Dashboard de Investimento')

# Estados iniciais na sidebar
with st.sidebar:
    invested_amount = st.number_input('Valor Investido (R$):', min_value=0, value=1000000, step=10000, format="%d")
    st.write(f'Valor Investido (R$): {invested_amount:,.2f} reais')
    st.sidebar.markdown('---')
    include_pro_labore = st.checkbox('Incluir Pró-labore?', value=False)
    if include_pro_labore:
        pro_labore = st.slider('Pró-labore (R$):', min_value=0, max_value=20000, step=500, value=12000, format="%d")
        st.write(f'Pró-labore (R$): {pro_labore:,.2f} reais')
    else:
        pro_labore = 0

    monthly_profit = st.slider('Lucro Mensal (R$):', min_value=0, max_value=1000000, step=50000, value=400000, format="%d")
    st.write(f'Lucro Mensal (R$): {monthly_profit:,.2f} reais')
    ownership_percentage = st.slider('Percentual de Participação:', min_value=0, max_value=100, step=5, value=5, format="%d%%")
    st.write(f'Percentual de Participação: {ownership_percentage:}%')
    st.sidebar.markdown('---')
    simulation_years = st.slider('Anos de Simulação:', min_value=1, max_value=10, step=1, value=10, format="%d")

# Cálculos
profit_withdrawal = monthly_profit * (ownership_percentage / 100)
total_monthly_withdrawal = profit_withdrawal + (pro_labore if include_pro_labore else 0)

# Adicionar retirada mensal do lucro e retirada mensal total na sidebar com uma linha de separação
with st.sidebar:
    st.sidebar.markdown('---')
    st.markdown(f"**Retirada Mensal do LUCRO (R$): {profit_withdrawal:,.2f} reais**")
    st.markdown(f"**Retirada Mensal TOTAL (R$): {total_monthly_withdrawal:,.2f} reais**")

# Calcular dados mensais e anuais
accumulated_profit = 0
accumulated_pro_labore = 0
break_even_month_year = None

for year in range(simulation_years):
    for month in range(12):
        accumulated_profit += profit_withdrawal
        accumulated_pro_labore += pro_labore if include_pro_labore else 0
        accumulated_total = accumulated_profit + accumulated_pro_labore
        if accumulated_total >= invested_amount and break_even_month_year is None:
            break_even_month_year = (year, month + 1)
            break
    if break_even_month_year is not None:
        break

# Exibir ponto de equilíbrio
if break_even_month_year is not None:
    total_months = (break_even_month_year[0]) * 12 + break_even_month_year[1]
    years = total_months // 12
    months = total_months % 12
    st.sidebar.markdown('---')
    st.sidebar.markdown(f"**Para atingir o ponto de equilíbrio é {years} anos e {months} meses**")
else:
    st.sidebar.markdown('---')
    st.sidebar.markdown(f"**Para atingir o ponto de equilíbrio é {simulation_years} anos e {simulation_years * 12} meses**")

# Calcular dados para exibição (mensais e anuais)
monthly_data = []
yearly_data = []
accumulated_profit = 0
accumulated_pro_labore = 0

for year in range(simulation_years):
    yearly_accumulated_profit = 0
    yearly_accumulated_pro_labore = 0
    for month in range(12):
        accumulated_profit += profit_withdrawal
        accumulated_pro_labore += pro_labore if include_pro_labore else 0
        yearly_accumulated_profit += profit_withdrawal
        yearly_accumulated_pro_labore += pro_labore if include_pro_labore else 0
        monthly_data.append({
            'Ano': f'{year} ano',
            'Mês': f'{month + 1} mês',
            'Acumulado Lucro (R$)': accumulated_profit,
            'Acumulado Pró-labore (R$)': accumulated_pro_labore,
            'Acumulado Total (R$)': accumulated_profit + accumulated_pro_labore
        })
    yearly_data.append({
        'Ano': f'{year + 1} ano',  # Ajustar aqui para que o ano zero seja ano 1
        'Acumulado Lucro (R$)': accumulated_profit,
        'Acumulado Pró-labore (R$)': accumulated_pro_labore,
        'Acumulado Total (R$)': accumulated_profit + accumulated_pro_labore
    })

monthly_df = pd.DataFrame(monthly_data)
yearly_df = pd.DataFrame(yearly_data)

# Filtrar dados para exibição
monthly_df_first_year = monthly_df[monthly_df['Ano'] == '0 ano'].copy()
yearly_df_filtered = yearly_df.copy()

# Função para destacar a linha do ponto de equilíbrio
def highlight_break_even(row):
    if break_even_month_year is not None:
        break_even_year = break_even_month_year[0]
        break_even_month = break_even_month_year[1]
        if row['Ano'] == f'{break_even_year} ano' and row['Mês'] == f'{break_even_month} mês':
            return ['background-color: yellow']*len(row)
    return ['']*len(row)

# Exibir tabelas
st.subheader('Detalhamento Mensal (12 meses)')
st.dataframe(monthly_df.style.apply(highlight_break_even, axis=1).format({
    'Acumulado Lucro (R$)': "{:,.2f} reais",
    'Acumulado Pró-labore (R$)': "{:,.2f} reais",
    'Acumulado Total (R$)': "{:,.2f} reais"
}))

st.subheader('Detalhamento Anual')
st.dataframe(yearly_df_filtered.style.format({
    'Acumulado Lucro (R$)': "{:,.2f} reais",
    'Acumulado Pró-labore (R$)': "{:,.2f} reais",
    'Acumulado Total (R$)': "{:,.2f} reais"
}))

# Gráficos interativos
st.subheader('Acúmulo Mensal (12 meses)')
fig_monthly = go.Figure()
fig_monthly.add_trace(go.Scatter(x=monthly_df_first_year['Mês'], y=monthly_df_first_year['Acumulado Lucro (R$)'],
                                 mode='lines+markers', name='Acumulado Lucro (R$)'))
fig_monthly.add_trace(go.Scatter(x=monthly_df_first_year['Mês'], y=monthly_df_first_year['Acumulado Pró-labore (R$)'],
                                 mode='lines+markers', name='Acumulado Pró-labore (R$)'))
fig_monthly.add_trace(go.Scatter(x=monthly_df_first_year['Mês'], y=monthly_df_first_year['Acumulado Total (R$)'],
                                 mode='lines+markers', name='Acumulado Total (R$)'))
fig_monthly.update_layout(title='Acúmulo Mensal (12 meses)',
                          xaxis_title='Mês',
                          yaxis_title='Valor (R$)')
st.plotly_chart(fig_monthly)

st.subheader('Acúmulo Anual')
fig_yearly = go.Figure()
fig_yearly.add_trace(go.Scatter(x=yearly_df_filtered['Ano'], y=yearly_df_filtered['Acumulado Lucro (R$)'],
                                mode='lines+markers', name='Acumulado Lucro (R$)'))
fig_yearly.add_trace(go.Scatter(x=yearly_df_filtered['Ano'], y=yearly_df_filtered['Acumulado Pró-labore (R$)'],
                                mode='lines+markers', name='Acumulado Pró-labore (R$)'))
fig_yearly.add_trace(go.Scatter(x=yearly_df_filtered['Ano'], y=yearly_df_filtered['Acumulado Total (R$)'],
                                mode='lines+markers', name='Acumulado Total (R$)'))
fig_yearly.update_layout(title='Acúmulo Anual',
                         xaxis_title='Ano',
                         yaxis_title='Valor (R$)')
st.plotly_chart(fig_yearly)
