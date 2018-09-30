#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes orsay | grep -v migration
