import os
import shutil
from pathlib import Path

TEST_DATA_DIR = Path("/tmp/docurule-ai-tests")
shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
os.environ["DOCURULE_DATA_DIR"] = str(TEST_DATA_DIR)
os.environ["DOCURULE_AI_PROVIDER"] = "local"
