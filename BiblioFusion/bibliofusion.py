#!/usr/bin/env python3
"""
BiblioFusion - Fusão Bibliográfica Inteligente
Script principal para mesclar bases Web of Science e Scopus
Autor: [Seu Nome]
Versão: 1.0.0
"""

import pandas as pd
import os
import sys
from datetime import datetime
import shutil

# Configurações do projeto
CONFIG = {
    'input_dir': 'inputs',
    'output_dir': 'outputs', 
    'docs_dir': 'docs',
    'required_files': ['wos_data.txt', 'scopus_data.csv'],
    'output_filename': 'bibliofusion_output.csv',
    'report_filename': 'processing_report.txt'
}

class BiblioFusion:
    def __init__(self):
        self.setup_directories()
        self.processing_log = []
        
    def setup_directories(self):
        """Cria a estrutura de diretórios do projeto"""
        directories = [CONFIG['input_dir'], CONFIG['output_dir'], CONFIG['docs_dir']]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log(f"✅ Diretório criado: {directory}")
            else:
                self.log(f"📁 Diretório encontrado: {directory}")
    
    def log(self, message):
        """Registra mensagens no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.processing_log.append(log_message)
        print(log_message)
    
    def check_input_files(self):
        """Verifica se os arquivos de entrada existem"""
        missing_files = []
        
        for file in CONFIG['required_files']:
            file_path = os.path.join(CONFIG['input_dir'], file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            self.log(f"❌ Arquivos não encontrados: {missing_files}")
            self.log("💡 Coloque os arquivos na pasta 'inputs/':")
            for file in missing_files:
                self.log(f"   - {file}")
            return False
        
        self.log("✅ Todos os arquivos de entrada encontrados")
        return True
    
    def load_data(self):
        """Carrega os dados das bases Web of Science e Scopus"""
        try:
            # Carregar Web of Science
            wos_path = os.path.join(CONFIG['input_dir'], 'wos_data.txt')
            self.log("📥 Carregando Web of Science...")
            wos_df = pd.read_csv(wos_path, sep='\t', encoding='utf-8', low_memory=False)
            self.log(f"✅ Web of Science: {len(wos_df)} registros")
            
            # Carregar Scopus
            scopus_path = os.path.join(CONFIG['input_dir'], 'scopus_data.csv')
            self.log("📥 Carregando Scopus...")
            scopus_df = pd.read_csv(scopus_path, encoding='utf-8', low_memory=False)
            self.log(f"✅ Scopus: {len(scopus_df)} registros")
            
            return wos_df, scopus_df
            
        except Exception as e:
            self.log(f"❌ Erro ao carregar dados: {e}")
            return None, None
    
    def process_data(self, wos_df, scopus_df):
        """Processa e mescla os dados"""
        # Adicionar identificador de fonte
        wos_df['Fonte'] = 'Web of Science'
        scopus_df['Fonte'] = 'Scopus'
        
        # Combinar os dados
        self.log("🔄 Combinando bases...")
        merged_df = pd.concat([wos_df, scopus_df], ignore_index=True)
        initial_count = len(merged_df)
        
        # Remover duplicatas
        self.log("🎯 Removendo duplicatas...")
        if 'DOI' in merged_df.columns:
            merged_df = merged_df.drop_duplicates(subset=['DOI'], keep='first')
            duplicates_removed = initial_count - len(merged_df)
            self.log(f"✅ Duplicatas removidas por DOI: {duplicates_removed}")
        else:
            merged_df = merged_df.drop_duplicates(subset=['Title', 'Year'], keep='first')
            duplicates_removed = initial_count - len(merged_df)
            self.log(f"✅ Duplicatas removidas por Título/Ano: {duplicates_removed}")
        
        # Processar datas
        self.log("📅 Processando datas...")
        merged_df = self.process_dates(merged_df)
        
        # Garantir colunas essenciais
        merged_df = self.ensure_essential_columns(merged_df)
        
        return merged_df, duplicates_removed
    
    def process_dates(self, df):
        """Processa e corrige formatos de data"""
        colunas_data = ['Year', 'Publication Year', 'Year of publication']
        coluna_ano_encontrada = None
        
        for coluna in colunas_data:
            if coluna in df.columns:
                coluna_ano_encontrada = coluna
                break
        
        if coluna_ano_encontrada:
            # Converter para string e extrair ano
            df[coluna_ano_encontrada] = df[coluna_ano_encontrada].astype(str)
            
            def extrair_ano(valor):
                if pd.isna(valor) or valor == '' or valor == 'nan':
                    return ''
                try:
                    if '.' in str(valor):
                        return str(int(float(valor)))
                    elif valor.replace('.', '').isdigit():
                        return str(int(float(valor)))
                    else:
                        return str(valor)
                except:
                    return ''
            
            df[coluna_ano_encontrada] = df[coluna_ano_encontrada].apply(extrair_ano)
            df[coluna_ano_encontrada] = pd.to_numeric(df[coluna_ano_encontrada], errors='coerce')
            
            # Filtrar anos válidos
            df = df[df[coluna_ano_encontrada].notna()]
            df = df[df[coluna_ano_encontrada] >= 1900]
            df = df[df[coluna_ano_encontrada] <= datetime.now().year + 1]
            
            df[coluna_ano_encontrada] = df[coluna_ano_encontrada].astype(int)
            df.rename(columns={coluna_ano_encontrada: 'Year'}, inplace=True)
            
            self.log("✅ Datas processadas com sucesso")
        
        return df
    
    def ensure_essential_columns(self, df):
        """Garante que as colunas essenciais existam"""
        colunas_essenciais = [
            'Title', 'Authors', 'Year', 'Source title', 'DOI', 
            'Abstract', 'Cited by', 'References', 'Fonte'
        ]
        
        for coluna in colunas_essenciais:
            if coluna not in df.columns:
                df[coluna] = ''
                self.log(f"⚠️ Coluna '{coluna}' não encontrada. Criada coluna vazia.")
        
        return df.fillna('')
    
    def generate_report(self, merged_df, duplicates_removed, processing_time):
        """Gera relatório detalhado do processamento"""
        report_content = []
        report_content.append("=" * 50)
        report_content.append("RELATÓRIO BIBLIOFUSION")
        report_content.append("=" * 50)
        report_content.append(f"Data do processamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"Tempo de processamento: {processing_time:.2f} segundos")
        report_content.append("")
        
        # Estatísticas
        total_records = len(merged_df)
        wos_count = len(merged_df[merged_df['Fonte'] == 'Web of Science'])
        scopus_count = len(merged_df[merged_df['Fonte'] == 'Scopus'])
        
        report_content.append("📊 ESTATÍSTICAS:")
        report_content.append(f"  Total de registros: {total_records:,}")
        report_content.append(f"  - Web of Science: {wos_count:,} ({wos_count/total_records*100:.1f}%)")
        report_content.append(f"  - Scopus: {scopus_count:,} ({scopus_count/total_records*100:.1f}%)")
        report_content.append(f"  Duplicatas removidas: {duplicates_removed:,}")
        
        # Período temporal
        if 'Year' in merged_df.columns and not merged_df['Year'].empty:
            min_year = merged_df['Year'].min()
            max_year = merged_df['Year'].max()
            anos_unicos = sorted(merged_df['Year'].unique())
            report_content.append("")
            report_content.append("📅 PERÍODO TEMPORAL:")
            report_content.append(f"  Período: {min_year} - {max_year}")
            report_content.append(f"  Anos cobertos: {len(anos_unicos)} anos")
        
        # Arquivos gerados
        report_content.append("")
        report_content.append("💾 ARQUIVOS GERADOS:")
        report_content.append(f"  Base mesclada: {CONFIG['output_filename']}")
        report_content.append(f"  Este relatório: {CONFIG['report_filename']}")
        
        # Log do processamento
        report_content.append("")
        report_content.append("📝 LOG DO PROCESSAMENTO:")
        for log_entry in self.processing_log:
            report_content.append(f"  {log_entry}")
        
        report_content.append("")
        report_content.append("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        report_content.append("=" * 50)
        
        return "\n".join(report_content)
    
    def save_results(self, merged_df, report_content):
        """Salva os resultados processados"""
        try:
            # Salvar base mesclada
            output_path = os.path.join(CONFIG['output_dir'], CONFIG['output_filename'])
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            self.log(f"💾 Base salva: {output_path}")
            
            # Salvar relatório
            report_path = os.path.join(CONFIG['output_dir'], CONFIG['report_filename'])
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.log(f"📄 Relatório salvo: {report_path}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar resultados: {e}")
            return False
    
    def run(self):
        """Executa o fluxo completo do BiblioFusion"""
        start_time = datetime.now()
        
        self.log("🚀 INICIANDO BIBLIOFUSION")
        self.log("=" * 50)
        
        # Verificar arquivos
        if not self.check_input_files():
            return False
        
        # Carregar dados
        wos_df, scopus_df = self.load_data()
        if wos_df is None or scopus_df is None:
            return False
        
        # Processar dados
        merged_df, duplicates_removed = self.process_data(wos_df, scopus_df)
        
        # Calcular tempo
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Gerar relatório
        report_content = self.generate_report(merged_df, duplicates_removed, processing_time)
        
        # Salvar resultados
        if self.save_results(merged_df, report_content):
            self.log("")
            self.log("🎉 BIBLIOFUSION CONCLUÍDO COM SUCESSO!")
            self.log(f"📊 {len(merged_df):,} registros processados")
            self.log(f"⏱️  Tempo total: {processing_time:.2f} segundos")
            return True
        else:
            return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🎯 BIBLIOFUSION - Fusão Bibliográfica Inteligente")
    print("="*60)
    
    # Verificar dependências
    try:
        import pandas as pd
        import numpy as np
    except ImportError as e:
        print(f"❌ Dependências não encontradas: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return
    
    # Executar BiblioFusion
    bf = BiblioFusion()
    success = bf.run()
    
    if success:
        print("\n✅ Processamento concluído! Verifique a pasta 'outputs/'")
    else:
        print("\n❌ Ocorreu um erro durante o processamento")
        print("📖 Consulte a documentação em 'docs/' para ajuda")

if __name__ == "__main__":
    main()