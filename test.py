#!/usr/bin/env python3

import re
import sys
import argparse
from pathlib import Path

GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

OK            = 0
FAILED        = 1
INVALID_USAGE = 2

def main():
    parser = argparse.ArgumentParser(
        description="Тест регулярного выражения на группах Университета"
    )
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="включить тихий режим")
    parser.add_argument("-r", "--regex", default="regex.txt",
                        help="файл с регулярным выражением")
    parser.add_argument("-g", "--groups", default="groups.csv",
                        help="файл с тестовыми группами")
    parser.add_argument("-n", "--no-color", action="store_true",
                        help="отключить цветной вывод")
    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()
    def c(text, color):
        return f"{color}{text}{RESET}" if use_color else text

    regex_path = Path(args.regex)
    groups_path = Path(args.groups)

    if not regex_path.is_file():
        print(f"Ошибка: файл {regex_path} не найден", file=sys.stderr)
        return INVALID_USAGE
    if not groups_path.is_file():
        print(f"Ошибка: файл {groups_path} не найден", file=sys.stderr)
        return INVALID_USAGE

    pattern_text = regex_path.read_text(encoding="utf-8").strip()
    try:
        pattern = re.compile(pattern_text)
    except re.error as e:
        print(f"Ошибка в регулярном выражении: {e}", file=sys.stderr)
        return INVALID_USAGE

    lines = [ln.rstrip("\n") for ln in groups_path.read_text(encoding="utf-8").splitlines()]
    lines = [ln for ln in lines if ln != ""]

    if not lines:
        print(f"Файл {groups_path}", file=sys.stderr)
        return INVALID_USAGE

    total = len(lines)
    matched = 0
    failed_lines = []

    for idx, line in enumerate(lines, 1):
        if pattern.search(line):
            matched += 1
            if not args.quiet:
                print(f"{c('OK  ', GREEN)} [{idx}] {line}")
        else:
            failed_lines.append((idx, line))
            if not args.quiet:
                print(f"{c('FAIL', RED)} [{idx}] {line}")

    percent = matched / total * 100
    color = GREEN if percent == 100 else (YELLOW if percent >= 50 else RED)

    print()
    print(c(f"{BOLD}Покрытие: {percent:.2f}% ({matched}/{total}){RESET}", color))

    if failed_lines:
        if not args.quiet:
            print(c("Не прошли проверку:", RED))
            for idx, line in failed_lines:
                print(f"  [{idx}] {line}")
        return FAILED

    return OK


if __name__ == "__main__":
    sys.exit(main())
