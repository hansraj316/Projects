#!/bin/bash

# CoachAI App Store Build Script
# This script prepares the app for App Store submission

set -e  # Exit on any error

echo "🚀 Starting CoachAI App Store Build Process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="CoachAI"
SCHEME="CoachAI"
WORKSPACE="${PROJECT_NAME}.xcodeproj"
BUILD_DIR="build"
ARCHIVE_PATH="${BUILD_DIR}/${PROJECT_NAME}.xcarchive"

# Functions
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v xcodebuild &> /dev/null; then
    print_error "Xcode command line tools not found. Please install Xcode."
    exit 1
fi

if [ ! -f "${WORKSPACE}" ]; then
    print_error "Xcode project not found: ${WORKSPACE}"
    exit 1
fi

print_success "Prerequisites check passed"

# Clean previous builds
print_step "Cleaning previous builds..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
xcodebuild clean -project "${WORKSPACE}" -scheme "${SCHEME}"
print_success "Clean completed"

# Validate project settings
print_step "Validating project settings..."

# Check if bundle identifier is set
BUNDLE_ID=$(xcodebuild -project "${WORKSPACE}" -scheme "${SCHEME}" -showBuildSettings | grep PRODUCT_BUNDLE_IDENTIFIER | head -1 | cut -d '=' -f2 | xargs)
if [ -z "$BUNDLE_ID" ] || [ "$BUNDLE_ID" = "\$(PRODUCT_BUNDLE_IDENTIFIER)" ]; then
    print_warning "Bundle identifier not set. Please configure in Xcode project settings."
fi

# Check if team is set
TEAM_ID=$(xcodebuild -project "${WORKSPACE}" -scheme "${SCHEME}" -showBuildSettings | grep DEVELOPMENT_TEAM | head -1 | cut -d '=' -f2 | xargs)
if [ -z "$TEAM_ID" ]; then
    print_warning "Development team not set. Please configure signing in Xcode."
fi

print_success "Project validation completed"

# Build for testing
print_step "Building for testing..."
xcodebuild build -project "${WORKSPACE}" -scheme "${SCHEME}" -destination "generic/platform=iOS" -configuration Release
print_success "Test build completed"

# Create archive
print_step "Creating archive..."
xcodebuild archive \
    -project "${WORKSPACE}" \
    -scheme "${SCHEME}" \
    -destination "generic/platform=iOS" \
    -archivePath "${ARCHIVE_PATH}" \
    -configuration Release \
    CODE_SIGN_STYLE=Automatic

if [ ! -d "${ARCHIVE_PATH}" ]; then
    print_error "Archive creation failed"
    exit 1
fi

print_success "Archive created successfully: ${ARCHIVE_PATH}"

# Validate archive
print_step "Validating archive..."
xcodebuild -validateArchive -archivePath "${ARCHIVE_PATH}"
print_success "Archive validation passed"

# Check for common issues
print_step "Checking for common submission issues..."

# Check for app icons
ICON_PATH="CoachAI/Resources/Assets.xcassets/AppIcon.appiconset"
if [ ! -d "$ICON_PATH" ]; then
    print_warning "App icon set not found at $ICON_PATH"
else
    ICON_COUNT=$(find "$ICON_PATH" -name "*.png" | wc -l)
    if [ "$ICON_COUNT" -lt 9 ]; then
        print_warning "Missing app icons. Found $ICON_COUNT, need 9 icons."
    else
        print_success "App icons check passed ($ICON_COUNT icons found)"
    fi
fi

# Check for privacy policy
if grep -q "privacy@coachai.app" CoachAI/Views/SettingsView.swift; then
    print_success "Privacy policy integration found"
else
    print_warning "Privacy policy integration not found in SettingsView"
fi

# Check for terms of service
if grep -q "legal@coachai.app" CoachAI/Views/SettingsView.swift; then
    print_success "Terms of service integration found"
else
    print_warning "Terms of service integration not found in SettingsView"
fi

print_success "Common issues check completed"

# Final summary
echo ""
echo "🎉 Build process completed successfully!"
echo ""
echo "📦 Archive location: ${ARCHIVE_PATH}"
echo ""
echo "📋 Next steps:"
echo "1. Open Xcode Organizer (Window → Organizer)"
echo "2. Select your archive and click 'Distribute App'"
echo "3. Choose 'App Store Connect' distribution"
echo "4. Follow the upload process"
echo ""
echo "📚 Additional requirements:"
echo "• Create app icons (see README.md for sizes)"
echo "• Set up App Store Connect listing"
echo "• Prepare screenshots"
echo "• Host privacy policy and terms at coachai.app"
echo ""
echo "🔗 Useful links:"
echo "• App Store Connect: https://appstoreconnect.apple.com"
echo "• Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/"
echo "• App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/"
echo ""
print_success "Ready for App Store submission! 🚀" 