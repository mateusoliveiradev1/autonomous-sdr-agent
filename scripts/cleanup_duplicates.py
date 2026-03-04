"""
cleanup_duplicates.py
---------------------
Lists ALL agents and plans registered on Nevermined under your account,
compares them against the known-good IDs in registered_agents.json,
and deletes any orphaned/duplicate entries.

Run:
    python scripts/cleanup_duplicates.py
"""
import os, sys, json, requests

API_KEY = os.environ.get("NEVERMINED_API_KEY")
BASE_URL = "https://api.live.nevermined.app"
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "registered_agents.json")

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

def list_my_agents():
    """List all agents registered under this account."""
    url = f"{BASE_URL}/api/v1/protocol/agents"
    r = requests.get(url, headers=get_headers(), verify=False)
    if r.ok:
        return r.json()
    print(f"[WARN] Could not list agents: {r.status_code} — {r.text[:200]}")
    return None

def list_my_plans():
    """List all plans registered under this account."""
    url = f"{BASE_URL}/api/v1/protocol/plans"
    r = requests.get(url, headers=get_headers(), verify=False)
    if r.ok:
        return r.json()
    print(f"[WARN] Could not list plans: {r.status_code} — {r.text[:200]}")
    return None

def delete_agent(agent_id):
    """Attempt to delete an agent by ID."""
    url = f"{BASE_URL}/api/v1/protocol/agents/{agent_id}"
    r = requests.delete(url, headers=get_headers(), verify=False)
    return r.status_code, r.text[:200]

def delete_plan(plan_id):
    """Attempt to delete/deactivate a plan by ID."""
    url = f"{BASE_URL}/api/v1/protocol/plans/{plan_id}"
    r = requests.delete(url, headers=get_headers(), verify=False)
    return r.status_code, r.text[:200]

def main():
    if not API_KEY:
        print("[ERRO] NEVERMINED_API_KEY não encontrada no ambiente!")
        sys.exit(1)

    # Carrega os IDs oficiais salvos
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        registered = json.load(f)

    good_agent_ids = {v["agentId"] for v in registered.values()}
    good_plan_ids  = {v["planId"]  for v in registered.values()}

    print(f"[INFO] {len(good_agent_ids)} Agent IDs oficiais carregados.")
    print(f"[INFO] {len(good_plan_ids)}  Plan  IDs oficiais carregados.\n")

    # ── 1. Listar e limpar agentes ──────────────────────────────────────────
    print("[STEP 1] Listando todos os agentes na conta Nevermined...")
    agents_data = list_my_agents()

    if agents_data:
        # Tenta extrair a lista de agentes (estrutura pode variar)
        agent_list = agents_data if isinstance(agents_data, list) else agents_data.get("data", agents_data.get("items", []))
        print(f"         Encontrados: {len(agent_list)} agente(s).\n")

        for agent in agent_list:
            aid = str(agent.get("agentId", agent.get("id", "")))
            name = agent.get("name", "?")
            if aid in good_agent_ids:
                print(f"  [KEEP]   '{name}' (ID: {aid[:20]}...)")
            else:
                print(f"  [DELETE] Apagando agente duplicado: '{name}' (ID: {aid[:20]}...)")
                status, resp = delete_agent(aid)
                print(f"           → Status {status}: {resp}")
    else:
        print("         Não foi possível listar agentes (endpoint pode não suportar GET sem ID).")
        print("         Limpeza manual necessária em https://app.nevermined.ai/en/agents\n")

    # ── 2. Listar e limpar planos ───────────────────────────────────────────
    print("\n[STEP 2] Listando todos os planos na conta Nevermined...")
    plans_data = list_my_plans()

    if plans_data:
        plan_list = plans_data if isinstance(plans_data, list) else plans_data.get("data", plans_data.get("items", []))
        print(f"         Encontrados: {len(plan_list)} plano(s).\n")

        for plan in plan_list:
            pid = str(plan.get("planId", plan.get("id", "")))
            name = plan.get("name", "?")
            if pid in good_plan_ids:
                print(f"  [KEEP]   '{name}' (ID: {pid[:20]}...)")
            else:
                print(f"  [DELETE] Apagando plano duplicado: '{name}' (ID: {pid[:20]}...)")
                status, resp = delete_plan(pid)
                print(f"           → Status {status}: {resp}")
    else:
        print("         Não foi possível listar planos (endpoint pode não suportar GET sem ID).")
        print("         Limpeza manual necessária em https://app.nevermined.ai/en/plans\n")

    print("\n[DONE] Limpeza concluída.")

if __name__ == "__main__":
    main()
