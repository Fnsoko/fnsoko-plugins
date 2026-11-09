# Fnsoko Money Skills

Money skills for your AI, from Fnsoko Literacy Hub. They help you **know your numbers** and climb the **Money Ladder**: budgeting, saving, clearing debt, and growing your money. They're built for Kenyan money (M-Pesa, Fuliza, chamas, SACCOs, HELB) and the **Fnsoko Money Planner**.

> Fnsoko is not a financial adviser. These skills explain options and do the maths. Every decision is yours. They never recommend a specific fund, bank, lender or app.

## What's inside

```
fnsoko-plugins/                       ← marketplace "fnsoko"
└── plugins/
    └── fnsoko-money-skills/          ← plugin "Fnsoko Money Skills"
        └── skills/
            └── fnsoko-money-coach/   ← skill
```

| Skill | What it does |
|---|---|
| `fnsoko-money-coach` | Reads your M-Pesa or bank statements, builds your money profile, plans and reviews your month, and helps with your emergency fund, debt payoff, goals and retirement. Always ends with your Money Ladder step and your one next move. |

New skills get added to Fnsoko Money Skills over time.

## Step 1: Get the Fnsoko Money Planner

**[Make your own copy of the Fnsoko Money Planner](https://docs.google.com/spreadsheets/d/10hyAqW-r_kK5tjseAC15GwyFMFDxmQzH9o7JRPFsaSw/copy)** (Google Sheets). To use it in Excel instead: File → Download → Microsoft Excel.

## Step 2: Install the skills

### Claude Code

```
/plugin marketplace add Fnsoko/fnsoko-plugins
/plugin install fnsoko-money-skills@fnsoko
```

Get updates later with:

```
/plugin marketplace update fnsoko
```

### Claude.ai (web, desktop and mobile apps)

1. Download [`fnsoko-money-coach.zip`](https://github.com/Fnsoko/fnsoko-plugins/releases/latest/download/fnsoko-money-coach.zip).
2. In Claude, open **Customize → Skills** (on older versions: **Settings → Capabilities → Skills**), upload a skill, and pick the zip. Don't unzip it first.
3. Start a chat and say: *"Help me get started with my money."*

### ChatGPT

ChatGPT supports the same open skill format ([Agent Skills](https://agentskills.io)).

1. Download [`fnsoko-money-coach.zip`](https://github.com/Fnsoko/fnsoko-plugins/releases/latest/download/fnsoko-money-coach.zip).
2. In ChatGPT, open **Skills → Create → Upload from your computer**, and pick the zip. On some workspace plans, an admin has to turn Skills on first.

No Skills option? Use the copy-paste prompts in [`fallback-prompts.md`](plugins/fnsoko-money-skills/skills/fnsoko-money-coach/references/fallback-prompts.md) instead.

### Other AI tools

Any tool that supports Agent Skills can use the `plugins/fnsoko-money-skills/skills/fnsoko-money-coach` folder as it is.

## Automate your money messages (optional)

Your phone can send every transaction SMS (M-Pesa, your bank, Airtel Money…) straight into your planner. Claude then sorts them into your Money Log on a daily or weekly schedule and sends you a short summary.

1. Copy the **[SMS-ready Fnsoko Money Planner](https://docs.google.com/spreadsheets/d/1Fb0n-PXVEvoOjDiSHcSHXy6FjuaA6O8pRQlEPu_XDU8/copy)**. It includes the SMS Inbox tab and its script.
2. In your copy: **Extensions → Apps Script → Deploy → New deployment → Web app** (Execute as Me, Who has access Anyone). Copy the link ending in `/exec`, and keep it private.
3. **iPhone:** add the **[Fnsoko SMS Inbox Automation shortcut](https://www.icloud.com/shortcuts/44261bde5e94486da4ed7bfb3a656878)** and paste your `/exec` link when asked. Then make one automation per keyword: **Automation → Message → Message Contains** `M-PESA` (another for your bank's name) → Run Immediately → Run Shortcut.
   **Android:** coming soon.
4. In Claude, turn on the **Google Sheets** and **Gmail** connectors and say: *"Help me set up my SMS inbox."* The skill walks you through the rest and offers to schedule it.

## Privacy

Never share passwords, PINs, one-time codes, ID numbers, or full account or phone numbers with any AI. If your statement PDF is locked, unlock it yourself first. The skill will never ask you for these.

## Updates

- **Claude Code:** run `/plugin marketplace update fnsoko`.
- **Claude.ai and ChatGPT:** download the newest zip and upload it again.
