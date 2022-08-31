TRIES = 3
import inquirer
import json
import click
import subprocess
import arrow
from pathlib import Path


curlfile = Path("curlfile.txt")
if not curlfile.exists():
    curlfile.write_text("")


results = {}
avgs = {}
TRIES = 3


def parse_curl(content):
    lines2 = []
    fields = []
    for line in content.splitlines():
        if line.strip().startswith("--data-raw"):
            import pudb;pudb.set_trace()
            p1 = ''.join(list(reversed(line.split("'", 1)[1])))
            p2 = ''.join(reversed(str(p1).split("'", 1)[1]))
            fields = data["params"]["args"][1]
            json_oneline = json.dumps(data).replace("\n", " ")
            data["params"]["args"][1] = ["$FIELD"]
            line = f"--data-raw '{json_oneline}' \\ "
        lines2.append(line)

    return "\n".join(lines2), fields


def execute(curl, fields):
    for f in fields:
        done = 0
        while done < TRIES:
            click.secho(f"Reading field {f}", fg="yellow")
            done += 1
            start = arrow.get()
            try:
                subprocess.check_call(["/bin/bash", "-c", cmd], env={"FIELDS": '["f"]'})
            except Exception:
                done -= 1
                continue
            duration = (arrow.get() - start).total_seconds()
            results.setdefault(f, [])
            results[f].append(duration)
        avgs[f] = float(sum(results[f])) / float(tries)

    click.secho("------------------------------", fg="blue")
    click.secho(json.dumps(results, indent=4), fg="green")
    click.secho("------------------------------", fg="blue")

    for field, avg in sorted(avgs.items(), key=lambda x: x[1]):
        click.secho(f"{field}: {avg}", fg="green")


curl, fields = parse_curl(curlfile.read_text())
execute(curl, fields)
