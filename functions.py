def configure_entrez(default_api_key='b7a9a1370cb8c51672e5c1dfcd7117a47108', default_email='marioassis1996@gmail.com'):
    """
    Configura as credenciais para o NCBI Entrez.

    Solicita ao usuário que forneça as configurações do NCBI Entrez e as define.
    O usuário pode fornecer a chave da API e o e-mail associado. Caso não forneça,
    serão utilizados valores preestabelecidos.

    Parâmetros:
    default_api_key (str): Chave da API padrão para o NCBI Entrez.
    default_email (str): E-mail padrão para o NCBI Entrez.
    """
    api_key = input(f"Por favor, insira a sua chave da API do NCBI Entrez: ")
    email = input(f"Por favor, insira o seu e-mail para uso com o NCBI Entrez: ")

    # Utiliza valores preestabelecidos se o usuário não fornecer
    if not api_key:
        api_key = default_api_key
        logging.info("Usando chave da API padrão do NCBI Entrez.")
    if not email:
        email = default_email
        logging.info("Usando e-mail padrão do NCBI Entrez.")

    Entrez.api_key = api_key
    Entrez.email = email

    logging.info(f"Configurações do NCBI Entrez definidas. Chave da API: {api_key}, E-mail: {email}")

    print("Configurações do NCBI Entrez definidas com sucesso!")

def search_NCBI(search_for, max_retries=3):
    """
    Realiza uma busca no NCBI usando o termo especificado.

    Parâmetros:
    search_for (str): Termo a ser pesquisado.
    max_retries (int): Número máximo de tentativas de consulta.

    Retorna:
    dict: Resultado da busca no formato de dicionário.
    """
    for tentativa in range(max_retries + 1):
        try:
            handle = Entrez.esearch(db='taxonomy', term=search_for)
            result = Entrez.read(handle)
            handle.close()
            return result
        except Exception as e:
            logging.error(f"Erro ao realizar a busca no NCBI para '{search_for}' na tentativa {tentativa+1}: {e}")
            if tentativa == max_retries:
                return None

def efetch_NCBI(efetch_for, max_retries=3):
    """
    Realiza uma busca no NCBI usando o termo especificado.

    Parâmetros:
    efetch_for (str): Termo a ser pesquisado.
    max_retries (int): Número máximo de tentativas de consulta.

    Retorna:
    dict: Resultado da busca no formato de dicionário.
    """
    for tentativa in range(max_retries + 1):
        try:
            stream = Entrez.efetch(db='taxonomy', id=efetch_for)
            result = Entrez.read(stream)
            stream.close()
            return result
        except Exception as e:
            logging.error(f"Erro ao realizar a busca no NCBI para '{efetch_for}' na tentativa {tentativa+1}: {e}")
            if tentativa == max_retries:
                return None

def search_tax_id(scientific_name, max_retries=3):
    """
    Realiza uma busca pelo ID de taxonomia de um nome científico.

    Parâmetros:
    scientific_name (str): Nome científico da espécie.
    max_retries (int): Número máximo de tentativas de consulta.

    Retorna:
    str: O ID de taxonomia da espécie.
    """
    result = search_NCBI(scientific_name, max_retries)
    if result:
        txid = ','.join(result['IdList'])
        if txid:
            logging.info(f"ID de taxonomia obtido com sucesso para '{scientific_name}'.")
            return txid
        else:
            logging.warning(f"Nome científico '{scientific_name}' não encontrado na pesquisa.")
            return None
    else:
        logging.error(f"Erro ao buscar ID de taxonomia para '{scientific_name}'.")
        return None

def fetch_tax_info(txid, max_retries=3):
    """
    Obtém informações de taxonomia para um determinado ID de taxonomia.

    Parâmetros:
    txid (str): O ID de taxonomia da espécie.
    max_retries (int): Número máximo de tentativas de consulta.

    Retorna:
    tuple: Uma tupla contendo o nome científico, a classificação taxonômica
    e o ID do taxonômico superior.
    """
    record = efetch_NCBI(txid, max_retries)
    if record:
        name = record[0]['ScientificName']
        rank = record[0]['Rank']
        taxid_sup_rank = record[0]['LineageEx'][-1]['TaxId']
        logging.info(f"Informações de taxonomia obtidas com sucesso para '{name}'.")
        return name, rank, taxid_sup_rank
    else:
        logging.error(f"Erro ao obter informações de taxonomia para o ID '{txid}'.")
        return None, None, None

def get_taxonomy_id(scientific_name, max_retries=3):
    """
    Obtém informações de taxonomia para um nome científico.

    Parâmetros:
    scientific_name (str): Nome científico da espécie.
    max_retries (int): Número máximo de tentativas de consulta.

    Retorna:
    tuple: Uma tupla contendo o nome científico, o ID de taxonomia, a classificação
    taxonômica e o ID do taxonômico superior, além de uma string vazia ou com os nomes de espécies que 
    não foram encontradas.
    """
    errors = ''
    txid = search_tax_id(scientific_name, max_retries)
    if txid:
        name, rank, taxid_sup_rank = fetch_tax_info(txid, max_retries)
        time.sleep(0.1)
        return name, txid, rank, taxid_sup_rank, errors
    else:
        errors = scientific_name
        time.sleep(0.1)
        return None, None, None, None, errors

def salvar_arquivo(extensao='.csv'):
    """
    Abre uma janela de seleção de arquivo para o usuário escolher o local e o nome do arquivo CSV.

    Retorna:
    str: O caminho completo do arquivo a ser salvo.
    """
    print("Abrindo caixa de seleção para salvar o arquivo. Por favor, verifique se a janela não está oculta.")
    # Criar uma instância da janela principal do Tkinter e ocultá-la
    root = tk.Tk()
    root.withdraw()

    # Exibir uma mensagem na caixa de seleção de arquivos
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=extensao,
        # filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar Arquivo"
    )
    return caminho_arquivo

def selecionar_arquivo():
    """
    Abre uma janela de seleção de arquivo para o usuário escolher um arquivo CSV.

    Retorna:
    str: O caminho completo do arquivo selecionado.
    """
    print("Abrindo caixa de seleção de arquivo. Por favor, verifique se a janela não está oculta.")

    # Criar uma instância da janela principal do Tkinter e ocultá-la
    root = tk.Tk()
    root.withdraw()

    # Exibir uma mensagem na caixa de seleção de arquivos
    arquivo_csv = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[("Arquivo", "*.*")],
        multiple=False
    )

    # Retornar o caminho do arquivo selecionado
    return arquivo_csv

def ler_arquivo_csv():
    """
    Lê o arquivo CSV selecionado e verifica se contém a coluna 'scientificName'.

    Retorna:
    DataFrame: O DataFrame contendo os dados do arquivo CSV se a coluna 'scientificName' estiver presente, caso contrário, None.
    """
    arquivo_csv = selecionar_arquivo()
    try:
        logging.info(f"Lendo o arquivo CSV: {arquivo_csv}")
        df = pd.read_csv(arquivo_csv)
        if 'scientificName' not in df.columns:
            logging.error(f"O arquivo selecionado {arquivo_csv} não contém a coluna 'scientificName'.")
            messagebox.showerror("Erro", "O arquivo selecionado não contém a coluna 'scientificName'. Por favor, selecione outro arquivo.")
            # Chama recursivamente a função para selecionar um novo arquivo
            return ler_arquivo_csv()
        else:
            logging.info(f"Coluna 'scientificName' encontrada no arquivo {arquivo_csv}.")
            return df
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo CSV: {e}")
        messagebox.showerror("Erro", f"Erro ao ler o arquivo CSV: {e}")

def get_children(tax_hierar, nome_cientifico_col='scientificName', filhos_col='index_filho', root=any, arvore={}):
    """
    Função recursiva para obter os filhos de um nó na hierarquia taxonômica.

    Parâmetros:
    tax_hierar (DataFrame): O DataFrame contendo a hierarquia taxonômica.
    nome_cientifico_col (str): O nome da coluna que contém os nomes científicos dos táxons.
    filhos_col (str): O nome da coluna que contém os índices dos filhos de cada táxon.
    root (any): O nó raiz para começar a construção da árvore. Padrão: qualquer valor.
    arvore (dict): O dicionário que representa a árvore. Padrão: {}.

    Retorna:
    None
    """
    indices_filho = tax_hierar.loc[tax_hierar[nome_cientifico_col] == root, filhos_col].values
    if len(indices_filho) > 0:
        indices_filho = indices_filho[0]
        if pd.notna(indices_filho):
            indices_filho = indices_filho.split(',')
            indices_filho = [int(i) for i in indices_filho]
            filhos_raiz = tax_hierar.loc[indices_filho, nome_cientifico_col]
            arvore[root] = {filho for filho in filhos_raiz}

            # Adicionar os filhos à raiz correspondente no dicionário arvore
            for filho in filhos_raiz:
                get_children(tax_hierar, root=filho)

def construir_arvore_taxonomica(tax_hierar, nome_cientifico_col='scientificName', filhos_col='index_filho', root=any):
    """
    Constrói uma árvore taxonômica a partir dos dados de hierarquia taxonômica fornecidos.

    Parâmetros:
    tax_hierar (DataFrame): O DataFrame contendo a hierarquia taxonômica.
    nome_cientifico_col (str): O nome da coluna que contém os nomes científicos dos táxons.
    filhos_col (str): O nome da coluna que contém os índices dos filhos de cada táxon.
    root (any): O nó raiz ou uma lista de nós raiz para começar a construção da árvore. Padrão: qualquer valor.

    Retorna:
    dict: Um dicionário representando a árvore taxonômica.
    """
    # Inicializar a árvore
    arvore = {}
    
    # Inicializar a árvore com a raiz 'Eukaryota'
    arvore['Eukaryota'] = {'Metazoa', 'Viridiplantae'}

    # Chamar a função get_children para construir a árvore a partir das raízes fornecidas
    for raiz in root:
        get_children(tax_hierar, root=raiz, arvore=arvore)

    return arvore

def arvore_para_newick(arvore, no_raiz):
    """
    Converte uma árvore representada como um dicionário em formato Newick.

    Parâmetros:
    arvore (dict): O dicionário representando a árvore.
    no_raiz (str): O nó raiz da árvore.

    Retorna:
    str: A representação Newick da árvore.
    """
    if no_raiz not in arvore:
        return no_raiz
    else:
        filhos = arvore[no_raiz]
        newick = "("
        # Converte recursivamente os filhos em formato Newick
        for filho in filhos:
            newick += arvore_para_newick(arvore, filho) + ","
        newick = newick[:-1] + ")"  # Remove a última vírgula e adiciona parênteses de fechamento
        return newick + no_raiz

# Esta URL e a string 'rank_dwc' precisam ser explicadas
url_api = 'http://bioinfo.icb.ufmg.br/cgi-bin/taxallnomy/taxallnomy_multi.pl'
rank_dwc = 'Kingdom, Phylum, Class, Order, Superfamily, Family, Subfamily, Genus, Subgenus, Species'
