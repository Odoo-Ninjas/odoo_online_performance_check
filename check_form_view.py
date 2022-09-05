TRIES = 3
import sys
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
    import pudb;pudb.set_trace()
    lines2 = []
    fields = []
    for line in content.splitlines():
        if line.strip().startswith("--data-raw"):
            p1 = "".join(list(reversed(line.split("'", 1)[1])))
            p2 = "".join(reversed(str(p1).split("'", 1)[1]))
            data = json.loads(p2)
            fields = data["params"]["args"][1]
            data["params"]["args"][1] = ["__FIELD__"]
            json_oneline = json.dumps(data).replace("\n", " ")
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
            curl = " ".join(curl.split("\n"))
            curlfields = curl.replace("__FIELD__")
            try:
                print(5 * "\n")
                print(curl)
                subprocess.check_call(["/bin/bash", "-c", curl], env={"FIELDS": '["f"]'})
            except Exception:
                done -= 1
                continue
            duration = (arrow.get() - start).total_seconds()
            results.setdefault(f, [])
            results[f].append(duration)
        avgs[f] = float(sum(results[f])) / float(TRIES)

    click.secho("------------------------------", fg="blue")
    click.secho(json.dumps(results, indent=4), fg="green")
    click.secho("------------------------------", fg="blue")

    for field, avg in sorted(avgs.items(), key=lambda x: x[1]):
        click.secho(f"{field}: {avg}", fg="green")


print(f"Paste the curl of the first read of a form view into {{ curlfile }}. Ctrl+D when done")
curl = curlfile.read_text()
curl, fields = parse_curl(curl)
execute(curl, fields)
