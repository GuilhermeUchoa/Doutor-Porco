import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import hydralit_components as hc
from library.data_refresh import atualizar_dados
import warnings
warnings.simplefilter("ignore")

#Carregando dataframe
df_proventos = pd.read_csv('data/df_proventos.csv')
df_posicao_acao = pd.read_csv('data/df_posicao_acao.csv')
df_posicao_fii = pd.read_csv('data/df_posicao_fii.csv')
df_negociacao = pd.read_csv('data/df_negociacao.csv')
df_fii_dadoHistorico = pd.read_csv('data/df_fii_dadoHistorico.csv')
df_acao_dadoHistorico = pd.read_csv('data/df_acao_dadoHistorico.csv')
df_fii_dadoHistorico_desempenho = pd.read_csv('data/df_fii_dadoHistorico_desempenho.csv')
df_acao_dadoHistorico_desempenho = pd.read_csv('data/df_acao_dadoHistorico_desempenho.csv')



#Variaveis usadas
compra = round(df_negociacao[df_negociacao['Tipo de Movimentação']=='Compra']['Valor'].sum(),2)
venda = round(df_negociacao[df_negociacao['Tipo de Movimentação']=='Venda']['Valor'].sum(),2)
totalProventos = round(df_proventos['Valor líquido'].sum(),2)
pl = df_posicao_fii['Valor total atual'].sum() + df_posicao_acao['Valor total atual'].sum()
rentabilidade = pl-(compra-venda)

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
        st.success(round(compra-venda,2),icon="💲")
        st.header('Rentabilidade real')
        st.success(round(rentabilidade+totalProventos,2),icon="💲")
        st.header('Rentabilidade relativa')
        st.success(str(round(((rentabilidade+totalProventos)/pl)*100,2))+"%",icon="💲")
        st.header('Total de proventos ')
        st.success(round(totalProventos,2),icon="💲")
        


with st.container():
    
    tab = st.tabs(["📄 Tabela ", "💲 Proventos ", "📊 Histogramas ", "📶 Desempenho da carteira ","♨️ Objetivos ",
                                                        "💡 Ideias ", "☕ Atualizar dados "," 🩺 Detalhes da conta " ,"🔴 Sobre Doutor Porco ", ])


    with tab[0]:
        st.title('Ativos negociados ') 
        
        st.dataframe(df_posicao_fii[['Código de Negociação','Valor Atualizado',
                                'Valor total atual','Valor total investido',
                                'Preco medio','rentabilidade']].style.format("{:.6}"))
        
        st.dataframe(df_posicao_acao[['Código de Negociação','Valor Atualizado',
                                'Valor total atual','Valor total investido',
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
        

        
        fig1 = plt.figure(figsize=(20,20))
        for i in range(1,len(df_fii_dadoHistorico.columns)):
            plt.subplot(len(df_fii_dadoHistorico.columns),2,i+0)
            sns.histplot(df_fii_dadoHistorico[df_fii_dadoHistorico.columns[i]],kde=True)
            plt.axvline(df_fii_dadoHistorico[df_fii_dadoHistorico.columns[i]].iloc[-1],color='green',label='Preço atual') #Preço atual
            plt.legend()
            plt.axvline(df_fii_dadoHistorico[df_fii_dadoHistorico.columns[i]].mode().mean(),color='red',label='Preço Modal medio') #Preço modal
            plt.legend()
            plt.xlabel("")
            plt.ylabel(round(df_fii_dadoHistorico[df_fii_dadoHistorico.columns[i]].iloc[-1],2))#preco atual
            plt.title(df_fii_dadoHistorico.columns[i])
        
        st.title('Fundos imobiliarios')    
        st.pyplot(fig1)
            
        fig2 = plt.figure(figsize=(25,25))
        for i in range(1,len(df_acao_dadoHistorico.columns)):
            plt.subplot(len(df_acao_dadoHistorico.columns),2,i+0)
            sns.histplot(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[i]],kde=True)
            plt.axvline(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[i]].iloc[-1],color='green',label='Preço atual') #Preço atual
            plt.legend()
            plt.axvline(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[i]].mode().mean(),color='red',label='Preço Modal medio') #Preço modal
            plt.legend()
            plt.xlabel("")
            plt.ylabel(round(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[i]].iloc[-1],2))#preco atual
            plt.title(df_acao_dadoHistorico.columns[i])
            
        st.title('Ações')  
        st.pyplot(fig2)
            

    with tab[3]:
        
        st.title('Fundos imobiliarios')
        st.plotly_chart(px.line(df_fii_dadoHistorico_desempenho[df_fii_dadoHistorico_desempenho.columns[1:]],width = 1500,height=500  ))
        st.title('Ações')
        st.plotly_chart(px.line(df_acao_dadoHistorico_desempenho[df_acao_dadoHistorico_desempenho.columns[1:]],width = 1500,height=500))

        
    #Objetivos       
    with tab[4]:
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
        
        fig3 = px.line(carteira_lista,width = 1700,height=500)
        fig3.add_hline(y=pl,line_dash='dash')
    
        
     
                
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Expectativa de patrimônio alcançado", "R$ "+str(round(carteira_lista[-1],2)),"Valor atual: "+str(pl))
        with col2:    
            st.metric("Proventos mensais", "R$ "+str(round(((carteira_lista[-1]*0.06)/12),2)),"Valor atual: "+str(round(totalProventos/12,2)))  
        with col3:
            st.metric("Objetivo de rendimento mensal", '0.5%',"Valor atual: "+str(round(((rentabilidade+totalProventos)/pl)*100/12,2)))
        with col4:    
            st.metric("rendimento bruto alcançado", "R$ "+str(((investimento_Mensal*meses_Trabalho)-round(carteira_lista[-1],2))*-1),"Valor atual: "+str(round(rentabilidade+totalProventos,2)))
            
       
        st.plotly_chart(fig3)
        if round(carteira_lista[-1],2) > valor_objetivo:
            st.warning('*** Você alcançara seu objetivo em: '+str(len(carteira_lista))+'Meses')
        else:
            st.warning('⚠️⚠️⚠️ Hey você precisa de mais meses para alcançar o seu objetivo ⚠️⚠️⚠️',)
             
    
    with tab[5]:    
        txt = st.text_area('Digite suas ideias', )
        
        with open('note/ideias.txt','a') as f:
            lines = f.write(txt)
            

        ler =  open('note/ideias.txt','r')
        st.write('Ideias salvas', ler.readlines())
        ler.close()
        
    with tab[6]:
        
        upload = st.file_uploader('Arquivos B3 Negociacao, Posicao, Proventos recebidos:',type=['xlsx'],accept_multiple_files=False)
        if upload is not None:
            df = pd.read_excel(upload)
            st.write(upload.name[:19])
            if upload.name[:10] == 'negociacao':   
                df.to_excel('data/negociacao.xlsx')
                st.write('Salvo... negociacao')
            elif upload.name[:7] == 'posicao':   
                df.to_excel('data/posicao.xlsx')
                st.write('Salvo...posicao')
            elif upload.name[:19] == 'proventos-recebidos':   
                df.to_excel('data/proventos-recebidos.xlsx')
                st.write('Salvo...proventos')

        if st.button("Atualizar valores"):
            with hc.HyLoader('Now doing loading',hc.Loaders.standard_loaders,index=[0]):
                atualizar_dados()
                st.experimental_rerun()
                
    
    with tab[7]:

        
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
            st.metric('Rentabilidade relativa',str(round(((rentabilidade+totalProventos)/pl)*100,2))+'%' ,)
            st.metric('Total de proventos ',"R$ "+str(round(totalProventos,2)))   
            st.metric("rendimento bruto alcançado", "R$ "+str(((investimento_Mensal*meses_Trabalho)-round(carteira_lista[-1],2))*-1),"Valor atual: "+str(round(rentabilidade+totalProventos,2)))

        
        
    with tab[8]:
        col = st.columns(2)
        with col[0]:
            st.image('img/pig.jpg',caption='')
            
        with col[1]:
            st.title('Sobre Nós:') 
            st.text('''
                    
                       Somos um sistema financeiro que busca integrar informações no sistema B3/CEI
                       e informações bancárias com o intuido de gerenciar, sua vida financeira,
                       de formar que auxilie para fazer planos rentaveis.  
            
                    
                    
                    
                    ''')   
        

