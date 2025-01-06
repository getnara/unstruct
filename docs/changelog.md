# Changelog

## URL Name Fix
Fixed incorrect URL name in API root view to match the OrganizationViewSet's URL pattern.

- Fixed organization URL name from `organization-list` to `organizations-list` to match viewset configuration 

# S3 Pre-signed URL Region Fix
Fixed an issue where S3 pre-signed URLs were being generated with incorrect region, causing immediate expiration of download links.

- Added explicit region configuration (us-east-2) to S3 client in TaskProcessor 