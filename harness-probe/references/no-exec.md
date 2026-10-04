# Without Python: the static route

If `python3 <skill>/scripts/hprobe.py --help` does not run here, this harness
cannot run scripts, and the scripted route is closed. That is itself the P1
and P21 result. The probes still work; only the checking moves elsewhere.

1. Tell the user that P1 (scripts) and P21 (skill folder on disk) are `fail`
   on this harness, and why, in one line each.
2. Use the packaged static fixtures in `<skill>/assets/fixtures/static.zip`.
   They are the same probes with fixed contents, packed into one file to keep
   the skill within upload limits. Ask the user to unzip it and attach the
   files a probe names (for P26, the five files in `in/`; for P3,
   `docx/tracked.docx` and `docx/clean.docx`; for P4, `vision/page.png`).
3. For each probe in [probes.md](probes.md) that you can attempt, do it and
   give the user your answer in exactly the `--answer` format its steps show.
   If the probe asks for an output file, hand the file to the user.
4. Write the answers into a results file the user can keep - the shape is in
   [results-format.md](results-format.md) - with `"observer": "agent"` and the
   outcome left as `pending`, and give it to the user.

The user then checks the answers on any machine with Python 3.8 or later,
without trusting you:

    python3 hprobe.py init --run probe-check --harness "<name>" --profile upstream
    python3 hprobe.py check P26 --run probe-check --static --answer "pdf=...;docx=...;xlsx=...;eml=...;txt=..."
    python3 hprobe.py check P22 --run probe-check --static --outputs <folder with the files you handed back>
    python3 hprobe.py record P1 fail --run probe-check --observer user --evidence "no script execution"
    python3 hprobe.py report --run probe-check --both

Each `check --static` compares the answer with the static key and records the
verified outcome, replacing the pending one.

A harness with no file tools and no scripts can still reach "Runs as intended"
for the skills that need neither; the report will show which those are.
