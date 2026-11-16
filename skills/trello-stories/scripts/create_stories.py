#!/usr/bin/env python3
"""Creates the stories of a change as Trello cards. Dry run by default, --apply to write.

Usage: create_stories.py <stories.json> [--apply]

stories.json (paths relative to the json file):
{
  "project": "shop-payments",             # short name, used in attachment file names
  "board": "AbCd1234",                    # optional, board shortLink/URL; default = `trello use` board
  "feature": "Payments",                  # REQUIRED: one run of the skill = one feature; this label goes on
                                          #   every card and is created if missing
  "feature_color": "green",               # optional, color for a newly created feature label
  "list": "Ready",                        # optional, target list for new cards; default = first list.
                                          #   Cards of this list are ordered like stories.json (= work order)
  "labels": [],                           # optional, extra labels on every card
  "members": ["me"],                      # optional, usernames or "me"; added to new AND existing cards
  "common_notes": "notes/common.md",      # Common context block, appended to every md
  "ac_checklist": "Criterios de aceptación",   # optional, checklist name
  "stories": [
    {
      "id": "S01",
      "card": "12",                       # optional: existing card (number, shortLink or URL) -> updated
      "title": "Preparación: configurar Twint en el entorno de pruebas",   # Spanish, without points
      "points": 2,
      "description": "desc/S01.md",       # simple Spanish, Trello Markdown, may contain placeholders
      "ac": ["El pago con Twint funciona en pruebas.", "..."],   # acceptance criteria (Spanish)
      "notes": "notes/S01.md",            # story part of the tech notes (English, starts with "## Goal")
      "extra_notes": ["notes/x.md"],      # optional
      "slug": "twint-config",             # attachment: <project>_<id>_<slug>_tech-notes.md
      "blocked_by": ["S03"],              # stories (ids) or existing cards (URL/shortLink) that block this one
      "blocks": ["S07"],                  # optional, stories this one blocks (same links, other side)
      "deps_text": "optional sentence used when nothing blocks this story",
      "labels": ["Publish"],              # optional, extra labels for this card
      "list": "Doing"                     # optional, per-card list (new cards only)
    }
  ]
}

Description placeholders: {{AC}}, {{BLOCKED_BY_LINKS}}, {{BLOCKS_LINKS}}, {{ATTACHMENT}},
{{S07}} card URL, {{S07:link}} [title](url), {{S07:title}} title.
Notes placeholders: the same plus {{BLOCKED_BY_LINE}}, {{BLOCKS_LINE}} (header, added automatically),
{{URL}}, {{SHORTLINK}} (this card).

Every dependency becomes a card-link attachment on BOTH cards and a line in both descriptions
("Bloqueada por" / "Bloquea"). blocked_by and blocks are merged and de-duplicated.

stories.json order = work order: a story must come after every story that blocks it (checked), and on
--apply the cards in the target list are re-ordered top-to-bottom in this order.

Trello access: `trello` CLI only (on PATH or $TRELLO_CLI).
Resumable: created cards and finished steps are stored in <stories.json>.state.json; a rerun skips them.
"""
import json
import os
import re
import shutil
import subprocess
import sys

CARD_REF = re.compile(r"(?:https://trello\.com/c/)?([A-Za-z0-9]{8})(?:/.*)?$")


def cli_path():
    path = os.environ.get("TRELLO_CLI") or shutil.which("trello")
    if not path:
        raise SystemExit("trello CLI not found: install it from https://github.com/silvioalbertoscarfo91/trello-cli "
                         "or set TRELLO_CLI")
    return path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if len(args) != 1:
        raise SystemExit(__doc__)
    spec_path = os.path.abspath(args[0])
    root = os.path.dirname(spec_path)
    spec = json.load(open(spec_path))
    state_path = spec_path + ".state.json"
    state = (json.load(open(state_path)) if os.path.exists(state_path)
             else {"cards": {}, "described": [], "checklisted": [], "uploaded": [], "links": []})
    board = spec.get("board")
    ac_name = spec.get("ac_checklist", "Criterios de aceptación")

    def trello(*a, as_json=False):
        cmd = [cli_path()] + (["--board", board] if board else []) + list(a)
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit(f"trello {' '.join(a[:2])} failed: {(out.stderr or out.stdout)[:500]}")
        return json.loads(out.stdout) if as_json else out.stdout

    def save():
        if apply:
            json.dump(state, open(state_path, "w"), indent=2, ensure_ascii=False)

    def read(rel):
        return open(os.path.join(root, rel)).read()

    stories = spec["stories"]
    by_id = {s["id"]: s for s in stories}

    # ---------------------------------------------------------------- validation
    problems = []
    for s in stories:
        for f in ("id", "title", "points", "description", "notes", "slug", "ac"):
            if f not in s:
                problems.append(f"{s.get('id', '?')}: missing field '{f}'")
        if not s.get("ac"):
            problems.append(f"{s.get('id')}: no acceptance criteria")
        if re.match(r"^\[\d", s.get("title", "")):
            problems.append(f"{s['id']}: points belong in 'points', not in the title")
        for dep in s.get("blocked_by", []) + s.get("blocks", []):
            if dep not in by_id and not CARD_REF.fullmatch(dep):
                problems.append(f"{s['id']}: unknown dependency {dep}")
        for f in [s.get("description", ""), s.get("notes", "")] + s.get("extra_notes", []):
            if f and not os.path.exists(os.path.join(root, f)):
                problems.append(f"{s['id']}: missing file {f}")
            elif f:
                for ref in re.findall(r"\{\{(S\d+)(?::\w+)?\}\}", read(f)):
                    if ref not in by_id:
                        problems.append(f"{s['id']}: {f} references {ref}, which is not in this stories.json "
                                        f"(use the card URL instead)")
    if not spec.get("feature"):
        problems.append("missing 'feature' (the feature label every card of this run gets)")
    index = {s["id"]: i for i, s in enumerate(stories)}
    for s in stories:
        for d in s.get("blocked_by", []):
            if d in index and index[d] > index[s["id"]]:
                problems.append(f"order: {d} blocks {s['id']}, so it must come before it in stories.json")
        for d in s.get("blocks", []):
            if d in index and index[d] < index[s["id"]]:
                problems.append(f"order: {s['id']} blocks {d}, so it must come before it in stories.json")
    if not os.path.exists(os.path.join(root, spec["common_notes"])):
        problems.append("missing common_notes")
    if problems:
        raise SystemExit("NOT OK:\n  " + "\n  ".join(problems))

    edges = []  # (blocker, blocked)
    for s in stories:
        edges += [(d, s["id"]) for d in s.get("blocked_by", [])]
        edges += [(s["id"], d) for d in s.get("blocks", [])]
    edges = list(dict.fromkeys(edges))

    # ---------------------------------------------------------------- feature label
    feature = spec["feature"]
    if apply and feature not in {l["name"] for l in trello("labels", "--json", as_json=True)}:
        trello("label-create", feature, "--color", spec.get("feature_color", "sky"))
        print(f"created label {feature}")
    elif not apply:
        print(f"FEATURE LABEL: {feature} (created if missing)")

    # ---------------------------------------------------------------- pass 1: cards
    for s in stories:
        if s["id"] in state["cards"]:
            continue
        labels = list(dict.fromkeys([feature] + spec.get("labels", []) + s.get("labels", [])))
        if not apply:
            verb = f"UPDATE card {s['card']}" if s.get("card") else "CREATE"
            print(f"{verb} {s['id']}: [{s['points']}] {s['title']}  labels={labels} members={spec.get('members', [])}")
            state["cards"][s["id"]] = {"shortLink": f"<{s['id']}>", "shortUrl": f"https://trello.com/c/<{s['id']}>"}
            continue
        if s.get("card"):
            ref = trello("update", s["card"], "--title", s["title"], "--points", str(s["points"]), "--json", as_json=True)
            for l in labels:
                trello("update", ref["shortLink"], "--add-label", l)
            for m in spec.get("members", []):
                trello("update", ref["shortLink"], "--add-member", m)
        else:
            a = ["create", s["title"], "--points", str(s["points"]), "--desc", "(en preparación)", "--json"]
            lst = s.get("list") or spec.get("list")
            if lst:
                a += ["--list", lst]
            for l in labels:
                a += ["--label", l]
            for m in spec.get("members", []):
                a += ["--member", m]
            ref = trello(*a, as_json=True)
        state["cards"][s["id"]] = {"shortLink": ref["shortLink"], "shortUrl": ref["shortUrl"]}
        save()
        print(f"{'updated' if s.get('card') else 'created'} {s['id']} = {ref['shortUrl']}")

    cards = state["cards"]
    external = {}

    def url(ref):
        if ref in cards:
            return cards[ref]["shortUrl"]
        return f"https://trello.com/c/{CARD_REF.fullmatch(ref).group(1)}"

    def title(ref):
        if ref in by_id:
            return by_id[ref]["title"]
        if ref not in external:
            external[ref] = (re.sub(r"^\[[\d.]+\]\s*", "", trello("show", ref, "--json", as_json=True)["name"])
                             if apply else f"<title of {ref}>")
        return external[ref]

    def resolve(text, s, attachment):
        blocked_by = [a for a, b in edges if b == s["id"]]
        blocks = [b for a, b in edges if a == s["id"]]
        text = text.replace("{{AC}}", "\n".join(f"- {c}" for c in s["ac"]))
        text = text.replace("{{BLOCKED_BY_LINKS}}", ("\n" + "\n".join(f"- {url(r)}" for r in blocked_by)) if blocked_by
                            else s.get("deps_text", "ninguna"))
        text = text.replace("{{BLOCKS_LINKS}}", ("\n" + "\n".join(f"- {url(r)}" for r in blocks)) if blocks else "ninguna")
        text = text.replace("{{BLOCKED_BY_LINE}}", ("Blocked by: " + ", ".join(f"{url(r)} ({title(r)})" for r in blocked_by))
                            if blocked_by else "")
        text = text.replace("{{BLOCKS_LINE}}", ("Blocks: " + ", ".join(f"{url(r)} ({title(r)})" for r in blocks))
                            if blocks else "")
        text = text.replace("{{ATTACHMENT}}", attachment)
        text = text.replace("{{URL}}", cards[s["id"]]["shortUrl"]).replace("{{SHORTLINK}}", cards[s["id"]]["shortLink"])
        text = re.sub(r"\{\{(S\d+):link\}\}", lambda m: f"[{title(m.group(1))}]({url(m.group(1))})", text)
        text = re.sub(r"\{\{(S\d+):title\}\}", lambda m: title(m.group(1)), text)
        text = re.sub(r"\{\{(S\d+)\}\}", lambda m: url(m.group(1)), text)
        left = re.findall(r"\{\{[A-Z0-9_:a-z]+\}\}", text)
        if left:
            raise SystemExit(f"{s['id']}: unresolved placeholders {left}")
        return text

    outdir = os.path.join(root, "rendered")
    os.makedirs(outdir, exist_ok=True)
    common = read(spec["common_notes"])
    workflow = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "agent-workflow.md")).read()

    # ---------------------------------------------------------------- pass 2: description, checklist, md
    for s in stories:
        ref = cards[s["id"]]["shortLink"]
        attachment = f"{spec['project']}_{s['id']}_{s['slug']}_tech-notes.md"
        desc = resolve(read(s["description"]), s, attachment)
        story_part = read(s["notes"]).strip()
        if not story_part.startswith("## Goal"):
            raise SystemExit(f"{s['id']}: notes must start with '## Goal' (goal prompt, see tech-notes-template.md)")
        md = (f"# {s['title']} (Trello {{{{URL}}}})\n\n{{{{BLOCKED_BY_LINE}}}}\n{{{{BLOCKS_LINE}}}}\n\n" + story_part
              + "\n\n" + workflow.strip() + "\n\n" + common.strip() + "\n")
        for extra in s.get("extra_notes", []):
            md += "\n" + read(extra).strip() + "\n"
        md = re.sub(r"\n{3,}", "\n\n", resolve(md, s, attachment))
        md_path = os.path.join(outdir, attachment)
        desc_path = os.path.join(outdir, s["id"] + ".description.md")
        open(md_path, "w").write(md)
        open(desc_path, "w").write(desc)
        if not apply:
            print(f"DESCRIBE + CHECKLIST ({len(s['ac'])} items) + ATTACH {s['id']}: {attachment}")
            continue
        if s["id"] not in state["described"]:
            trello("update", ref, "--desc-file", desc_path)
            state["described"].append(s["id"]); save()
        if s["id"] not in state["checklisted"]:
            trello("checklist", ref, ac_name, *s["ac"], "--replace")
            state["checklisted"].append(s["id"]); save()
        if s["id"] not in state["uploaded"]:
            trello("attach", ref, md_path, "--replace")
            state["uploaded"].append(s["id"]); save()
        print(f"described + checklist + attached {s['id']}")

    # ---------------------------------------------------------------- pass 3: links (both ways, idempotent)
    def cref(r):
        return cards[r]["shortLink"] if r in cards else CARD_REF.fullmatch(r).group(1)

    for blocker, blocked in edges:
        tag = f"{cref(blocker)}>{cref(blocked)}"
        if not apply:
            print(f"LINK {url(blocker)} blocks {url(blocked)} (card links on both)")
            continue
        if tag in state["links"]:
            continue
        trello("link", cref(blocker), cref(blocked), "--both-ways")
        state["links"].append(tag); save()
        print(f"linked {tag}")

    # ---------------------------------------------------------------- pass 4: order in the target list
    target = spec.get("list")
    if not apply:
        print("ORDER (top to bottom in list " + (target or "<first list>") + "): " + ", ".join(s["id"] for s in stories))
    else:
        lists = trello("lists", "--json", as_json=True)
        target_list = next((l for l in lists if l["name"] == target), lists[0])
        for s in stories:
            c = trello("show", cards[s["id"]]["shortLink"], "--json", as_json=True)
            if c["idList"] == target_list["id"]:  # never move cards somebody already took (Doing, Done, …)
                trello("move", cards[s["id"]]["shortLink"], target_list["name"], "--pos", "bottom")
        print(f"ordered {len(stories)} cards in {target_list['name']}")

    # ---------------------------------------------------------------- verify
    if apply:
        bad = []
        for s in stories:
            c = trello("show", cards[s["id"]]["shortLink"], "--json", as_json=True)
            att_urls = {a.get("url") for a in c.get("attachments", [])}
            neighbours = {a for a, b in edges if b == s["id"]} | {b for a, b in edges if a == s["id"]}
            missing = [url(n) for n in neighbours if url(n) not in att_urls]
            if missing:
                bad.append(f"{s['id']}: missing card links {missing}")
            if not any(a.get("name", "").endswith("_tech-notes.md") for a in c.get("attachments", [])):
                bad.append(f"{s['id']}: tech-notes attachment missing")
            if not any(cl["name"] == ac_name for cl in c.get("checklists", [])):
                bad.append(f"{s['id']}: checklist missing")
        print("verify OK" if not bad else "VERIFY FAILED:\n  " + "\n  ".join(bad))
        print("\n| id | card | title |\n|---|---|---|")
        for s in stories:
            print(f"| {s['id']} | {cards[s['id']]['shortUrl']} | [{s['points']}] {s['title']} |")
    print(f"\nrendered files: {outdir}")
    print("dry run only, rerun with --apply" if not apply else "done")


if __name__ == "__main__":
    main()
