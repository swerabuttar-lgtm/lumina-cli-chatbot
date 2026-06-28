"""
✨ Lumina — your sparkling CLI companion ✨
Powered by Gemini | Built with stardust and Python

Run with:
  python -m chatbot.cli
  python -m chatbot.cli --persona "You are a sarcastic pirate navigator"
"""
import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from colorama import init as colorama_init, Fore, Style
from chatbot.memory import ConversationManager
from chatbot.providers import call_model
from chatbot.pricing import compute_cost

colorama_init(autoreset=True)

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
}

# ── colour palette ──────────────────────────────────────────────────────────
YOU      = Fore.WHITE   + Style.BRIGHT
BOT      = Fore.GREEN   + Style.BRIGHT
DIM      = Fore.WHITE   + Style.DIM
WARN     = Fore.YELLOW  + Style.BRIGHT
ERR      = Fore.RED     + Style.BRIGHT
CMD      = Fore.CYAN    + Style.BRIGHT
ACCENT   = Fore.MAGENTA + Style.BRIGHT
RESET    = Style.RESET_ALL

# ── cosmetic helpers ─────────────────────────────────────────────────────────
SPARKLE = "✦"
STAR    = "★"

BANNER = f"""
{ACCENT}{'─'*58}
  {STAR}  L U M I N A  —  your sparkling CLI companion  {STAR}
  {DIM}powered by Gemini · memory · cost tracking · magic{RESET}{ACCENT}
{'─'*58}{RESET}
"""

HELP_TEXT = f"""
{CMD}{'─'*48}
  Available Commands
{'─'*48}{RESET}
{CMD}  /help{RESET}           {DIM}Show this message{RESET}
{CMD}  /clear{RESET}          {DIM}Wipe history & start fresh (keeps persona){RESET}
{CMD}  /summary{RESET}        {DIM}Ask Lumina to summarise the convo in 3 bullets{RESET}
{CMD}  /cost{RESET}           {DIM}Show running token usage & total spend{RESET}
{CMD}  /save [file]{RESET}    {DIM}Save history to JSON  (default: conversation.json){RESET}
{CMD}  /load [file]{RESET}    {DIM}Load history from JSON{RESET}
{CMD}  /quit{RESET}           {DIM}Exit{RESET}
{CMD}{'─'*48}{RESET}
"""

TOKEN_WARNING_THRESHOLD = 0.80   # warn at 80 % of budget


# ── REPL ──────────────────────────────────────────────────────────────────────
def run(
    provider: str,
    system_prompt: str,
    max_tokens: int,
    input_fn=input,
    print_fn=print,
):
    model = DEFAULT_MODELS[provider]
    memory = ConversationManager(system_prompt=system_prompt, max_tokens=max_tokens)
    total_cost = 0.0
    total_tokens_used = 0

    print_fn(BANNER)
    print_fn(
        f"{DIM}  Model : {model}   "
        f"│  Token budget : {max_tokens:,}   "
        f"│  Type /help for commands{RESET}\n"
    )

    warned_threshold = False   # so we only show the 80 % warning once per stretch

    while True:
        # ── token-usage warning ────────────────────────────────────────────
        usage_ratio = memory.total_tokens() / max_tokens if max_tokens else 0
        if usage_ratio >= TOKEN_WARNING_THRESHOLD and not warned_threshold:
            print_fn(
                f"\n{WARN}  ⚠  Heads-up! Memory is at "
                f"{usage_ratio*100:.0f}% of the token budget "
                f"({memory.total_tokens():,}/{max_tokens:,} tokens). "
                f"Old messages will start being trimmed soon.{RESET}\n"
            )
            warned_threshold = True
        elif usage_ratio < TOKEN_WARNING_THRESHOLD:
            warned_threshold = False   # reset so it can warn again after /clear

        # ── prompt ────────────────────────────────────────────────────────
        try:
            raw = input_fn(f"{YOU}  you{RESET}{DIM} ›{RESET} ")
            user_input = raw.strip()
        except (EOFError, KeyboardInterrupt):
            print_fn(f"\n{ACCENT}  {SPARKLE} Lumina signing off — see you among the stars! {SPARKLE}{RESET}\n")
            return

        if not user_input:
            continue

        # ── /quit ─────────────────────────────────────────────────────────
        if user_input in ("/quit", "/exit", "/q"):
            print_fn(f"\n{ACCENT}  {SPARKLE} Lumina signing off — see you among the stars! {SPARKLE}{RESET}\n")
            return

        # ── /help ─────────────────────────────────────────────────────────
        if user_input == "/help":
            print_fn(HELP_TEXT)
            continue

        # ── /clear  ── Challenge 1 ─────────────────────────────────────────
        if user_input == "/clear":
            memory.clear(system_prompt)
            warned_threshold = False
            print_fn(
                f"\n{ACCENT}  {SPARKLE} History cleared! Fresh start — the slate is clean.{RESET}\n"
            )
            continue

        # ── /cost ─────────────────────────────────────────────────────────
        if user_input == "/cost":
            print_fn(
                f"\n{DIM}  Tokens used this session : {total_tokens_used:,}\n"
                f"  Total cost               : ${total_cost:.6f}{RESET}\n"
            )
            continue

        # ── /save ─────────────────────────────────────────────────────────
        if user_input.startswith("/save"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) == 2 else "conversation.json"
            memory.save(path)
            print_fn(f"\n{CMD}  {SPARKLE} Conversation saved → {path}{RESET}\n")
            continue

        # ── /load ─────────────────────────────────────────────────────────
        if user_input.startswith("/load"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) == 2 else "conversation.json"
            try:
                memory.load(path)
                print_fn(f"\n{CMD}  {SPARKLE} Conversation loaded ← {path}{RESET}\n")
            except FileNotFoundError:
                print_fn(f"\n{ERR}  ✗ File not found: {path}{RESET}\n")
            continue

        # ── /summary  ── Challenge 4 ──────────────────────────────────────
        if user_input == "/summary":
            if len([m for m in memory.messages if m["role"] != "system"]) == 0:
                print_fn(f"\n{DIM}  Nothing to summarise yet — start chatting first!{RESET}\n")
                continue

            summary_prompt = (
                "Please summarise our conversation so far in exactly 3 concise "
                "bullet points. Be specific and capture the key topics discussed."
            )
            # Temporary snapshot — don't pollute real history
            temp_messages = list(memory.messages) + [
                {"role": "user", "content": summary_prompt}
            ]
            print_fn(f"\n{DIM}  Summoning the summary orb...{RESET}")
            try:
                reply, usage = call_model(provider, model, temp_messages)
                cost = compute_cost(model, usage)
                total_cost += cost
                total_tokens_used += usage["input_tokens"] + usage["output_tokens"]

                print_fn(f"\n{ACCENT}{'─'*50}")
                print_fn(f"  {STAR} Conversation Summary")
                print_fn(f"{'─'*50}{RESET}")
                print_fn(f"{BOT}{reply}{RESET}")
                print_fn(
                    f"{DIM}  [{usage['input_tokens']}in / {usage['output_tokens']}out "
                    f"| ${cost:.6f}]{RESET}\n"
                )
            except Exception as exc:
                print_fn(f"\n{ERR}  ✗ Summary failed: {exc}{RESET}\n")
            continue

        # ── normal message ─────────────────────────────────────────────────
        memory.add("user", user_input)

        print_fn(f"{DIM}  ...{RESET}", end="\r")   # thinking indicator

        try:
            reply, usage = call_model(provider, model, memory.messages)
        except Exception as exc:
            memory.messages.pop()   # remove the user turn we just added
            print_fn(f"\n{ERR}  ✗ Error calling model: {exc}{RESET}\n")
            continue

        memory.add("assistant", reply)

        cost = compute_cost(model, usage)
        total_cost += cost
        total_tokens_used += usage["input_tokens"] + usage["output_tokens"]

        print_fn(f"\n{BOT}  Lumina › {RESET}{BOT}{reply}{RESET}")
        print_fn(
            f"  {DIM}[{usage['input_tokens']}in / {usage['output_tokens']}out tokens "
            f"| ${cost:.6f} this turn | ${total_cost:.6f} total]{RESET}\n"
        )


# ── entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="✨ Lumina — sparkling CLI chatbot powered by Gemini",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--provider", default="gemini",
        choices=DEFAULT_MODELS.keys(),
        help="LLM provider to use (default: gemini)",
    )
    # Challenge 2: --persona flag
    parser.add_argument(
        "--persona",
        default=None,
        metavar="PROMPT",
        help=(
            'Custom system prompt / persona, e.g.\n'
            '  --persona "You are a sarcastic pirate navigator"\n'
            '  --persona "You are a Python tutor who loves bad puns"'
        ),
    )
    parser.add_argument(
        "--system",
        default="You are Lumina, a helpful, witty, and concise assistant with a hint of sparkle.",
        help="System prompt (overridden by --persona if both are given)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=3000,
        help="Sliding-window token budget (default: 3000)",
    )
    args = parser.parse_args()

    # --persona takes priority over --system
    system_prompt = args.persona if args.persona else args.system

    run(args.provider, system_prompt, args.max_tokens)


if __name__ == "__main__":
    main()