import argparse
import sys
from pathlib import Path


def cmd_run(args):
    from arena.harness import Tournament

    tournament_dir = Path(args.tournament_dir)
    pkg_root = Path(__file__).parent.parent.parent
    baseline_dir = pkg_root / "baseline"
    seed_dir = pkg_root / "seed_challenges"

    tournament = Tournament(
        tournament_dir=tournament_dir,
        num_agents=args.agents,
        challenges_per_round=args.challenges_per_round,
        total_rounds=args.rounds,
    )

    if tournament.load_state():
        print(f"Resuming tournament from round {tournament.state.round_num + 1}")
    else:
        print("Starting new tournament...")
        tournament.setup(baseline_dir, seed_dir)

    tournament.run()
    print("\nTournament complete!")
    print(f"Token usage: {tournament.llm.token_usage}")


def cmd_bootstrap(args):
    from arena.leetcode import bootstrap
    from arena.challenges import save_challenge

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Bootstrapping challenges from LeetCode...")
    print(f"  Easy: {args.easy}, Medium: {args.medium}, Hard: {args.hard}")

    specs = bootstrap(easy=args.easy, medium=args.medium, hard=args.hard)

    for spec in specs:
        save_challenge(spec, output_dir)
        print(f"  saved {spec.id} ({spec.difficulty}): {spec.title}")

    print(f"\n{len(specs)} challenges saved to {output_dir}")


def cmd_status(args):
    from arena.harness import Tournament

    tournament_dir = Path(args.tournament_dir)
    tournament = Tournament(tournament_dir=tournament_dir)

    if not tournament.load_state():
        print("No tournament found at", tournament_dir)
        sys.exit(1)

    status = tournament.get_status()
    print("Tournament Status")
    print(f"  Round: {status['round']}/{status['total_rounds']}")
    print(f"  Agents: {status['num_agents']}")
    print(f"  Challenges: {status['num_challenges']}")
    print("\nAgents:")
    for a in status["agents"]:
        print(f"  {a['id']} (gen {a['generation']})")
    print(f"\nToken Usage: {status['token_usage']}")


def main():
    parser = argparse.ArgumentParser(
        prog="arena",
        description="Adversarial Agent Evolution Tournament",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run
    run_parser = subparsers.add_parser("run", help="Run the tournament")
    run_parser.add_argument("--agents", type=int, default=4)
    run_parser.add_argument("--rounds", type=int, default=20)
    run_parser.add_argument("--challenges-per-round", type=int, default=4)
    run_parser.add_argument("--tournament-dir", default="./tournament")

    # bootstrap
    boot_parser = subparsers.add_parser(
        "bootstrap", help="Bootstrap challenges from LeetCode"
    )
    boot_parser.add_argument("--easy", type=int, default=5)
    boot_parser.add_argument("--medium", type=int, default=5)
    boot_parser.add_argument("--hard", type=int, default=3)
    boot_parser.add_argument("--output-dir", default="./seed_challenges")

    # status
    status_parser = subparsers.add_parser("status", help="Show tournament status")
    status_parser.add_argument("--tournament-dir", default="./tournament")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "bootstrap":
        cmd_bootstrap(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
