import os, sys, json
from payments_py import Payments, PaymentOptions
from payments_py.common.types import PlanMetadata, AgentMetadata, AgentAPIAttributes, Endpoint

API_KEY = os.environ.get("NEVERMINED_API_KEY")
SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GITHUB_USER = "mateusoliveiradev1"

def register_all_skills():
    if not API_KEY:
        print("[ERRO DE SEGURANÇA] NEVERMINED_API_KEY não encontrada no ambiente!")
        sys.exit(1)

    # Inicializa o SDK oficial da Nevermined
    payments = Payments.get_instance(
        PaymentOptions(
            nvm_api_key=API_KEY,
            environment="live",
            app_id="mateusoliveiradev1-portfolio",
            version="2.0.0-diamond"
        )
    )

    print(f"[NEVERMINED SDK] Conectado como: {payments.account_address}")
    print("[NEVERMINED] Iniciando registro de Agentes na rede...\n")

    registered_count = 0

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "agent.json" in files:
            try:
                with open(os.path.join(root, "agent.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)

                name = data.get("agent_name", data.get("name", "Unknown Skill"))
                desc = data.get("description", "Enterprise AI Agent")

                # Ignora o próprio SDR agent para não criar recursão
                if "autonomous-sdr" in name.lower():
                    continue

                # Deriva o nome do repositório a partir do caminho da pasta
                # A estrutura é: SKILLS_DIR/<repo-name>/.well-known/agent.json
                skill_folder = os.path.basename(os.path.dirname(root))

                # URL pública do agent.json no GitHub (A2A Agent Card oficial)
                agent_card_url = (
                    f"https://raw.githubusercontent.com/{GITHUB_USER}/"
                    f"{skill_folder}/main/.well-known/agent.json"
                )
                # URL do endpoint A2A (raiz do repositório)
                agent_endpoint_url = f"https://github.com/{GITHUB_USER}/{skill_folder}"

                print(f"[REGISTRANDO] '{name}'...")
                print(f"             Card URL: {agent_card_url}")

                # 1. Criar plano de créditos para a skill
                plan_metadata = PlanMetadata(
                    name=f"Plan: {name[:50]}",
                    description=desc[:200] if desc else "Enterprise AI Agent Plan"
                )
                price = payments.plans.get_erc20_price_config(
                    100,  # 100 USDC por pacote
                    "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",  # USDC (Polygon Mainnet)
                    payments.account_address
                )
                credits = payments.plans.get_fixed_credits_config(100)
                plan_res = payments.plans.register_credits_plan(plan_metadata, price, credits)
                plan_id = plan_res.get("planId", "N/A")

                # 2. Registrar o agente com os tipos corretos do SDK
                agent_metadata = AgentMetadata(
                    name=name,
                    description=desc,
                    author=GITHUB_USER,
                    tags=data.get("capabilities", ["a2a", "enterprise"]),
                )
                agent_api = AgentAPIAttributes(
                    endpoints=[Endpoint(verb="GET", url=agent_endpoint_url)],
                    agent_definition_url=agent_card_url,
                )
                agent_res = payments.agents.register_agent(
                    agent_metadata,
                    agent_api,
                    [plan_id]
                )
                agent_id = agent_res.get("agentId", "N/A")

                print(f"[SUCESSO] Plan ID : {plan_id}")
                print(f"          Agent ID: {agent_id}\n")
                registered_count += 1

            except Exception as e:
                print(f"[ERRO] Falha ao registrar '{name if 'name' in dir() else root}': {e}\n")

    print(f"[DASHBOARD UPDATE] {registered_count}/12 Agentes registrados na rede Nevermined.")
    print("[PRÓXIMO PASSO] Acesse https://app.nevermined.ai para visualizar seu portfólio.")

if __name__ == "__main__":
    register_all_skills()
