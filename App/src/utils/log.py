
import inspect
import json
import traceback
from datetime import datetime
from pathlib import Path


def log(data, path=None):
    frame = inspect.currentframe().f_back

    filename = Path(frame.f_code.co_filename).name if frame else "app.py"
    stem = Path(filename).stem

    if filename in ("<stdin>", "<string>", "-c"):
        filename, stem = "app.py", "app"

    del frame

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(data, (dict, list)):
        data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    elif isinstance(data, BaseException):
        data = "".join(traceback.format_exception(data)).strip()
    else:
        data = str(data).strip()

    header = f"[ {now} ] [ {filename} ]"

    entry = (
        f"{header} ----------------------------------------\n"
        f"{data}\n"
        f"--------------------------------------------------"
        if "\n" in data
        else f"{header} {data}"
    )

    target = Path(path) if path else Path("logs") / f"{stem}.log"
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("a", encoding="utf-8") as file:
        file.write(entry + "\n")

    return entry
