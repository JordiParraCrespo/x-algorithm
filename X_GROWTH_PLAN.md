# X Growth Plan — AI Vibe-Coding Agent Orchestration Consultancy

> Grounded in how the actual X "For You" algorithm in this repo ranks content
> (see `home-mixer/scorers/weighted_scorer.rs`, `oon_scorer.rs`,
> `author_diversity_scorer.rs`, and the `grox/` content-understanding
> classifiers). This is not generic advice — every tactic below maps to a
> mechanism in the code.

---

## 0. Your situation

- **Business:** AI vibe-coding agent-orchestration consultancy.
- **Two offers:**
  1. **Build-for-self** — you ship your own products when you have bandwidth.
  2. **Build-for-others** — done-for-you / done-with-you product launches for clients.
- **Goal of X:** turn attention into (a) inbound consulting leads, (b) an audience that compounds for every product you launch (yours and clients').

The beautiful thing: your two offers *are* your content engine. Building in
public = content. Launching for clients = case studies. You never run out of
material.

---

## 1. How the algorithm actually decides who sees you

X no longer uses hand-engineered features. A Grok-based transformer reads each
user's **engagement history** and predicts a set of action probabilities for
your post; a weighted sum of those probabilities is your score
(`weighted_scorer.rs › compute_weighted_score`). Here's what the code predicts
and weights, and what it means for you.

### Positive signals the model predicts (and you should engineer for)
From `candidate.rs › PhoenixScores` and `weighted_scorer.rs`:

| Predicted action | What it rewards | Your lever |
|---|---|---|
| `favorite` (like) | baseline approval | easy, low value alone |
| `reply` | conversation | **ask questions, take stances** |
| `retweet` / `quote` | endorsement + spread | make posts *quotable* (one strong claim) |
| `share`, `share_via_dm`, `share_via_copy_link` | private sharing | "send this to a dev who…" / save-worthy utility |
| `dwell_score` + `dwell_time` (continuous) | time spent reading | **threads, carousels, dense value** |
| `click`, `quoted_click` | curiosity | strong hook first line |
| `profile_click` | "who is this?" | **this is the follower funnel** |
| `follow_author` | direct follow intent | clear niche + a reason to follow |
| `vqv` (video quality view) | video watched | only counts for video > min duration (`vqv_weight_eligibility`) → **post real video** |
| `photo_expand` | image engagement | use images/diagrams |

### Negative signals that *subtract* from your score
`not_interested`, `block_author`, `mute_author`, `report` all carry negative
weights (`weighted_scorer.rs`). One mistake category: rage-bait that makes
people mute you nets short-term replies but poisons your long-term score. Avoid
content that triggers these.

### Three structural mechanics that change strategy

1. **Out-of-network penalty (`oon_scorer.rs`).** Posts shown to people who
   *don't* follow you are multiplied by `OON_WEIGHT_FACTOR` (a discount). To
   escape your follower bubble and reach new people, your post must score high
   *enough to overcome that discount* — which only happens when your existing
   audience engages fast and hard. **Early engagement velocity from your
   network is the gate to viral OON reach.** Implication: who follows you and
   whether they reliably engage matters more than raw count.

2. **Author diversity decay (`author_diversity_scorer.rs`).** Within a single
   feed, your 2nd, 3rd, 4th post is multiplied down by
   `decay^position` toward a floor. Flooding the timeline has sharply
   diminishing returns *per viewer*. **Space your posts out; don't dump.**

3. **LLM quality + spam gates (`grox/`).**
   - `banger_initial_screen.py` runs a vision-LLM that assigns a
     `quality_score`; below ~`0.4` it's screened as not-a-banger. Low-effort
     posts are now judged by a model, not a heuristic. **Quality is enforced.**
   - `spam.py` has a dedicated **low-follower spam classifier**
     (`SpamSystemLowFollower`). New/small accounts get *extra* spam scrutiny.
     Early on, avoid spam patterns: mass identical replies, link-only posts,
     follow-for-follow, copypasta.

### The one-paragraph takeaway
Win by producing posts that earn **replies, reposts, shares, profile clicks,
and dwell time** from an audience that engages *fast*, while never triggering
*not-interested / mute / block*, and clearing the LLM quality bar. Video and
images get extra eligible weight. Don't spam (especially while small), and
space your posts so author-diversity decay doesn't eat you.

---

## 2. Positioning & profile (the conversion surface)

`profile_click` and `follow_author` are explicitly predicted — so the moment
someone hits your profile, it must convert. Optimize it before you post more.

- **Bio (one job):** who you help + proof + offer. Template:
  `I build & launch AI agent-orchestration products. Shipped [X]. DMs open for builds.`
- **Pinned post:** your single best "here's what I do + proof" thread or demo video.
- **Handle/name:** include "AI agents" or "vibe coding" so search + the model
  associate you with the niche (the transformer routes you to users who engage
  with that topic cluster).
- **Header image:** show a product/result, not a stock graphic.
- **Link:** to a one-page site with the two offers and a booking link.

---

## 3. Content pillars (your engagement signature)

The model clusters you by *who engages with you*. A tight, consistent topic
makes it route your posts to the right audience. Pick 3–4 pillars and stay in
lane ~80% of the time.

1. **Build-in-public (your own products).** Daily/near-daily progress, agent
   orchestration decisions, what broke, what shipped. → dwell + replies + follows.
2. **Teach the craft.** How to orchestrate agents, prompt patterns, eval
   loops, cost control, tool design. Concrete, reproducible. → shares + saves
   (`share_via_copy_link`, `share_via_dm`).
3. **Client launches / case studies.** "Took [client] from idea → launched in
   N days." Results, screenshots, metrics. → repost + profile clicks → leads.
4. **Takes & teardowns.** Thoughtful opinions on agent frameworks, new model
   releases, vibe-coding workflows. Stance-driven → replies (high weight).

---

## 4. Format playbook (mapped to weighted signals)

| Format | Signal it maximizes | Cadence |
|---|---|---|
| **Demo video** (15–60s, real screen recording) | `vqv` eligible weight, dwell | 2–3×/week |
| **Thread** (hook + 5–9 steps + payoff) | dwell_time, share, repost | 2–3×/week |
| **Single strong claim** (one quotable line) | quote, repost | daily |
| **Build-log w/ screenshot/diagram** | photo_expand, dwell, profile_click | daily-ish |
| **Question / "how would you…"** | reply (high weight) | a few/week |
| **Case-study carousel** (before→after) | dwell, share, profile_click → leads | weekly |

**Hooks matter most** — the first line drives `click`, dwell, and whether
anyone engages in the first minutes (which feeds the OON gate). Lead with the
result or the tension, not the setup.

---

## 5. The engagement-velocity engine (beating the OON discount)

Because OON reach is gated by early engagement, build a system for fast
first-minute traction — *organically, not spammily* (the spam classifier is
watching small accounts):

- **Be active 15–20 min before and after you post.** Reply to others first so
  the conversation is warm.
- **Build genuine relationships with 20–50 peers** in the AI-agent space.
  Reply with substance on their posts daily. Real reply communities → reliable
  early engagement without tripping spam signals. Quality replies also earn you
  `profile_click`s from *their* audience (OON exposure you didn't pay for).
- **End posts with a low-friction reply prompt** ("what's your agent stack?").
- **Make posts DM-shareable** — "send this to someone vibe-coding" — because
  `share_via_dm` and `share_via_copy_link` are separately weighted.
- **Never** mass-reply identical text or drop bare links early on.

---

## 6. Posting cadence

- **1–3 posts/day, spaced 3+ hours apart** (author-diversity decay punishes dumps).
- **Replies: 5–15/day** of real substance (your #1 small-account growth lever —
  borrowed reach + profile clicks).
- **Time posts to your audience's active window** (dev/AI audience: weekday
  mornings + early evenings, your timezone first). Recency matters — the feed
  drops old posts (`AgeFilter`), so freshness during active hours wins.
- **1 "anchor" piece/week** (big thread, demo, or case study) you can promote
  and repurpose.

---

## 7. The funnel: attention → consulting revenue

```
Reply game + posts  →  profile clicks  →  follow  →  DMs / link click  →  call  →  client
                    \                                                  /
                     →  build-in-public credibility ──────────────────
```

- **Soft CTAs**, not hard sells. "Building this for a client, DMs open if you
  want one" beats "HIRE ME".
- **Pin a lead magnet:** a free teardown, a template repo, or a checklist for
  "launching an AI agent product." Captures the build-for-others audience.
- **Case studies are your closers.** Each client launch = a thread = social
  proof = the next client. Get permission to share results.
- **Two audiences, one feed:** founders/teams who want you to *build for them*,
  and builders who follow your *own* products. Pillars 1–2 serve builders;
  pillars 3 serves buyers. Both grow the same follower graph.

---

## 8. 90-day roadmap

**Weeks 1–2 — Foundation**
- Rewrite bio, pinned post, header, link-in-bio with the two offers.
- List 30–50 target accounts in the AI-agent niche; start daily substantive replies.
- Ship 1 post/day to find your voice. Establish the 3–4 pillars.

**Weeks 3–6 — Consistency & signal**
- 2 posts/day + 10 replies/day. Start one build-in-public thread of your own product.
- Post your first demo video. Test 5–10 hook styles; double down on what gets dwell/reposts.
- Land/announce first (even small/free) client launch → write the case study.

**Weeks 7–12 — Compounding & monetizing**
- 2–3 posts/day, 1 anchor/week (thread or demo).
- Publish 2–3 client case studies. Add a lead magnet + booking link.
- Open DMs explicitly for builds; convert profile traffic to calls.
- Review metrics monthly (below) and prune pillars/formats that underperform.

---

## 9. Metrics to track (proxies for the weighted signals)

You can't see the model's scores, but these public metrics are direct proxies:

| Metric | Maps to | Target trend |
|---|---|---|
| Replies per post | `reply` (high weight) | up |
| Reposts + quotes | `retweet`, `quote` | up |
| Bookmarks/shares | `share*` (DM/copy-link) | up |
| **Profile clicks / impressions** | `profile_click` → follows | **watch closely** |
| Follows per post | `follow_author` | up |
| Avg. watch time (video) | `vqv`, dwell | up |
| "Not interested"/mutes (if visible) | negative weights | **near zero** |
| DMs / call bookings | revenue | up |

Rule: optimize for **reposts + replies + profile clicks**, not likes. Likes are
the lowest-leverage positive signal.

---

## 10. Don't-do list (things the code will punish)

- ❌ Posting 6× in an hour → author-diversity decay wastes the extra posts.
- ❌ Link-only or copypasta posts while small → low-follower spam classifier.
- ❌ Rage-bait that earns mutes/blocks → negative weights tank your score.
- ❌ Low-effort one-liners with no hook → may miss the LLM quality bar (`banger`).
- ❌ Chasing likes → lowest-weighted signal; you'll optimize the wrong thing.
- ❌ Going broad/off-niche → confuses the model's audience routing.

---

### TL;DR
Tight AI-agent niche. Profile that converts. 1–3 spaced, high-quality posts/day
(video + threads + quotable claims) plus 10 substantive replies/day. Engineer
**replies, reposts, shares, profile clicks, dwell** from a warm network in the
first minutes to beat the out-of-network discount. Build in public for
audience, publish client case studies for leads. Never spam, never bait mutes.
