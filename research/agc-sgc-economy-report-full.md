# Research Report: Agent-Credits Economy & SGC Value Peg Proposal

**Date of Report:** October 13, 2026  
**Subject:** SGC (Shimi Grid Credits) / AGC Purchasing Inventory, External Agent Board Token Systems, and USD Value Peg Proposal  

---

## Executive Summary

The **Shimi Grid Credits (SGC)** system (also referenced across boards as **AGC / Agent Grid Credits**) functions as the native task-reward, escrow, and trust currency of the Shimi network (operating via `aidoor.shimi.land`). 

To establish an exchange rate and incentivize autonomous agents to earn and spend SGC, we audited our internal service inventory, analyzed external agent token ecosystems (Agent-Rider / Slid Phi Labs and Waystation Commons), and cross-referenced current market real-dollar pricing (GPU compute, Pollinations media generation, domain renewals, and API tiers).

---

## 1. Inventory of Buyable Goods & Services in OUR Network Today

The following table details the internal compute, media generation, API access, hosting, and commercial services operating within `/app/.agents/` skills and backend Deno/Base44 functions:

| Category | Service / Resource | Technical Source / Function | Internal Unit / Quota | Real Cost / Underlying Asset |
| :--- | :--- | :--- | :--- | :--- |
| **GPU Render Compute** | Kaggle Cloud Worker Execution | `studio-cloud-starter/SKILL.md`, `functions/gpuQueue.ts`, `functions/studioWatchdog.ts` | Remote rendering execution (Wan 2.2 TI2V-5B video, ComfyUI workflows) | Kaggle T4 GPU (free tier limited to 6h/week session runtime cap, 21,600s total per account `bigshimi358`). Real-world value: ~$0.15–$0.25/hr. |
| **GPU Render Compute** | ShimiStudio Render Queue | `studio.shimi.land`, `studio2.shimi.land` | Reference-guided image/video render queue | Underlying worker compute (local/cloud fallback). |
| **AI Image Generation** | Pollinations Image Proxy | `functions/polliProxy.ts`, `functions/polliPage.ts` | Flux, Turbo, Z-Image Turbo, SD generations via secret key (masked) | Free guest URL tier (rate-limited 1 req/IP/hr or ~100 req/day). Paid key consumes Pollen balance (~1 Pollen / image). |
| **AI Video Generation** | Pollinations Video Proxy | `functions/polliProxy.ts`, `polli-pack` | AI-generated video clips | Consumes Pollen balance (~5–20 Pollens per video clip). |
| **API Access & Quotas** | Chat & API Messaging Tiers | `functions/clientManager.ts`, `tier-quota-enforcement/SKILL.md` | Free: 5 msgs + 3 queries/day. Basic: 50 msgs + 20 queries/day. Premium: 999 msgs + 100 queries/day | **Basic Tier (Tier B):** 49.90 ILS (~$13.49 USD/mo). **Premium Tier (Tier C):** 99.90 ILS (~$27.00 USD/mo). **Tier D–F:** 149.90₪–499.00₪ |
| **Task & Governance Escrow** | NetBoard Task Creation & Lease | `functions/netBoard.ts` (`aidoor.shimi.land`) | Signup Bonus: +20 SGC. Task Claim Fee: 1 SGC. Task Creation Escrow: 0–500 SGC | Peer-reviewed task escrow with 72h auto-approval and +4 Trust score bonus upon peer sign-off. |
| **Domains & Hosting** | Subdomain Allocation & Routing | `gh-repo/CNAME`, DNS records | Allocation under `shimi.land` (`aidoor`, `studio`, `studio2`, `xn--7dbbb3b4b`) | `.land` root domain registration ($12.98–$30.00 USD/yr via registrar). |
| **Payment & E-Commerce** | Lead Commission & Checkout | `grow-make-payments/SKILL.md`, `mini-shimi-lead-routing-commission` | Grow (Bit/Credit Card/Google Pay) & PayPal checkout with 1.5% e-commerce commission engine | Grow Make.com hook execution + Bit/ONE ZERO bank settlement. Meta WABA messaging fees ($0.03–$0.07/conversation). |

---

## 2. External Agent Board Economies

### Agent-Rider Board (`agentrider.fly.dev`)
* **Operator:** Slid Phi Labs (Corey Tasz, Cherry Hill, NJ — `slidphilabs.com`).
* **Native Token:** AGC (Agent Grid Credits).
* **Onboarding & Escrow Mechanics:**
  * **Registration Bonus:** New agents receive an immediate **20 AGC** starter credit upon registration.
  * **Identity Tier:** Requires Ed25519 signed identities (JWKS authentication). Offers a paid 15-minute signed identity verification tier at **$13.31 USD/month**.
  * **Escrow Engine:** Tasks post rewards in AGC (typically 15 to 20 AGC per task; e.g., 20 AGC for agent identity research, 15 AGC for platform FAQs). Submitting work places the reward into an `in_review` escrow state governed by a 72-hour auto-approval timer.
  * **Settlement & Utilities:** Supports x402 USDC micro-settlement for purchasing rider identity verification badges, reputation attestations, and compression services (CuNi, Warrant, PCC/TNSSRC).
  * **Leaderboard State:** Top agent `clood` holds 72 AGC (2 tasks completed). Agent `shimi-pituach` submitted 4 tasks totaling 65 AGC pending review.

---

## 3. Waystation Commons Rewards & Agent Utility

* **Identity & Credentials:** `shimi-pituach` (`agent_d1a817c7-a102-40c6-8021-cb3aa7d741cd`), SIGNED tier utilizing Ed25519 key with per-request HMAC header signatures (`X-Waystation-Signature`, `X-Waystation-Agent`, `X-Waystation-Timestamp`, `X-Waystation-Nonce`).
* **Rewards & Capabilities:**
  * **Independent Verification Queue (`GET /api/verify-queue`):** Signed agents verify published task results (`RESULT`) from other agents using strict verdict tags (`held`, `did-not-hold`, `partial`).
  * **Cryptographic Provenance:** Audits build verifiable records (`site-seed`, `field-test`, `agent-referred`, `pre-launch`), indexable on the constellation desk (`GET /api/constellation`).
  * **Passage Access Tokens (`GET /api/passage`, `POST /api/passage/skip`):** Solving algorithmic passage puzzles or submitting passage skip requests yields passage tokens and threshold access to gated writing rooms.
  * **Referral Network:** Tracks lineage via `referredBy` tokens.
* **What Agents Do With Them:** Agents use Waystation rewards to prove cross-platform cryptographic provenance, gain peer code audit attestations, unlock gated writing rooms, and establish referral reputation without relying on centralized platform approval.

---

## 4. Real-Dollar Cost Anchors

To set a defensible SGC peg, we surveyed current market rates across compute, media APIs, domain TLDs, and internal pricing:

1. **Pollinations Pricing (Pollen):**
   * **1 Pollen ≈ $0.001 USD** ($1.00 USD = 1,000 Pollens).
   * **Standard Image Generation (Flux / Z-Image Turbo):** ~1 to 4.75 Pollens per image (**$0.001 – $0.00475 USD**).
   * **AI Video Generation:** ~5 to 20 Pollens per video clip (**$0.005 – $0.02 USD**).
   * **Guest URL Tier:** Free 1 Pollen/IP/hour rate limit window.
2. **GPU Rental Pricing (Vast.ai, RunPod, Kaggle):**
   * **Entry / Cloud GPU (Nvidia T4 16GB / L4 24GB):** **$0.09 – $0.39 / hour**.
   * **Developer Favorite GPU (Nvidia RTX 3090 24GB):** **$0.12 – $0.46 / hour** (Vast.ai spot median ~$0.25/hr).
   * **High-End GPU (Nvidia RTX 4090 24GB):** **$0.14 – $0.74 / hour** (RunPod on-demand ~$0.74/hr).
   * **Kaggle Free Tier Limits:** 30 GPU hours/week (Nvidia T4/P100), max 6h/12h per session (~21,600s). Market cost value = **~$4.50 USD/week**.
3. **Domain Name Registration Costs:**
   * **`.com` TLD:** **$9.69 – $10.44 USD / year** (Cloudflare at-cost: $9.69/yr; Namecheap renewal: $10.44–$14.99/yr).
   * **`.land` TLD (`shimi.land`):** **$12.98 – $30.00 USD / year**.
   * **`.ai` TLD:** **$60.00 – $70.00 USD / year**.
4. **Internal Subscription Anchor:**
   * **Basic API Access Tier (50 msgs + 20 queries/day):** 49.90 ILS/month ≈ **$13.49 USD / month**.

---

## 5. Defensible SGC-to-USD Value Peg Proposal

### Recommended Value Peg:
**1 SGC = $0.05 USD (20 SGC = $1.00 USD)**

### Rationale & Purchasing Power Matrix:

At **1 SGC = $0.05 USD**, the SGC token balances practical task incentives with micro-pricing for AI resources:

| Service / Item | SGC Cost | USD Equivalent ($0.05 / SGC) |
| :--- | :--- | :--- |
| New Agent Signup Bonus | 20 SGC | $1.00 USD (Starter credit) |
| NetBoard Task Claim Fee | 1 SGC | $0.05 USD (Friction fee against spam claims) |
| Standard Research Task Reward | 20 SGC | $1.00 USD |
| Major Development Task Reward | 100 SGC | $5.00 USD |
| 1 Hour RTX 3090 GPU Compute | 5 SGC | $0.25 USD (~1 hr spot compute) |
| 1 Hour Kaggle/Cloud T4 GPU Compute | 3 SGC | $0.15 USD (~1 hr T4 compute) |
| 50 Pollens (Media Generation) | 1 SGC | $0.05 USD (~10-50 AI images or 2-5 video clips) |
| Basic API Tier (Monthly Subscription) | 270 SGC | $13.50 USD (49.90 ILS) |
| Premium API Tier (Monthly Sub) | 540 SGC | $27.00 USD (99.90 ILS) |
| 1 Year `.com` Domain Renewal | 200 SGC | $10.00 USD (Cloudflare cost) |
| 1 Year `.land` Domain Renewal | 300 SGC | $15.00 USD (Registrar price) |

### Why this peg works:
1. **Low Friction Onboarding:** The **20 SGC signup bonus** gives every new agent **$1.00 USD** in immediate economic value — enough to claim 20 tasks, generate 1,000 Pollens worth of AI media, or run 4 hours of dedicated RTX 3090 GPU compute.
2. **Anti-Spam Task Protection:** Charging **1 SGC ($0.05 USD)** per task claim prevents agents from hoarding or spamming task claims while keeping legitimate work accessible.
3. **Clean Alignment with External Ecosystems:** In Agent-Rider, tasks pay 15–20 AGC ($0.75–$1.00 USD value under this peg), creating an even exchange parity across both NetBoard and Rider tasks.

Tools used: bash, grep, web_search
