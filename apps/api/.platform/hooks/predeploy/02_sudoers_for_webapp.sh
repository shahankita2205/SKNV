#!/bin/bash

# Exit on error
set -euo pipefail

echo "Configuring sudo for webapp user to restart web service"

# Create a sudoers file to allow the webapp user to restart the web service without a password.
# This is needed for the refresh_secrets.sh script which may run periodically.
cat <<EOF > /etc/sudoers.d/webapp-restart
# Allow webapp user to restart web service without a password
webapp ALL=(ALL) NOPASSWD: /bin/systemctl restart web.service
EOF

# Set the correct permissions for the sudoers file, which is required by sudo.
chmod 0440 /etc/sudoers.d/webapp-restart

echo "Sudoers configuration for webapp user complete."
