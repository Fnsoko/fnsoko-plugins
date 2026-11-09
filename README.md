# Fnsoko Skills

Money skills for your AI, from [Fnsoko Literacy Hub](#). They help you **know your numbers** and climb the **Money Ladder**: budgeting, saving, clearing debt, and growing your money. They're built for Kenyan money (M-Pesa, Fuliza, chamas, SACCOs, HELB) and the **Fnsoko Money Planner**.

> Fnsoko is not a financial adviser. These skills explain options and do the maths. Every decision is yours. They never recommend a specific fund, bank, lender or app.

## What's inside

| Skill | What it does |
|---|---|
| `fnsoko-money-coach` | Reads your M-Pesa or bank statements, builds your money profile, plans your month, reviews it, and helps with your emergency fund, debt payoff, goals and retirement. Always ends with your Money Ladder step and your one next move. |

More skills will be added here. When you update, you get them automatically.

## Step 1: Get the Fnsoko Money Planner

Make your own copy of the planner (Google Sheets): **PLANNER_LINK**

You can also download it as Excel from Google Sheets (File → Download → Microsoft Excel).

## Step 2: Install the skills

### Claude Code (terminal or desktop app)

```
/plugin marketplace add GITHUB_OWNER/fnsoko-skills
/plugin install fnsoko@fnsoko
```

To get the latest version later:

```
/plugin marketplace update fnsoko
```

### Claude.ai (web, desktop and mobile apps)

1. Download this repository: green **Code** button → **Download ZIP**.
2. Unzip it. Inside `skills/`, zip the `fnsoko-money-coach` folder on its own.
3. In Claude, go to **Settings → Capabilities → Skills**, choose **Upload skill**, and pick that zip.
4. Start a chat and say: *"Help me get started with my money."*

### ChatGPT

ChatGPT doesn't install Claude plugins. The skill is plain instructions, so you can still use it:

- Open `skills/fnsoko-money-coach/references/fallback-prompts.md` and copy the prompts into a chat, **or**
- Create a Custom GPT and paste `SKILL.md` into its instructions, uploading the `references/` files as knowledge.

## Privacy

Never share passwords, PINs, one-time codes, ID numbers, or full account or phone numbers with any AI. If your statement PDF is locked, unlock it yourself first. The skill will never ask you for these details.

## Updates

Fnsoko updates these skills over time. Claude Code users: run `/plugin marketplace update fnsoko`. Others: download the ZIP again.
