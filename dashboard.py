import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise de Estoque",
    layout="centered"
)

st.title("Dashboard de Análise de Estoque")
st.markdown("### Processamento Rápido de Arquivos CSV/Excel")

# --- 1. Função de Upload ---
uploaded_file = st.file_uploader(
    "1. Selecione um arquivo (.csv ou .xlsx)",
    type=['csv', 'xlsx']
)

# Variável para armazenar o DataFrame processado
df_processado = None 
mostrar_download = False

# --- 2. Lógica de Processamento (roda se o arquivo for carregado) ---
if uploaded_file is not None:
    # 2.1. Leitura do Arquivo
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("Arquivo carregado com sucesso! Iniciando processamento...")

        # 2.2. Operações de Negócio (Baseado no exercício de Lucro de Lojas)
        
        # Verificar se as colunas necessárias existem
        if 'Quantidade_Estoque' in df.columns and 'Preco_Unitario' in df.columns and 'Categoria' in df.columns:
            
            # 1. Criar a coluna com o valor total em estoque
            df['Valor_Total_Estoque'] = df['Quantidade_Estoque'] * df['Preco_Unitario']
            
            # 2. Calcular o valor total do estoque por categoria
            df_resumo_loja = df.groupby('Categoria', as_index=False)['Valor_Total_Estoque'].sum()
            
            # 3. Arredondar os valores
            df_resumo_loja['Valor_Total_Estoque'] = df_resumo_loja['Valor_Total_Estoque'].round(2)
            
            # 4. Exibir na tela
            st.header("2. Resultados do Processamento (Valor Total em Estoque por Categoria)")
            st.dataframe(df_resumo_loja, width="stretch")

            
            # 5. Preparar para download
            df_processado = df_resumo_loja
            mostrar_download = True

        else:
            st.error("Erro: O arquivo deve conter as colunas 'Categoria', 'Quantidade_Estoque' e 'Preco_Unitario' para o processamento.")

    except Exception as e:
        st.error(f"Ocorreu um erro na leitura/processamento do arquivo: {e}")


# --- 3. Botão de Download (só aparece após o processamento) ---

if mostrar_download and df_processado is not None:
    
    st.header("3. Gráfico de Barras Representativo")
    
    eixo_x = df_processado['Categoria']
    eixo_y = df_processado['Valor_Total_Estoque']
 
    figura, eixos = plt.subplots(figsize=(10, 6))
    
    eixos.bar(eixo_x, eixo_y, color='green')
    
    eixos.set_xlabel('Categoria', fontsize=12)
    eixos.set_ylabel('Valor_Total_Estoque', fontsize=12)
    eixos.grid(axis='y', linestyle='--', alpha=1)
    
    for i in range(len(eixo_x)):
        eixos.text(eixo_x[i], eixo_y[i] + 5, str(eixo_y[i]), ha='center', va='bottom', fontweight='bold')

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(figura)
    
    st.header("4. Exportar Resultados")
    
    # Criar o arquivo Excel em memória (usando io.BytesIO)
    buffer = io.BytesIO()
    
    # Exportar o DataFrame Processado para o buffer como Excel
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_processado.to_excel(writer, sheet_name='Venda_Total_Estoque', index=False)
        
    buffer.seek(0)
    
    # O comando st.download_button cria o botão de download
    st.download_button(
        label="Baixar Relatório em Excel",
        data=buffer,
        file_name='Relatorio_Venda_Total_Estoque.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        help="Clique para baixar o resumo da Venda Total do Estoque."
    )
    
    st.success("Processamento concluído. O botão de download está pronto!")
