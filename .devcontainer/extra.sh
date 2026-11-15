#!/usr/bin/env bash
# Project-owned build hook, run as root at the end of the image build.
# `copier update` never overwrites this file. Add whatever the image needs beyond apt packages.
set -euo pipefail
