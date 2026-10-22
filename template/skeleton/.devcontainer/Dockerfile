# The sandbox's agent image: the coding CLIs from other vendors, git, gh and Python for the checks.
# Versions are exact and at least two weeks old when pinned. setup.py keeps this only in a sandbox.
FROM node:22.23.2-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends gh && rm -rf /var/lib/apt/lists/*
RUN npm install -g @github/copilot@1.0.93 @google/gemini-cli@0.63.0
USER node
WORKDIR /home/node
