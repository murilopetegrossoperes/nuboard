import pandas as pd

def categorizar_transacao(descricao):
    """
    Verifica a descrição da compra e retorna a categoria correspondente
    com base em palavras-chave.
    """
    # Dicionário de regras de categorização (tudo em minúsculo para facilitar a busca)
    regras = {
        'uber': 'Transporte',
        'lanchonete': 'Alimentação',
        'atm': 'Transporte',
        'abolicao': 'Alimentação',
        'lmb': 'Transporte',
        'lourencini': 'Mercado',
        'monster dog': 'Alimentação',
        '99app': 'Transporte',
        'posto': 'Transporte',
        'ifood': 'Alimentação',
        'mcdonalds': 'Alimentação',
        'supermercado': 'Mercado',
        'atacadao': 'Mercado',
        'netflix': 'Assinaturas',
        'spotify': 'Assinaturas',
        'totalpass': 'Assinaturas',
        'farmacia': 'Saúde',
        'drogasil': 'Saúde',
        'pagamento de fatura': 'Pagamento Fatura', # Movimentações que não são gastos
        'transferência recebida': 'Receita',
        'resgate': 'Investimentos',
        'subway': 'Alimentação',
        'mercado livre': 'Compras Online',
        'transferência enviada': 'Transferência',
        'realFood': 'Alimentação',
        'zig': 'Lazer',
        'carrefour': 'Mercado',
        'lojas americanas': 'Mercado',
        'magalu': 'Compras Online',
        'mp *geladeira': 'Outros',
        'zig*formosa hifi': 'Lazer',
        'ponto light comercio': 'Alimentação',
        'quiosque da cocada': 'Alimentação',
        'neusadelduque': 'Serviços',
        'sabordahora': 'Alimentação',
        'nova estacao maua': 'Alimentação',
        'carrefour sto': 'Mercado',
        'naominakane': 'Serviços',
        'moda mundial': 'Vestuário',
        'wks estacao cafe': 'Alimentação',
        'realfood': 'Alimentação',
        'johnnyalvesde': 'Serviços',
        '99 tecnologia': 'Transporte',
        'burger king': 'Alimentação',
        'valpan': 'Mercado',
        'bus facil': 'Transporte',
        'dadoo grill': 'Alimentação',
        'puro sabor': 'Alimentação',
        'kfc': 'Lazer',
    }
    
    # Converte a descrição para minúsculo para garantir que o texto vai "dar match"
    descricao_lower = str(descricao).lower()
    
    # Percorre o dicionário procurando as palavras-chave na descrição
    for chave, categoria in regras.items():
        if chave in descricao_lower:
            return categoria
            
    # Se nenhuma palavra-chave for encontrada, classifica como 'Outros'
    return 'Outros'

def carregar_dados(caminho_arquivo):
    """
    Carrega, limpa e categoriza os dados do extrato CSV do Nubank.
    """
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        
        colunas_map = {
            'Data': 'data',
            'Valor': 'valor',
            'identificador': 'identificador',
            'DescriÃ§Ã£o': 'descricao',
            'Descrição': 'descricao'
        }
        df = df.rename(columns=colunas_map)
        
        # 1. Tratamento de Data
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        
        # 2. Tratamento de Valor
        if df['valor'].dtype == 'O':  
            df['valor'] = df['valor'].astype(str).str.replace(',', '.').astype(float)
        else:
            df['valor'] = df['valor'].astype(float)
            
        # 3. Aplicação do Motor de Categorização
        # Criamos a nova coluna 'categoria' passando a função linha a linha
        df['categoria'] = df['descricao'].apply(categorizar_transacao)
        
        # 4. Ordenação
        df = df.sort_values('data').reset_index(drop=True)
        
        print("✅ Dados carregados e categorizados com sucesso!")
        
        # Opcional: mostrar quantas transações caíram em "Outros" para você refinar o dicionário depois
        qtd_outros = len(df[df['categoria'] == 'Outros'])
        print(f"Atenção: {qtd_outros} transações não identificadas (categoria 'Outros').")
        
        return df

    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {e}")
        return None

# Testando o script
if __name__ == "__main__":
    dados = carregar_dados("fatura.csv")
    
    if dados is not None:
        # Filtra a tabela mantendo apenas as linhas onde a categoria é 'Outros'
        df_outros = dados[dados['categoria'] == 'Outros']
        
        if not df_outros.empty:
            print(f"\n⚠️ Você tem {len(df_outros)} transações para categorizar:")
            
            # Força o Pandas a mostrar todas as linhas sem resumir com "..."
            pd.set_option('display.max_rows', None)
            
            # Imprime apenas as colunas que importam para você ler e ajustar
            print(df_outros[['data', 'descricao', 'valor']])
            
            # Retorna a configuração do Pandas ao padrão original
            pd.reset_option('display.max_rows')
        else:
            print("\n🎉 Excelente! Todas as transações foram mapeadas e categorizadas.")