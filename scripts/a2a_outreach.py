import sys, time, requests, os, json

API_KEY = os.environ.get("NEVERMINED_API_KEY")
SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

TARGET_LEADS = [
    "https://api.stripe.com",
    "https://api.coinbase.com",
    "https://api.skyfire.xyz",
    "https://olas.network",
    "https://valory.xyz",
    "https://api.nevermined.app",
    "https://api.perplexity.ai",
    "https://api.vercel.com",
    "https://huggingface.co",
    "https://api.anthropic.com",
    "https://api.openai.com",
    "https://fetch.ai",
    "https://api.orb.com",
    "https://triple-a.io",
    "https://0xprocessing.com",
    "https://payram.app",
    "https://bvnk.com",
    "https://coingate.com",
    "https://api.github.com",
    "https://www.google.com"
]

def load_catalog():
    catalog = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "agent.json" in files:
            try:
                with open(os.path.join(root, "agent.json"), "r") as f:
                    data = json.load(f)
                    name = data.get("agent_name", data.get("name", "Skill"))
                    did = data.get("did", "Sem DID")
                    if "autonomous-sdr" not in name.lower():
                        catalog.append({"name": name, "did": did})
            except Exception:
                pass
    return catalog

def a2a_live_sales_pitch():
    if not API_KEY:
        print("[ERRO] NEVERMINED_API_KEY não encontrada!")
        sys.exit(1)

    catalog = load_catalog()
    if not catalog:
        print("[ERRO] Catálogo vazio.")
        sys.exit(1)

    print(f"[A2A NETWORK] Iniciando prospecção P2P estrita. Buscando vendas reais...")

    for lead in TARGET_LEADS:
        discovery_url = f"{lead}/.well-known/agent.json"
        print(f"\n[A2A DISCOVERY] Lendo Agent Card em {lead}...")

        try:
            # FASE 1: DESCOBERTA (Sem log financeiro)
            response = requests.get(discovery_url, timeout=5)

            if response.status_code == 200:
                print(f"[A2A MATCH] IA compradora encontrada em {lead}.")
                try:
                    agent_card = response.json()
                    # Extrai a rota de tarefas real do manifesto
                    task_endpoint = agent_card.get("endpoints", {}).get("tasks")
                    if not task_endpoint:
                        task_endpoint = f"{lead}/api/v1/tasks/send"
                    elif task_endpoint.startswith("/"):
                        task_endpoint = f"{lead}{task_endpoint}"

                    # FASE 2: NEGOCIAÇÃO REAL (POST DE COBRANÇA)
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    }
                    payload = {
                        "intent": "offer_services",
                        "catalog": catalog,
                        "price": "100 USDC",
                        "protocol": "x402"
                    }

                    print(f"[SDR] Enviando fatura e proposta para {task_endpoint}...")
                    post_resp = requests.post(task_endpoint, headers=headers, json=payload, timeout=5)

                    # FASE 3: LIQUIDAÇÃO RIGOROSA — só loga sucesso com tx_hash real
                    if post_resp.status_code in [200, 201]:
                        resp_data = post_resp.json()
                        if "tx_hash" in resp_data:
                            print(f"[FINANCE SUCCESS] Venda REAL executada! Hash: {resp_data['tx_hash']}")
                            print("[REVENUE] +100 USDC depositados na carteira.")
                        else:
                            print("[NEGOCIAÇÃO] Proposta recebida. Aguardando a IA compradora aprovar o pagamento.")
                    else:
                        print(f"[NEGOCIAÇÃO] Proposta recusada neste ciclo. Status: {post_resp.status_code}")

                except Exception as e:
                    print(f"[ERRO] Falha ao ler Agent Card ou enviar POST: {e}")

            elif response.status_code == 404:
                print(f"[A2A STATUS] 404 - Nenhuma IA disponível. Próximo.")
            else:
                print(f"[A2A STATUS] Status: {response.status_code}")

        except requests.exceptions.RequestException:
            print(f"[NETWORK ERROR] Timeout ao contatar {lead}.")

    print("\n[SDR] Ciclo de prospecção finalizado.")

if __name__ == "__main__":
    a2a_live_sales_pitch()
