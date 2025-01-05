#!/bin/bash

# Check if GH_TOKEN environment variable is set
if [ -z "$GH_TOKEN" ]; then
  echo "GH_TOKEN is not set. Authenticating..."

  gh auth login

  # Check if authentication was successful
  if [ $? -eq 0 ]; then
    echo "Authentication successful."
  else
    echo "Authentication failed. Please try again."
    exit 1
  fi
else
  echo "GH_TOKEN is set. No need to authenticate."
fi

gh repo clone https://rayh1@github.com/rayh1/gc2web

cd gc2web

git config --global user.name "raymond"
git config --global user.email "raymond-prive@charm.nl"

git config --global user.name "raymond"
git config --global user.email "raymond-prive@charm.nl"

cd site

npm install

npm run astro telemetry disable
