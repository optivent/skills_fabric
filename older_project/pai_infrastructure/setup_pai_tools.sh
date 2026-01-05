#!/bin/bash
set -e

# Ensure /opt/pai/bin exists
if [ ! -d "/opt/pai/bin" ]; then
    echo "Creating /opt/pai/bin..."
    sudo mkdir -p /opt/pai/bin
    sudo chown $USER /opt/pai/bin
fi

# Function to create a wrapper
create_wrapper() {
    local tool_name=$1
    local package_name=$2
    local executable_name=$3 
    local wrapper_path="/opt/pai/bin/$tool_name"

    echo "Creating wrapper for $tool_name..."
    cat <<INNER > "$wrapper_path"
#!/bin/bash
uv tool run --from $package_name $executable_name "\$@"
INNER
    chmod +x "$wrapper_path"
}

# Create wrappers
create_wrapper "crawl4ai" "crawl4ai" "crwl"

echo "Setup complete. Add /opt/pai/bin to your PATH."
