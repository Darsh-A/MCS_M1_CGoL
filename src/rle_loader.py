def load_rle(path):
    cells = []
    x = 0
    y = 0
    count = ""

    with open(path) as f:
        lines = [line.strip() for line in f if not line.startswith("#")]

    pattern = "".join(lines[1:])

    for char in pattern:
        if char.isdigit():
            count += char
        elif char == "o":
            n = int(count) if count else 1
            for _ in range(n):
                cells.append((x, y))
                x += 1
            count = ""
        elif char == "b":
            n = int(count) if count else 1
            x += n
            count = ""
        elif char == "$":
            n = int(count) if count else 1
            y += n
            x = 0
            count = ""
        elif char == "!":
            break

    return [(x, -y) for x, y in cells]
