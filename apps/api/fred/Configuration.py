#!/usr/bin/env python3
"""
CyberSource SDK Configuration File for Django
Creates a proper configuration object that the SDK expects
Integrates with Django settings
"""

import os
from django.conf import settings


class Configuration:
    """Configuration class that provides the interface expected by CyberSource SDK"""

    def __init__(self):
        # Authentication method - HTTP Signature
        self.authentication_type = "http_signature"

        # Merchant credentials - Load from Django settings
        self.merchantid = getattr(settings, "CYBERSOURCE_MERCHANT_ID", "")
        self.merchant_keyid = getattr(settings, "CYBERSOURCE_MERCHANT_KEY_ID", "")
        self.merchant_secretkey = getattr(
            settings, "CYBERSOURCE_MERCHANT_SECRET_KEY", ""
        )

        # Environment - Load from Django settings
        # Default to production, set to 'sandbox' for testing
        cybersource_env = getattr(settings, "CYBERSOURCE_ENVIRONMENT", "production")
        if cybersource_env.lower() == "sandbox":
            self.run_environment = "apitest.cybersource.com"
        else:
            self.run_environment = "api.cybersource.com"

        # Optional: Logging configuration
        self.enable_log = getattr(settings, "CYBERSOURCE_ENABLE_LOG", False)
        self.log_file_name = getattr(settings, "CYBERSOURCE_LOG_FILE_NAME", "cybs")
        self.log_maximum_size = getattr(
            settings, "CYBERSOURCE_LOG_MAXIMUM_SIZE", 10487560
        )

        # Use Django's BASE_DIR if available, otherwise current directory
        base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        self.log_directory = getattr(
            settings, "CYBERSOURCE_LOG_DIRECTORY", os.path.join(base_dir, "logs")
        )

        self.log_level = getattr(settings, "CYBERSOURCE_LOG_LEVEL", "INFO")
        self.enable_masking = getattr(settings, "CYBERSOURCE_ENABLE_MASKING", True)

        # Optional: MetaKey settings
        self.use_metakey = getattr(settings, "CYBERSOURCE_USE_METAKEY", False)
        self.portfolio_id = getattr(settings, "CYBERSOURCE_PORTFOLIO_ID", None)

        # Create logs directory if it doesn't exist and logging is enabled
        if self.enable_log and not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def get(self, key, default=None):
        """Get configuration value with optional default"""
        return getattr(self, key, default)

    def set(self, key, value):
        """Set configuration value"""
        setattr(self, key, value)

    def has_key(self, key):
        """Check if configuration has a key"""
        return hasattr(self, key)

    def keys(self):
        """Return all configuration keys"""
        return [
            attr
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        ]

    def __getitem__(self, key):
        """Support dictionary-style access: config['key']"""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"Configuration key '{key}' not found")

    def __setitem__(self, key, value):
        """Support dictionary-style assignment: config['key'] = value"""
        setattr(self, key, value)

    def __contains__(self, key):
        """Support 'in' operator: 'key' in config"""
        return hasattr(self, key)

    def __iter__(self):
        """Support iteration over configuration keys"""
        return iter(self.keys())

    def items(self):
        """Return key-value pairs like a dictionary"""
        return [(key, getattr(self, key)) for key in self.keys()]


# Create the configuration instance
configuration = Configuration()

# Also set module-level variables for backward compatibility
authentication_type = configuration.authentication_type
merchantid = configuration.merchantid
merchant_keyid = configuration.merchant_keyid
merchant_secretkey = configuration.merchant_secretkey
run_environment = configuration.run_environment
enable_log = configuration.enable_log
log_file_name = configuration.log_file_name
log_maximum_size = configuration.log_maximum_size
log_directory = configuration.log_directory
log_level = configuration.log_level
enable_masking = configuration.enable_masking
use_metakey = configuration.use_metakey
portfolio_id = configuration.portfolio_id
