#!/bin/bash

set -e  # Exit on any error

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\e[32m$message\e[0m" ;;
        "yellow") echo -e "\e[33m$message\e[0m" ;;
        "red") echo -e "\e[31m$message\e[0m" ;;
    esac
}

# Check if script is NOT being run as root
if [ "$EUID" -eq 0 ]; then 
    print_status "red" "Please do not run as root. Run as your normal user."
    exit 1
fi

# Get the hostname for subdomain
HOSTNAME=$(hostname)

# Install Certbot and Nginx plugin
print_status "yellow" "Installing Certbot..."
sudo apt-get install -y certbot python3-certbot-nginx

print_status "yellow" "Starting development environment setup..."

# Remove unwanted repositories
REPOS_TO_REMOVE=(
    "/etc/apt/sources.list.d/ondrej-ubuntu-php-jammy.list"
    "/etc/apt/sources.list.d/phalcon_stable.list"
)

for repo in "${REPOS_TO_REMOVE[@]}"; do
    if [ -f "$repo" ]; then
        print_status "yellow" "Removing repository: $repo"
        sudo rm "$repo"
    fi
done

# Update package list
print_status "yellow" "Updating package list..."
sudo apt-get update

# Install essential packages
print_status "yellow" "Installing essential packages..."
sudo apt-get install -y \
    curl \
    git \
    apt-transport-https \
    ca-certificates \
    gnupg \
    software-properties-common \
    nginx

# Configure Nginx
print_status "yellow" "Configuring Nginx virtual hosts..."

# Create API virtual host
sudo tee /etc/nginx/sites-available/api.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    server_name api.${HOSTNAME}.sknv.cubby.zone;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Create App virtual host
sudo tee /etc/nginx/sites-available/app.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    server_name app.${HOSTNAME}.sknv.cubby.zone;

    # Custom error page for 502
    error_page 502 /502.html;
    location = /502.html {
        alias /home/dev/proj/nextgen/infrastructure/dev/502.html;
        internal;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Next.js specific headers
        proxy_set_header X-NextJS-Data 1;
    }
}
EOL

# Create Dashboard virtual host
sudo tee /etc/nginx/sites-available/dashboard.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    server_name dashboard.${HOSTNAME}.sknv.cubby.zone;

    location / {
        proxy_pass http://localhost:5555;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Enable the sites
sudo ln -sf /etc/nginx/sites-available/api.sknv.cubby.zone /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/app.sknv.cubby.zone /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/dashboard.sknv.cubby.zone /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Setup SSL certificates with Let's Encrypt
print_status "yellow" "Setting up SSL certificates..."

# Request certificates for all domains
sudo certbot certonly \
    --nginx \
    --email devops@sknv.com \
    --agree-tos \
    --no-eff-email \
    -d "api.${HOSTNAME}.sknv.cubby.zone" \
    -d "app.${HOSTNAME}.sknv.cubby.zone" \
    -d "dashboard.${HOSTNAME}.sknv.cubby.zone"

# Update Nginx configurations to use SSL
print_status "yellow" "Updating Nginx configurations with SSL..."

# Update API virtual host with SSL
sudo tee /etc/nginx/sites-available/api.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    listen [::]:80;
    server_name api.${HOSTNAME}.sknv.cubby.zone;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.${HOSTNAME}.sknv.cubby.zone;

    ssl_certificate /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Update App virtual host with SSL
sudo tee /etc/nginx/sites-available/app.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    listen [::]:80;
    server_name app.${HOSTNAME}.sknv.cubby.zone;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.${HOSTNAME}.sknv.cubby.zone;

    ssl_certificate /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Custom error page for 502
    error_page 502 /502.html;
    location = /502.html {
        alias /home/dev/proj/nextgen/infrastructure/dev/502.html;
        internal;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Next.js specific headers
        proxy_set_header X-NextJS-Data 1;
    }
}
EOL

# Update App virtual host with SSL
sudo tee /etc/nginx/sites-available/dashboard.sknv.cubby.zone > /dev/null << EOL
server {
    listen 80;
    listen [::]:80;
    server_name dashboard.${HOSTNAME}.sknv.cubby.zone;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dashboard.${HOSTNAME}.sknv.cubby.zone;

    ssl_certificate /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.${HOSTNAME}.sknv.cubby.zone/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        proxy_pass http://localhost:5555;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Setup auto-renewal
print_status "yellow" "Setting up certificate auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

print_status "green" "SSL certificates have been configured!"

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "yellow" "Installing Docker..."
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
else
    print_status "green" "Docker is already installed"
fi

# Remove old docker-compose if it exists (both package and binary)
print_status "yellow" "Removing old Docker Compose versions..."
if command -v docker-compose &> /dev/null; then
    # Remove package if installed via apt
    sudo apt-get remove -y docker-compose
fi

# Remove binary if it exists
sudo rm -f /usr/bin/docker-compose
sudo rm -f /usr/local/bin/docker-compose

# Install Docker Compose V2
print_status "yellow" "Installing Docker Compose V2..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create symlink for backward compatibility
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Setup Docker permissions
print_status "yellow" "Setting up Docker permissions..."
sudo groupadd -f docker
sudo usermod -aG docker $USER

# Install NVM if not present
if [ ! -d "$HOME/.nvm" ]; then
    print_status "yellow" "Installing NVM..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    
    # Add NVM to path for current session
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
else
    print_status "green" "NVM is already installed"
fi

# Ensure NVM is loaded
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js LTS and Yarn
print_status "yellow" "Installing Node.js LTS and Yarn..."
nvm install --lts
nvm use --lts

# Disable corepack auto-pinning
export COREPACK_ENABLE_AUTO_PIN=0

# Add to bash profile if not already present
if ! grep -q "export COREPACK_ENABLE_AUTO_PIN=0" ~/.bashrc; then
    echo "export COREPACK_ENABLE_AUTO_PIN=0" >> ~/.bashrc
fi

# Install Yarn using corepack if not present
if ! command -v yarn &> /dev/null; then
    corepack enable
    corepack prepare yarn@stable --activate
fi

# Verify installations
print_status "yellow" "Verifying installations..."

echo "Docker version:"
docker --version || echo "Docker not accessible yet (requires logout/login)"

echo "Docker Compose version:"
docker-compose --version || echo "Docker Compose not accessible yet (check permissions)"

echo "Node.js version:"
node --version

echo "Yarn version:"
yarn --version

print_status "green" "Setup complete!"