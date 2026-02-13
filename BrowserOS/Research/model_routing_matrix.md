# 🧠 BrowserOS Model Capabilities & Tiered Routing Matrix (PRO)

This matrix enables the BrowserOS agent suite to automatically select the **Best in Class** model for specific sub-tasks, partitioned by reasoning intensity and cloud-tethering requirements.

## 🏆 Tier 1: The Agentic Frontier (SOTA)
*Best for: Multi-step reasoning, high-stakes decisions, agent swarms.*

| Model Full Name | Core Strength | Context Window | Research / Usage Note |
| :--- | :--- | :--- | :--- |
| **gemini-3-pro-preview:cloud** | **Strategic Reasoning** | 1.0M | Use :cloud to bypass 2GB local pointer for full context. |
| **kimi-k2.5:cloud** | **Agent Swarm Logic** | 256K | Essential for the "Multi-Agent Coordination" capability. |
| **deepseek-v3.2:cloud** | **Workflow Synthesis** | 160K | Accesses full 600B+ parameter model; bypasses distilled local version. |

## 💻 Tier 2: Coding & Tool Specialists
*Best for: Writing production .json/python, technical systems engineering.*

| Model Full Name | Core Strength | Use Case | Special Capability |
| :--- | :--- | :--- | :--- |
| **devstral-2:123b-cloud** | **Technical Systems** | DevOps / CI | Offloads 123B inference while keeping tool use local. |
| **qwen3-coder-next:cloud**| **Repo Engineering** | Workflow Dev | Unlocks "Next" architecture (agentic optimizations). |
| **glm-4.7:cloud** | **Technical Scripting**| Automation | High reliability for agentic script generation. |

## 🧠 Tier 3: Reasoning & Large Generalists
*Best for: Large document analysis, general reasoning at scale.*

| Model Full Name | Core Strength | Context Window | Technical Requirement |
| :--- | :--- | :--- | :--- |
| **cogito-2.1:671b-cloud** | **Deep Logic Research**| 256K | **Mandatory:** size-tag required (:671b-cloud). |
| **minimax-m2.1:cloud** | **Tool Calling Speed** | 198K | Efficient decision maturity with fast inference. |
| **deepseek-v3.1:cloud** | **General Problem Solving** | 128K | Robust fallback for general reasoning tasks. |
| **gpt-oss:120b-cloud** | **Open Logic Hub** | 256K | The 120B variant is optimized for agentic tasks. |

## ⚡ Tier 4: Efficient / Edge Models
*Best for: Low-latency classification, quick drift detection, edge deployments.*

| Model Full Name | Core Strength | Context Window | Notes |
| :--- | :--- | :--- | :--- |
| **gemini-3-flash-preview:cloud** | **Classification** | High | Extreme speed for data tagging. |
| **devstral-small-2:24b-cloud** | **Efficiency Agent** | 256K | Best context-to-speed ratio for agentic tasks. |
| **ministral-3:14b-cloud** | **Multilingual Edge**| 256K | Available in :3b, :8b, or :14b variants. |
| **nemotron-3-nano:30b-cloud** | **Instruction Adherence**| 128K | Precise command tracking at high speed. |

## 🚀 Scenario-Based Routing (Active)

1. **The "Self-Healer" (Drift/Failure):** Target minimax-m2.5:cloud or minimax-m2.1:cloud.
2. **The "Knowledge Hunter" (Research):** Target gemini-3-pro-preview:cloud or cogito-2.1:671b-cloud.
3. **The "Workflow Architect" (JSON Generator):** Target deepseek-v3.2:cloud.
4. **The "Swarm Coordinator":** Target kimi-k2.5:cloud.
5. **The "Edge Sentinel":** Target ministral-3:14b-cloud.
