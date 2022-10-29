import pandas as pd
import numpy as np
import pandas_datareader as pdr
import warnings
warnings.simplefilter("ignore")


#Atualizar dados atuais
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
        
    #Transformar nomes em simples nomes
    for i in range(len(df_proventos['Produto'])):
        df_proventos['Produto'].iloc[i] = df_proventos['Produto'].iloc[i].split('-')[0]
    
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

    for i in range(len(df_posicao_acao['Código de Negociação'])):
        for j in  range(len(df_acao_dadoHistorico.columns)):                
            if df_posicao_acao['Código de Negociação'].iloc[i] == df_acao_dadoHistorico.columns[j][:-3]:                  
                df_posicao_acao['Valor Atualizado'][i] =  round(df_acao_dadoHistorico[df_acao_dadoHistorico.columns[j]][-1],2)
    

    
        
    #Cria valor total atual   
    df_posicao_fii['Valor total atual'] = df_posicao_fii['Valor Atualizado'] * df_posicao_fii['Quantidade']
    df_posicao_acao['Valor total atual'] = df_posicao_acao['Valor Atualizado'] * df_posicao_acao['Quantidade']
    
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


    
 