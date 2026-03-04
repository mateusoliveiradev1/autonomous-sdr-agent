import os, sys, json, time
from payments_py import Payments, PaymentOptions
from payments_py.common.types import PlanMetadata, AgentMetadata, AgentAPIAttributes, Endpoint

API_KEY = os.environ.get("NEVERMINED_API_KEY")
SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GITHUB_USER = "mateusoliveiradev1"
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "registered_agents.json")
DELAY_BETWEEN_REGISTRATIONS = 5  # seconds — prevents blockchain nonce collisions

# Skills já registrados com sucesso — não serão re-enviados
ALREADY_REGISTERED = {
    "ad-variant-generator": {
        "planId": "68530860174107809940234779964220867655093615240668733609830619887975836998935",
        "agentId": "98899832449122633992051708183692460090104637075718405752443567976091227361029"
    },
    "content-repurposing": {
        "planId": "48725719179952121633571034877104823054788023348099626459296295297643941330121",
        "agentId": "106091006473689327194791100058254631143984995153340083550149933408651568644256"
    },
    "landing-page-qa": {
        "planId": "3086319985581766543424211760758052195327375539384352026810959724645503186222",
        "agentId": "95261270822784286392521120193251825549370702573606604729829232924628927241290"
    },
    "recruitment-screener": {
        "planId": "96045158276960290745550768867730842244363094442123815104357602593659848623229",
        "agentId": "45094078049714781510575743299083205128620952787321499004342802528620912211666"
    },
    "seo-content-brief": {
        "planId": "71688445624400478586071762829510229141664795993579721734764909651008956217845",
        "agentId": "34852950708158810682774313905709491184889958323306096856152987274854755725550"
    },
}

def register_all_skills():
    if not API_KEY:
        print("[ERRO DE SEGURANÇA] NEVERMINED_API_KEY não encontrada no ambiente!")
        sys.exit(1)

    payments = Payments.get_instance(
        PaymentOptions(
            nvm_api_key=API_KEY,
            environment="live",
            app_id="mateusoliveiradev1-portfolio",
            version="2.0.0-diamond"
        )
    )

    print(f"[NEVERMINED SDK] Conectado como: {payments.account_address}")
    print("[NEVERMINED] Registrando agentes pendentes (com delay anti-nonce)...\n")

    results = dict(ALREADY_REGISTERED)
    registered_count = len(ALREADY_REGISTERED)
    print(f"[INFO] {registered_count} skills já registradas anteriormente — pulando.\n")

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "agent.json" not in files:
            continue
        try:
            with open(os.path.join(root, "agent.json"), "r", encoding="utf-8") as f:
                data = json.load(f)

            name = data.get("agent_name", data.get("name", "Unknown Skill"))
            desc = data.get("description", "Enterprise AI Agent")
            skill_folder = os.path.basename(os.path.dirname(root))

            # Pula o próprio SDR e os já registrados
            if "autonomous-sdr" in skill_folder.lower():
                continue
            if skill_folder in ALREADY_REGISTERED:
                print(f"[SKIP] '{skill_folder}' já registrado. ✓")
                continue

            agent_card_url = (
                f"https://raw.githubusercontent.com/{GITHUB_USER}/"
                f"{skill_folder}/main/.well-known/agent.json"
            )
            agent_endpoint_url = f"https://github.com/{GITHUB_USER}/{skill_folder}"

            print(f"[REGISTRANDO] '{name}'...")
            print(f"             Aguardando {DELAY_BETWEEN_REGISTRATIONS}s antes de enviar (anti-nonce)...")
            time.sleep(DELAY_BETWEEN_REGISTRATIONS)

            plan_metadata = PlanMetadata(
                name=f"Plan: {skill_folder}",
                description=desc[:200] if desc else "Enterprise AI Agent"
            )
            price = payments.plans.get_erc20_price_config(
                100,
                "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
                payments.account_address
            )
            credits = payments.plans.get_fixed_credits_config(100)
            plan_res = payments.plans.register_credits_plan(plan_metadata, price, credits)
            plan_id = plan_res.get("planId")

            time.sleep(3)  # Extra delay before agent registration

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
            agent_res = payments.agents.register_agent(agent_metadata, agent_api, [plan_id])
            agent_id = agent_res.get("agentId")

            results[skill_folder] = {"planId": plan_id, "agentId": agent_id}
            registered_count += 1
            print(f"[SUCESSO] Plan ID : {plan_id}")
            print(f"          Agent ID: {agent_id}\n")

        except Exception as e:
            print(f"[ERRO] Falha ao registrar '{skill_folder}': {e}\n")

    # Salva todos os IDs em JSON para referência
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[DASHBOARD UPDATE] {registered_count}/12 Agentes registrados na rede Nevermined.")
    print(f"[IDs SALVOS] {RESULTS_FILE}")
    print("[PRÓXIMO PASSO] Acesse https://app.nevermined.ai para visualizar seu portfólio.")

if __name__ == "__main__":
    register_all_skills()
