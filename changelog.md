# Changelog

## Project Messaging and Open Source Announcement
Updated project messaging to better reflect our mission and open-source focus.

- Revised project overview to position Unstruct as "Supabase for AI"
- Added detailed explanation of core AI backend components
- Added "Why Open Source?" section explaining our mission
- Added comprehensive feature table showcasing key capabilities
- Updated project purpose to emphasize community and infrastructure focus

## Documentation Updates
Improved setup instructions and added contribution guidelines.

- Added Quick Start section with run_local.sh script instructions
- Enhanced manual setup instructions with PostgreSQL requirements
- Improved code block formatting with bash syntax highlighting
- Added comprehensive CONTRIBUTING.md guide
- Added Contributing section to README with quick start guide
- Added community links and contribution process

## Authentication and License Updates
Improved authentication handling and updated license.

- Modified simple_auth.py to persist bypass user in database instead of keeping in memory
- Updated license from Apache to MIT
- Updated notebook with improved request handling
- Added proper error handling for authentication failures

# Add C++11 Support for chroma-hnswlib
Added additional C++ development tools and libraries to support building chroma-hnswlib which requires C++11.\n\n- Added gcc, libc6-dev, make, pkg-config, and python3-dev packages to system dependencies\n- Improved C++ build environment in Dockerfile\n\n- Added build-essential and g++ packages to system dependencies\n- Fixed line continuation in apt-get install command\n\n- Added libstdc++6 package to system dependencies\n- Set CFLAGS and CXXFLAGS environment variables for C++11 support\n- Set CC and CXX environment variables for compiler configuration
