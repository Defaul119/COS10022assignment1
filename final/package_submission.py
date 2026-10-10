"""
Build the submission zip after the final workflow has been executed and saved in KNIME.

    python package_submission.py            # checks outputs, builds submission/ and the zip

Layout produced (brief: "place all input files in the same directory as your KNIME workflow"):

    submission/
        COS10022_A1_Workflow.knwf   executed workflow; inputs inside data/src, outputs inside data/output
        src/                        copy of the input files, unchanged
        output/                     copy of every file the workflow wrote
        HOW_TO_RUN.txt
        <your video>                put it in submission/ before running this script (any .mp4/.mov/.mkv)
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "COS10022_A1_Workflow")
SUB = os.path.join(HERE, "submission")
VERIFY = os.path.join(HERE, "verify_outputs.py")
SKIP = {".knimeLock"}

out_dir = os.path.join(WF, "data", "output")
if not os.path.isdir(out_dir):
    sys.exit("No data/output folder yet: open the workflow in KNIME, Execute all, then Save, and run this again.")

print("== checking KNIME outputs")
if subprocess.run([sys.executable, "-I", VERIFY, out_dir]).returncode != 0:
    sys.exit("Output check failed - fix the workflow before packaging.")

videos = [f for f in os.listdir(SUB) if f.lower().endswith((".mp4", ".mov", ".mkv", ".avi"))] if os.path.isdir(SUB) else []
os.makedirs(SUB, exist_ok=True)
for d in ("src", "output"):
    shutil.rmtree(os.path.join(SUB, d), ignore_errors=True)
shutil.copytree(os.path.join(WF, "data", "src"), os.path.join(SUB, "src"))
shutil.copytree(out_dir, os.path.join(SUB, "output"))

knwf = os.path.join(SUB, "COS10022_A1_Workflow.knwf")
with zipfile.ZipFile(knwf, "w", zipfile.ZIP_DEFLATED) as z:
    for d, _, files in os.walk(WF):
        for f in files:
            if f not in SKIP:
                full = os.path.join(d, f)
                z.write(full, os.path.relpath(full, HERE))

with open(os.path.join(SUB, "HOW_TO_RUN.txt"), "w", encoding="utf-8") as f:
    f.write("1. KNIME Analytics Platform 5.x: File > Import KNIME Workflow > COS10022_A1_Workflow.knwf\n"
            "2. The input files are inside the workflow (data/src) and all paths are relative to the workflow,\n"
            "   so no path needs changing. Click 'Execute all'.\n"
            "3. Outputs are written to the workflow's data/output folder (copies are in output/ here).\n"
            "4. All random nodes use seed 2026, so results match the report.\n")

zip_path = os.path.join(HERE, "COS10022_A1_submission.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for d, _, files in os.walk(SUB):
        for f in files:
            full = os.path.join(d, f)
            z.write(full, os.path.relpath(full, SUB))

print(f"\n== built {zip_path}")
print(f"   video included: {videos[0] if videos else 'NO - put your video in submission/ and run this again'}")
