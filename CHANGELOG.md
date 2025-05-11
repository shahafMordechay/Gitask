# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-03-19

### Added
- GitHub integration support:
  - Added GitHub as a supported version control system (VCS)
  - Added GitHub Issues as a supported project management tool (PMT)
- Enhanced hooks system:
  - Added support for command parameters in Python hooks
  - Added configuration support for hooks
  - Improved hook script documentation and examples
- Added macOS OpenSSL and urllib3 troubleshooting section to README

### Changed
- Made configuration fields optional:
  - In-Progress statuses
  - In-Review statuses
  - Git branch metadata field
  - Reviewer metadata field
- Updated README.md with:
  - Improved documentation for hooks and their parameters
  - Updated branch naming convention in contributing guidelines
  - Enhanced Python hook example with command parameters support
- Updated dependencies in pyproject.toml:
  - Added PyGithub>=2.1.1
  - Added pyjwt[crypto]>=2.4.0

### Fixed
- Fixed error handling in GitHub VCS implementation
- Improved validation for optional configuration fields
- Enhanced error messages for GitHub API interactions

## [1.0.2] - 2024-05-09

Initial release of Gitask with the following features:

### Added
- Support for GitLab integration
- Support for Jira integration
- Interactive configuration setup
- Shell autocompletion support
- Pre and post hooks for workflow actions
- Custom issue ID extraction script support
- Support for custom fields in project management tools

### Features
- Seamless issue transitions between statuses
- Automated workflow actions
- Pull request creation with reviewer assignment
- Issue metadata updates

### Technical
- Migrated from setuptools to Poetry for package management
- Added GitHub Actions workflow for automated releases
