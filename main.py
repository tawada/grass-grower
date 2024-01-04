import sys
from routers import (
    generate_code_from_issue,
    generate_readme,
    update_issue,
)


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        if (
            args[1] == "generate_code_from_issue"
            and len(args) > 2
            and args[2].isdecimal()
        ):
            generate_code_from_issue(int(args[2]))
        elif args[1] == "generate_readme":
            generate_readme()
        elif args[1] == "update_issue":
            update_issue()
