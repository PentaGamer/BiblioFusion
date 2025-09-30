import pandas as pd
import os
import numpy as np

print("🔧 Iniciando processo de mesclagem das bases...")

# Verificar se os arquivos existem
arquivos_necessarios = ['wos_data.txt', 'scopus_data.csv']
for arquivo in arquivos_necessarios:
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        print("💡 Certifique-se de que os arquivos estão na mesma pasta do script")
        exit()

try:
    # Carregar dados
    print("📥 Carregando bases de dados...")
    wos_df = pd.read_csv('wos_data.txt', sep='\t', encoding='utf-8', low_memory=False)
    scopus_df = pd.read_csv('scopus_data.csv', encoding='utf-8', low_memory=False)
    
    print(f"✅ Web of Science: {len(wos_df)} registros")
    print(f"✅ Scopus: {len(scopus_df)} registros")
    
    # Adicionar identificador de fonte
    wos_df['Fonte'] = 'Web of Science'
    scopus_df['Fonte'] = 'Scopus'
    
    # Combinar os dados
    print("🔄 Combinando bases...")
    merged_df = pd.concat([wos_df, scopus_df], ignore_index=True)
    
    # Tentar remover duplicatas por DOI primeiro, depois por título
    colunas_duplicatas = ['DOI'] if 'DOI' in merged_df.columns else ['Title', 'Year']
    tamanho_inicial = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=colunas_duplicatas, keep='first')
    duplicatas_removidas = tamanho_inicial - len(merged_df)
    
    print(f"✅ Duplicatas removidas: {duplicatas_removidas}")
    print(f"📊 Total antes da limpeza: {len(merged_df)} registros")
    
    # 🔧 CORREÇÃO PARA AS DATAS - EXTRAIR APENAS O ANO
    print("📅 Corrigindo formato das datas para extrair apenas o ano...")
    
    # Verificar quais colunas de data/ano existem
    colunas_data = ['Year', 'Publication Year', 'Year of publication']
    coluna_ano_encontrada = None
    
    for coluna in colunas_data:
        if coluna in merged_df.columns:
            coluna_ano_encontrada = coluna
            print(f"✅ Coluna de ano encontrada: {coluna}")
            break
    
    if coluna_ano_encontrada:
        # Converter para string primeiro para lidar com diferentes formatos
        merged_df[coluna_ano_encontrada] = merged_df[coluna_ano_encontrada].astype(str)
        
        # Função para extrair apenas o ano
        def extrair_ano(valor):
            if pd.isna(valor) or valor == '' or valor == 'nan':
                return ''
            try:
                # Se for formato ano.mês (ex: 2024.6), pegar apenas a parte inteira
                if '.' in str(valor):
                    return str(int(float(valor)))
                # Se for apenas número, converter para inteiro
                elif valor.replace('.', '').isdigit():
                    return str(int(float(valor)))
                # Se já for string com ano, manter
                else:
                    return str(valor)
            except:
                return ''
        
        # Aplicar a função para extrair apenas o ano
        merged_df[coluna_ano_encontrada] = merged_df[coluna_ano_encontrada].apply(extrair_ano)
        
        # Converter para numérico e remover valores inválidos
        merged_df[coluna_ano_encontrada] = pd.to_numeric(merged_df[coluna_ano_encontrada], errors='coerce')
        
        # Remover registros com ano inválido
        registros_antes = len(merged_df)
        merged_df = merged_df[merged_df[coluna_ano_encontrada].notna()]
        merged_df = merged_df[merged_df[coluna_ano_encontrada] >= 1900]
        merged_df = merged_df[merged_df[coluna_ano_encontrada] <= 2025]
        
        # Converter para inteiro
        merged_df[coluna_ano_encontrada] = merged_df[coluna_ano_encontrada].astype(int)
        
        registros_removidos = registros_antes - len(merged_df)
        print(f"✅ Registros com datas inválidas removidos: {registros_removidos}")
        
        # Renomear coluna para padronizar
        merged_df.rename(columns={coluna_ano_encontrada: 'Year'}, inplace=True)
    else:
        print("⚠️  Nenhuma coluna de ano encontrada. Criando coluna Year vazia.")
        merged_df['Year'] = ''
    
    # Garantir que as colunas essenciais para VOSviewer existam
    colunas_essenciais_vosviewer = [
        'Title', 'Authors', 'Year', 'Source title', 'DOI', 'Abstract', 
        'Cited by', 'References', 'Fonte'
    ]
    
    for coluna in colunas_essenciais_vosviewer:
        if coluna not in merged_df.columns:
            merged_df[coluna] = ''
            print(f"⚠️  Coluna '{coluna}' não encontrada. Criando coluna vazia.")
    
    # Preencher valores NaN com string vazia
    merged_df = merged_df.fillna('')
    
    print(f"📊 Total final após limpeza: {len(merged_df)} registros")
    
    # Verificar os anos únicos para confirmar
    anos_unicos = sorted(merged_df['Year'].unique())
    print(f"📅 Anos únicos encontrados: {anos_unicos}")
    
    # Salvar arquivo
    output_file = 'base_bibliometrica_apenas_ano.csv'
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"🎉 Arquivo salvo com sucesso: {output_file}")
    print("📁 O arquivo está pronto para usar no VOSviewer!")
    print("\n📋 Estatísticas finais:")
    print(f"   - Total de registros: {len(merged_df)}")
    print(f"   - Período: {merged_df['Year'].min()} - {merged_df['Year'].max()}")
    print(f"   - Fontes: {merged_df['Fonte'].value_counts().to_dict()}")
    
except Exception as e:
    print(f"❌ Erro durante o processamento: {e}")
    print("💡 Verifique se os arquivos estão no formato correto")