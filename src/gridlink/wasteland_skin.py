def colorize_status(s: str) -> str:
    colors = dict(GREEN="\033[92m", YELLOW="\033[93m", RED="\033[91m")
    end = "\033[0m"
    return f"{colors.get(s,'')}{s}{end}"