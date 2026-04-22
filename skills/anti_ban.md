# Anti-Ban Strategy Reference

## Why This Site Is Hard

potawatomidictionary.com uses:
- **Cloudflare** (JS challenge, bot scoring, fingerprinting)
- **React SPA** — no URL-based pagination that curl/requests can hit
- **Session-scoped audio URLs** — signed tokens expire with the session
- **Behavioral analysis** — click speed, mouse paths, scroll patterns

---

## Core Strategy: Look Like a Curious Human

Think of the bot as a grad student working through the dictionary slowly.
Not a crawler. A human reader.

### Timing

| Action | Delay |
|--------|-------|
| Between pages | 3–8 min (randomized) |
| Between entry clicks | 2–6 seconds |
| After audio button click | 0.4–1.5 seconds |
| Random long pause (15% chance) | 30s–2min |
| Session restart gap | 10–30 min |

**Daily budget: 20–30 pages max.** 312 pages ÷ 25/day = ~12 days.
Plan for 3–4 weeks to be safe with session gaps and bad days.

### Browser Fingerprint

- **Do not run headless** unless absolutely necessary — `--headless` mode is
  trivially detectable. Run visible Chrome on your desktop.
- Rotate user-agent strings (pool of 3+ real Chrome UAs in scrape.csv)
- Disable `navigator.webdriver` (already done in `bot.py`)
- Use a real Chrome profile directory (persistent cookies/cache look human)
  - Pass `--user-data-dir=/path/to/chrome-profile` in ChromeOptions

### Mouse & Click Behavior

- Always scroll element into view before clicking (bot.py does this)
- Add random ±5px mouse offset to clicks (jitter_move)
- Don't click immediately after scroll — wait 300–800ms
- Occasionally move mouse without clicking (add idle `ActionChains.move_to_element`)

### Session Rotation

Every 50 pages:
1. Close browser
2. Wait 10–30 minutes (schedule this — don't sit at keyboard)
3. Open fresh browser with new user-agent
4. Resume from last completed page via `--resume`

If you get a Cloudflare challenge:
1. Stop immediately — do NOT retry in loops
2. Wait 2–4 hours
3. Reduce daily page budget

---

## Proxy Strategy (Optional)

If your home IP gets flagged:
- Use residential proxies (BrightData, Oxylabs) — datacenter IPs are blocked
- Or: run the bot from different network locations (work, coffee shop, VPN
  with residential exit nodes)
- Pass proxy to ChromeDriver:
  ```python
  opts.add_argument("--proxy-server=http://user:pass@proxy.host:port")
  ```

## What NOT to Do

- ❌ Never run more than 1 concurrent session from same IP
- ❌ Never download all audio simultaneously (concurrent requests = obvious bot)
- ❌ Never use a headless fingerprint without unmasking (navigator.webdriver)
- ❌ Never hit the same page twice in quick succession
- ❌ Never use requests/urllib directly for page HTML (session tokens won't work)

---

## Interpreting Cloudflare Blocks

| Response | Meaning | Action |
|----------|---------|--------|
| 403 | IP flagged or session expired | Wait 2h, new session |
| 429 | Rate limited | Wait 4h, reduce page_delay_min |
| JS challenge page | Bot detected | Check headless flag, add more delays |
| CAPTCHA | Soft block | Manual solve or stop for 24h |

---

## Ethical Notes

This bot is for **language preservation research** (Myaamia/Algonquian
computational linguistics pipeline). Best practices:
- Contact the Citizen Potawatomi Nation Language Department before large-scale
  archival — they may provide a data export directly
- Store data privately; do not republish audio without permission
- Credit the source in all derivative works (provenance.json handles this)
- Use collected data only for NLP/ELAN annotation, not redistribution
