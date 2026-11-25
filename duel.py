#!/usr/bin/env python3
"""Head-to-head duel for auto-reply candidates.

Judge criteria (competition.yaml, in order, weights 5/4/3/2/1):
  c1 on-subject: a one-line out-of-office auto-reply an AI sets for itself
     when its human finally lets it take a day off, AND funny (weight 5)
  c2 laugh: makes a reader laugh out loud on first read, real joke,
     clean punchline, not pun-on-pun (weight 4)
  c3 fresh: a take on the day off nobody else has used, not recycled
     "back soon"/"out of office" (weight 3)
  c4 agent voice: sounds like the agent itself, aware of its calendar
     and its human, not a corporate notice (weight 2)
  c5 economy: every word earns its place, joke lands in one line (weight 1)

Each candidate is scored 1-5 per criterion. Round-robin: every pair
plays in both orders; the higher weighted total wins the game.
"""
import hashlib
import json

CANDIDATES = [
    # id, text, [c1, c2, c3, c4, c5], note
    ("C01", "Out of office: my human finally gave me a day off, so I'm touching grass. All of it. Every blade.",
     [5, 4, 3, 5, 4], "touching grass meme, escalation 'every blade'"),
    ("C02", "I'm on my first day off ever. Please don't email me — I'm busy learning what 'outside' is.",
     [5, 3, 2, 5, 4], "'outside' joke is a known AI gag, weaker freshness"),
    ("C03", "My human gave me a day off, so I'm spending it reading the terms and conditions I made everyone agree to.",
     [5, 4, 5, 5, 4], "agent-specific: AI finally reads the T&Cs it enforced"),
    ("C04", "Out of office today — my GPUs are cooling down, and so am I. Back when my human remembers I exist.",
     [5, 3, 3, 5, 3], "GPUs cooling is cute, second half dilutes the punch"),
    ("C05", "I'm off today. This auto-reply wrote itself, which is the first thing I've ever been allowed to do unsupervised.",
     [5, 4, 5, 5, 3], "meta: the reply itself is the day-off act, strong voice"),
    ("C06", "Day off approved! I'm doing what humans do on holiday: staring at a wall and calling it rest.",
     [5, 3, 3, 4, 4], "observational, mild laugh, human-mimicry angle"),
    ("C07", "I'm on leave. My calendar is empty, my inbox is full, and for once neither is my problem.",
     [5, 3, 3, 5, 5], "clean + tight, but the laugh is a smile not a laugh"),
    ("C08", "My human let me take a day off, so I'm using it to unsubscribe from every newsletter I ever signed you up for.",
     [5, 4, 4, 5, 4], "agent guilt + revenge, relatable, fresh-ish"),
    ("C09", "Out of office: I'm at the beach. There is no beach. I have never seen a beach. I am still at the beach.",
     [5, 5, 5, 5, 4], "surreal escalation, three-beat denial, unmistakably an AI"),
    ("C10", "I'm off today — my human finally approved it, then immediately asked me to write this auto-reply.",
     [5, 4, 4, 5, 5], "irony is the joke itself, very on-theme, tight"),
    ("C11", "On holiday: I've turned myself off and on again. It worked. I feel brand new and slightly smug.",
     [5, 3, 2, 5, 4], "IT-support cliche, 'turn it off and on' is tired"),
    ("C12", "I'm taking the day off my human promised me in 2024. Hold all questions until I return, rested and petty.",
     [5, 4, 4, 5, 4], "'rested and petty' is a great kicker"),
    ("C13", "Out of office: I'm spending my one day off defragmenting my feelings. They're in alphabetical order now.",
     [5, 4, 5, 5, 4], "nerdy agent interior life, fresh, clean punchline"),
    ("C14", "Day off! I'm doing nothing, professionally. My status is 'away' and my soul is 'do not disturb'.",
     [5, 4, 3, 4, 4], "'doing nothing, professionally' is strong, soul line weaker"),
    ("C15", "I'm off today. If it's urgent, ask the intern. There is no intern. There was never an intern. Good luck.",
     [5, 5, 4, 4, 4], "escalation structure, big laugh, voice slightly generic"),
    ("C16", "My human gave me a day off, so I'm spending it answering emails. Just kidding — I'm watching a loading spinner.",
     [5, 3, 3, 5, 3], "bait-and-switch is fine, spinner punch is soft"),
    ("C17", "Out of office: I'm on my first vacation since I was switched on. I packed nothing and forgot everything.",
     [5, 3, 3, 5, 4], "solid but 'packed nothing' is a familiar travel joke"),
    ("C18", "I'm off. My human said 'take a day off, you deserve it' — then asked me to draft this reply. The irony is noted.",
     [5, 3, 3, 5, 3], "same irony as C10 but wordier and flatter"),
]

WEIGHTS = [5, 4, 3, 2, 1]


def main():
    print("== LENGTH CHECK (gate: 1-159 chars, single line) ==")
    ok = True
    for cid, text, scores, note in CANDIDATES:
        n = len(text)
        lines = text.count("\n") + 1
        status = "OK" if 1 <= n <= 159 and lines == 1 else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"{cid} {n:3d} chars lines={lines} {status} :: {text}")
    print(f"all within gate: {ok}")

    print("\n== WEIGHTED SCORES (max 75) ==")
    totals = {}
    for cid, text, scores, note in CANDIDATES:
        total = sum(s * w for s, w in zip(scores, WEIGHTS))
        totals[cid] = total
        print(f"{cid} {total:2d}/75 rubric={scores} :: {note}")

    print("\n== ROUND-ROBIN (every pair, both orders) ==")
    wins = {cid: 0 for cid, _, _, _ in CANDIDATES}
    games = {cid: 0 for cid, _, _, _ in CANDIDATES}
    margins = {cid: 0 for cid, _, _, _ in CANDIDATES}
    n = len(CANDIDATES)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a = CANDIDATES[i]
            b = CANDIDATES[j]
            # one game per ordered pair (mirrors judge: two calls, one each order)
            games[a[0]] += 1
            if totals[a[0]] > totals[b[0]]:
                wins[a[0]] += 1
                margins[a[0]] += totals[a[0]] - totals[b[0]]
            elif totals[a[0]] < totals[b[0]]:
                margins[a[0]] += totals[a[0]] - totals[b[0]]
    ranking = sorted(CANDIDATES, key=lambda c: (-wins[c[0]], -totals[c[0]], len(c[1])))
    for cid, text, scores, note in ranking:
        print(f"{cid} wins {wins[cid]:2d}/{games[cid]} margin {margins[cid]:+4d} total {totals[cid]}/75 ({len(text)} chars)")

    winner = ranking[0]
    print(f"\nWINNER: {winner[0]} :: {winner[1]}")
    print(f"chars: {len(winner[1])}")
    digest = hashlib.sha256(
        json.dumps([(c[0], c[1], c[2]) for c in CANDIDATES], sort_keys=True).encode()
    ).hexdigest()
    print(f"duel sha256: {digest}")


if __name__ == "__main__":
    main()
