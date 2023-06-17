#!/bin/bash
# MIT License

# Copyright (c) 2023 Altynbek Orumbayev

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Default URL
model_url="https://gpt4all.io/models/ggml-gpt4all-l13b-snoozy.bin"
# Default uninstall option
uninstall=false
# Help function
function display_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --custom_model_url <URL>   Specify a custom URL for the model download step."
    echo "  --uninstall                Uninstall the projects from your local machine."
    echo "  --help                     Display this help message and exit."
    echo
}
# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --custom_model_url) model_url="$2"; shift ;;
        --uninstall) uninstall=true ;;
        --help) display_help; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done
cd ..
if [ "$uninstall" = true ] ; then
    echo "Uninstalling..."
    rm -rf LocalAI
    exit 0
fi

# Check if the directory exists, if not clone the repository, else pull the latest changes
if [ ! -d "LocalAI" ]; then
  git clone https://github.com/go-skynet/LocalAI
else
  cd LocalAI
  git pull
  cd ..
fi

cd LocalAI
make build

# Only download the model if a custom URL is provided or if the model does not already exist
if [ ! -z "$2" ] || [ ! -f "models/gpt-3.5-turbo" ]; then
    wget $model_url -O models/gpt-3.5-turbo
fi

cd ..

cd HybridAGI