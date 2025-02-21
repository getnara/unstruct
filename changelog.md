# Changelog

## Authentication and License Updates
Improved authentication handling and updated license.

- Modified simple_auth.py to persist bypass user in database instead of keeping in memory
- Updated license from Apache to MIT
- Updated notebook with improved request handling
- Added proper error handling for authentication failures

# Add C++11 Support for chroma-hnswlib
Added additional C++ development tools and libraries to support building chroma-hnswlib which requires C++11.\n\n- Added gcc, libc6-dev, make, pkg-config, and python3-dev packages to system dependencies\n- Improved C++ build environment in Dockerfile\n\n- Added build-essential and g++ packages to system dependencies\n- Fixed line continuation in apt-get install command\n\n- Added libstdc++6 package to system dependencies\n- Set CFLAGS and CXXFLAGS environment variables for C++11 support\n- Set CC and CXX environment variables for compiler configuration
