from nbformat import write
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pandas_datareader as pdr


#Carregando dataframe
df_proventos = pd.read_csv('data/df_proventos.csv')
df_posicao_acao = pd.read_csv('data/df_posicao_acao.csv')
df_posicao_fii = pd.read_csv('data/df_posicao_fii.csv')
df_negociacao = pd.read_csv('data/df_negociacao.csv')
df_fii_dadoHistorico = pd.read_csv('data/df_fii_dadoHistorico.csv')
df_acao_dadoHistorico = pd.read_csv('data/df_acao_dadoHistorico.csv')
df_fii_dadoHistorico_desempenho = pd.read_csv('data/df_fii_dadoHistorico_desempenho.csv')
df_acao_dadoHistorico_desempenho = pd.read_csv('data/df_acao_dadoHistorico_desempenho.csv')

def atualizar_dados():
    
    #Carregando dataframe
    df_proventos = pd.read_excel('data/proventos-recebidos.xlsx')
    df_posicao_acao = pd.read_excel('data/posicao.xlsx',sheet_name='Acoes')
    df_posicao_fii = pd.read_excel('data/posicao.xlsx',sheet_name='Fundo de Investimento')
    df_posicao_fii.dropna(inplace=True)
    df_posicao_acao.dropna(inplace=True)
    df_negociacao = pd.read_excel('data/negociacao.xlsx')

    #Transformar as datas para apenas para mes/ano
    for i in range(len(df_proventos['Pagamento'])):
        df_proventos['Pagamento'].iloc[i]= df_proventos['Pagamento'].iloc[i][3:] 
        
    
    #pegar dados de df_negociacao para criar em posicao valor total investido
    ativosjanegociados=[]
    [ativosjanegociados.append(i) for i in df_negociacao['Código de Negociação'] if not i in ativosjanegociados]
    totalInvestido=[]
    for i in ativosjanegociados:
        compra = df_negociacao[(df_negociacao['Código de Negociação'] == i)&
        (df_negociacao['Tipo de Movimentação']=='Compra')

        ]['Valor']

        venda = df_negociacao[(df_negociacao['Código de Negociação'] == i)&
        (df_negociacao['Tipo de Movimentação']=='Venda')

        ]['Valor']
        
        if compra.sum() > venda.sum():
            totalInvestido.append([i.removesuffix('F'),round(compra.sum()-venda.sum(),2)])
        else:
            totalInvestido.append([i.removesuffix('F'),round(venda.sum() - compra.sum(),2)])

    df_posicao_acao['Valor total investido'] = df_posicao_acao['Motivo']
    for j in range(len(df_posicao_acao['Código de Negociação'])):
        for i in range(len(totalInvestido)):
            if df_posicao_acao['Código de Negociação'].iloc[j] == totalInvestido[i][0]:
                df_posicao_acao['Valor total investido'].iloc[j] = totalInvestido[i][1]
                
    df_posicao_fii['Valor total investido'] = df_posicao_fii['Motivo'] 
    for j in range(len(df_posicao_fii['Código de Negociação'])):
        for i in range(len(totalInvestido)):
            if df_posicao_fii['Código de Negociação'].iloc[j] == totalInvestido[i][0]:
                df_posicao_fii['Valor total investido'].iloc[j] = totalInvestido[i][1]
                
    
    #dados historicos
    df_fii_dadoHistorico = pdr.get_data_yahoo(df_posicao_fii['Código de Negociação']+'.SA',start="2022-01-01")['Close']
    df_acao_dadoHistorico = pdr.get_data_yahoo(df_posicao_acao['Código de Negociação']+'.SA',start="2022-01-01")['Close']
        
    #Atualizar dados atuais a partir do DFdadohistorico  
    for i in range(len(df_posicao_fii['Código de Negociação'])):
            for j in  range(len(df_fii_dadoHistorico.columns)):                
                if df_posicao_fii['Código de Negociação'].iloc[i] == df_fii_dadoHistorico.columns[j][:-3]:                  
                    df_posicao_fii['Valor Atualizado'][i] =  round(df_fii_dadoHistorico[df_fii_dadoHistorico.columns[j]][-1],2)                   
    df_posicao_fii = df_posicao_fii.rename(columns = {"Valor Atualizado":"Cotacao Atual"})

    for i in range(len(df_posicao_acao['Código de Negociação'])):
        for j in  range(len(df_acao_dadoHistorico.columns)):                
            if df_posicao_acao['Código de Negociação'].iloc[i] == df_acao_dadoHistorico.columns[j][:-3]:                  
                df_posicao_acao['Valor Atualizado'][i] =  round(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[j]][-1],2)  
    df_posicao_acao = df_posicao_acao.rename(columns = {"Valor Atualizado":"Cotacao Atual"})
    
        
    #Cria valor total atual   
    df_posicao_fii['Valor total atual'] = df_posicao_fii['Cotacao Atual'] * df_posicao_fii['Quantidade']
    df_posicao_acao['Valor total atual'] = df_posicao_acao['Cotacao Atual'] * df_posicao_acao['Quantidade']
    
    #Criar preço medio
    df_posicao_acao['Preco medio'] = df_posicao_acao['Valor total investido'] / df_posicao_acao['Quantidade'] 
    df_posicao_fii['Preco medio'] = df_posicao_fii['Valor total investido'] /df_posicao_fii['Quantidade']
    
    #Rentabilidade
    df_posicao_acao['rentabilidade'] = ((df_posicao_acao['Valor total atual'] / df_posicao_acao['Valor total investido'] )-1)*100
    df_posicao_fii['rentabilidade'] = ((df_posicao_fii['Valor total atual'] /df_posicao_fii['Valor total investido'] )-1)*100
    
    
    #Grafico de desempenho no tempo da carteira
    df_acao_dadoHistorico_desempenho = df_acao_dadoHistorico.copy()
    df_fii_dadoHistorico_desempenho = df_fii_dadoHistorico.copy()
    
    for i in range(0,len(df_acao_dadoHistorico_desempenho.columns)):
        df_acao_dadoHistorico_desempenho[df_acao_dadoHistorico_desempenho.columns[i]] = df_acao_dadoHistorico_desempenho[df_acao_dadoHistorico_desempenho.columns[i]]/df_acao_dadoHistorico_desempenho[df_acao_dadoHistorico_desempenho.columns[i]].iloc[0]
    
    for i in range(0,len(df_fii_dadoHistorico_desempenho.columns)):
        df_fii_dadoHistorico_desempenho[df_fii_dadoHistorico_desempenho.columns[i]] = df_fii_dadoHistorico_desempenho[df_fii_dadoHistorico_desempenho.columns[i]]/df_fii_dadoHistorico_desempenho[df_fii_dadoHistorico_desempenho.columns[i]].iloc[0]
    
    
    #Transforma em CSV

    
    
    df_proventos.to_csv("data/df_proventos.csv")
    df_posicao_acao.to_csv("data/df_posicao_acao.csv")
    df_posicao_fii.to_csv("data/df_posicao_fii.csv")
    df_negociacao.to_csv("data/df_negociacao.csv")  
    df_fii_dadoHistorico.to_csv("data/df_fii_dadoHistorico.csv")
    df_acao_dadoHistorico.to_csv("data/df_acao_dadoHistorico.csv")
    df_fii_dadoHistorico_desempenho = pd.read_csv('data/df_fii_dadoHistorico_desempenho.csv')
    df_acao_dadoHistorico_desempenho = pd.read_csv('data/df_acao_dadoHistorico_desempenho.csv')
    

    writer = pd.ExcelWriter(r'data/bd.xlsx', engine='xlsxwriter')
    
    df_proventos.to_excel(writer,sheet_name='proventos')
    df_posicao_acao.to_excel(writer,sheet_name='posicao_acao')
    df_posicao_fii.to_excel(writer,sheet_name='posicao_fii')
    df_negociacao.to_excel(writer,sheet_name='negociacao')
    df_fii_dadoHistorico.to_excel(writer,sheet_name='fii_dadoHistorico')
    df_acao_dadoHistorico.to_excel(writer,sheet_name='acao_dadoHistorico')
    df_fii_dadoHistorico_desempenho.to_excel(writer,sheet_name='fii_dadoHistorico_desempenho')
    df_acao_dadoHistorico_desempenho.to_excel(writer,sheet_name='acao_dadoHistorico_desempenho')

    writer.save()

#Variaveis Nu_Bank
nubank_aplicado = 8402.01
nubank_provento = 55.87

#Variaveis usadas
compra = round(df_negociacao[df_negociacao['Tipo de Movimentação']=='Compra']['Valor'].sum(),2)
venda = round(df_negociacao[df_negociacao['Tipo de Movimentação']=='Venda']['Valor'].sum(),2)
valor_aplicado = round((compra-venda) + nubank_aplicado,2)

totalProventos = round(df_proventos['Valor líquido'].sum(),2)+nubank_provento

pl = round(df_posicao_fii['Valor total atual'].sum() + df_posicao_acao['Valor total atual'].sum() + nubank_aplicado + totalProventos,2)

rentabilidade = round(pl - valor_aplicado,2)
rentabilidade_relativa = rentabilidade/pl



#Configuracao da pagina 
st.set_page_config(
     page_title="Doutor Porco App",
     page_icon="🐷",
     layout="wide",
     initial_sidebar_state ="expanded",
 )

#Carregar CSS
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>',unsafe_allow_html=True)
    
#SideBar
with st.container():
    with st.sidebar:

        st.header('Patrimônio Atual')
        st.success(round(pl,2),icon="💲")
        st.header('Valor aplicado')
        st.success(valor_aplicado,icon="💲")
        st.header('Rentabilidade real')
        st.success(rentabilidade,icon="💲")
        st.header('Rentabilidade relativa')
        st.success(str(round((rentabilidade*100)/pl,2))+"%",icon="💲")
        st.header('Total de proventos ')
        st.success(round(totalProventos,2),icon="💲")
        


with st.container():
    
    tab = st.tabs(["📄 Tabela ", "💲 Proventos ","📶 Desempenho da carteira ","♨️ Objetivos ",
                                                        "🏦 Bancos "," 🩺 Detalhes da conta "," ☕ Atualizar dados "  ])


    with tab[0]:
        st.title('Ativos negociados ') 
        
        st.dataframe(df_posicao_fii[['Código de Negociação','Cotacao Atual',
                                'Preco medio','rentabilidade']].style.format("{:.6}"))
        
        st.dataframe(df_posicao_acao[['Código de Negociação','Cotacao Atual',
                                'Preco medio','rentabilidade']].style.format("{:.6}"))  
    
  
        

    with tab[1]:
        st.title('Proventos mensais')
        st.plotly_chart(px.bar(df_proventos.sort_index(ascending=False),
                            x='Pagamento',
                            y='Valor líquido',
                            title='',
                            color='Produto',
                            width =1450,
                            height=460))
        
        

    with tab[2]:
        
        st.title('Fundos imobiliarios')
        st.plotly_chart(px.line(df_fii_dadoHistorico_desempenho[df_fii_dadoHistorico_desempenho.columns[1:]],width = 1500,height=500  ))
        st.title('Ações')
        st.plotly_chart(px.line(df_acao_dadoHistorico_desempenho[df_acao_dadoHistorico_desempenho.columns[1:]],width = 1500,height=500))

        
    #Objetivos       
    with tab[3]:
        #Variaveis usadas
        anual = round(((rentabilidade+totalProventos)/pl)*100,2)
        carteira_lista=[]
        
        col = st.columns(5)
        with col[0]:
            carteira = st.number_input('Carteira inicial: ',value=0)
        with col[1]:
            investimento_Mensal = st.number_input('Aporte Mensal: ',value=1000)
        with col[2]:
            meses_Trabalho = st.number_input('Meses trabalhados: ',value=360)
        with col[3]:
            anual = round(((rentabilidade+totalProventos)/pl)*100,2)
            rendimento_mensal=st.number_input('Rendimento mensal atual: ',value=round((1+(anual/100)/12),4),format='%f')
        with col[4]:
            valor_objetivo = st.number_input('Objetivo de patrimonio: ',value=1000000)

        
        for i in range(meses_Trabalho):
            carteira = (carteira + investimento_Mensal)*(rendimento_mensal)
            carteira_lista.append(carteira)
            if  carteira >= valor_objetivo:
                break
        
        fig3 = px.line(carteira_lista,width = 1300,height=500)
        fig3.add_hline(y=pl,line_dash='dash')
    
        
     
                
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Expectativa de patrimônio alcançado", "R$ "+str(round(carteira_lista[-1],2)),"Valor atual: "+str(pl))
        with col2:    
            st.metric("Proventos mensais", "R$ "+str(round(((carteira_lista[-1]*0.06)/12),2)),"Valor atual: "+str(round(totalProventos/12,2)))  
        with col3:
            st.metric("Objetivo de rendimento mensal", '0.5%',"Valor atual: "+str(round(((rentabilidade+totalProventos)/pl)*100/12,2)))
        with col4:    
            st.metric("rendimento bruto alcançado", "R$ "+str(round(((investimento_Mensal*meses_Trabalho)-round(carteira_lista[-1],2))*-1,2)),"Valor atual: "+str(round(rentabilidade+totalProventos,2)))
            
       
        st.plotly_chart(fig3)
        if round(carteira_lista[-1],2) > valor_objetivo:
            st.warning('*** Você alcançara seu objetivo em: '+str(len(carteira_lista))+'Meses')
        else:
            st.warning('⚠️⚠️⚠️ Hey você precisa de mais meses para alcançar o seu objetivo ⚠️⚠️⚠️',)
             
    
    with tab[4]:    
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("NuBank","R$ "+str(nubank_aplicado),'Provimento: '+str(nubank_provento))

    
    with tab[5]:

        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Patrimônio Atual","R$ "+str(round(pl,2)),)
            st.metric('Rentabilidade da carteira sem proventos',"R$ "+str(round(rentabilidade,2)),)
            st.metric("Objetivo de patrimonio", "R$ "+str(round(carteira_lista[-1],2)),"Valor atual: "+str(pl))
        with col2:   
            st.metric("Valor aplicado","R$ "+str(round(compra-venda,2)),)
            st.metric(' - ',' - ')   
            st.metric("Possivel proventos mensais", "R$ "+str(round(((carteira_lista[-1]*0.06)/12),2)),"Valor atual: "+str(round(totalProventos/12,2)))  
        with col3:
            st.metric('Rentabilidade real',"R$ "+str(round(rentabilidade+totalProventos,2)) ,)
            st.metric(' - ',' - ')  
            st.metric("Objetivo de rendimento relativo mensal", '0.5%',"Valor atual: "+str(round(((rentabilidade+totalProventos)/pl)*100/12,2)))
        with col4: 
            st.metric('Rentabilidade relativa',str(round(rentabilidade_relativa*100,2))+'%' ,)
            st.metric('Total de proventos ',"R$ "+str(round(totalProventos,2)))   
            st.metric("rendimento bruto alcançado", "R$ "+str(round(((investimento_Mensal*meses_Trabalho)-round(carteira_lista[-1],2))*-1,2)),"Valor atual: "+str(round(rentabilidade+totalProventos,2)))

                  
        
    with tab[6]:
        
        upload = st.file_uploader('Arquivos B3 Negociacao, Posicao, Proventos recebidos:',type=['xlsx'],accept_multiple_files=False)
        if upload is not None:
            df = pd.read_excel(upload)
            st.write(upload.name[:19])
            if upload.name[:10] == 'negociacao':   
                df.to_excel('data/negociacao.xlsx')
                st.write('Salvo... negociacao')
            elif upload.name[:7] == 'posicao':   
                
                df_posicao_acao = pd.read_excel(upload,sheet_name='Acoes')
                df_posicao_fii = pd.read_excel(upload,sheet_name='Fundo de Investimento')
                
                writer = pd.ExcelWriter(r'data/posicao.xlsx', engine='xlsxwriter')
                df_posicao_acao.to_excel(writer,sheet_name='Acoes')
                df_posicao_fii.to_excel(writer,sheet_name='Fundo de Investimento')
                writer.save()
    
                st.write('Salvo...posicao')
                
            elif upload.name[:19] == 'proventos-recebidos':   
                df.to_excel('data/proventos-recebidos.xlsx')
                st.write('Salvo...proventos')

        if st.button("Atualizar valores"):
            atualizar_dados()
            st.experimental_rerun()
            
