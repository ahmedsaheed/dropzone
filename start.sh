 #!/usr/bin/env bash

export GOOGLE_APPLICATION_CREDENTIALS="./GriffithLabs_IAM.json"
python3 -m uvicorn init:app --reload