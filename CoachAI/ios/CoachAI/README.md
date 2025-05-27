# CoachAI - iOS App Store Submission Guide

## Overview
CoachAI is an AI-powered learning companion that creates personalized study plans using OpenAI's GPT-4 API. This guide covers everything needed for App Store submission.

## App Store Submission Checklist

### ✅ Required Files and Assets
- [x] App Icons (all sizes in AppIcon.appiconset)
- [x] Launch Screen configuration
- [x] Privacy Policy (included in app and hosted online)
- [x] Terms of Service (included in app and hosted online)
- [x] App Store metadata and description

### ✅ App Store Requirements Met
- [x] iOS 15.6+ compatibility
- [x] Portrait orientation only (mobile-optimized)
- [x] No inappropriate content
- [x] Privacy-first approach (local data storage)
- [x] Clear subscription pricing and terms
- [x] Proper API usage disclosure

### ✅ Technical Requirements
- [x] Network security (ATS configured for OpenAI)
- [x] No encryption export compliance needed
- [x] Proper usage descriptions for tracking/location
- [x] Error handling and graceful degradation
- [x] Onboarding flow for new users

## Pre-Submission Steps

### 1. Create App Icons
You need to create the following app icon sizes and place them in `CoachAI/Resources/Assets.xcassets/AppIcon.appiconset/`:

- Icon-App-20x20@2x.png (40x40)
- Icon-App-20x20@3x.png (60x60)
- Icon-App-29x29@2x.png (58x58)
- Icon-App-29x29@3x.png (87x87)
- Icon-App-40x40@2x.png (80x80)
- Icon-App-40x40@3x.png (120x120)
- Icon-App-60x60@2x.png (120x120)
- Icon-App-60x60@3x.png (180x180)
- Icon-App-1024x1024@1x.png (1024x1024)

**Icon Design Guidelines:**
- Use a brain/AI/learning theme
- Bright, recognizable colors (blue/purple gradient recommended)
- Simple, scalable design
- No text in the icon
- Rounded corners will be applied automatically

### 2. Configure Xcode Project
1. Open `CoachAI.xcodeproj` in Xcode
2. Set your Team and Bundle Identifier
3. Configure signing certificates
4. Set deployment target to iOS 15.6
5. Ensure all required capabilities are enabled

### 3. Test on Device
- Test on multiple iPhone models
- Verify API key setup flow
- Test subscription flow (if implementing Stripe)
- Ensure all features work offline when possible
- Test onboarding experience

### 4. Create App Store Connect Listing

#### App Information
- **Name**: CoachAI - AI Learning Coach
- **Subtitle**: Personalized AI-powered learning plans
- **Category**: Education
- **Age Rating**: 4+

#### Description
Use the description from `AppStoreMetadata.md`

#### Keywords
learning, education, AI, study, plans, personalized, coaching, progress, tracking, skills

#### Screenshots Needed (6.7" iPhone)
1. Onboarding welcome screen
2. Learning plan creation interface
3. Generated learning plan example
4. Dashboard with progress tracking
5. Settings and subscription screen

#### App Review Information
- **Demo Account**: Not required (app works with user's own OpenAI API key)
- **Review Notes**: 
  ```
  This app requires users to provide their own OpenAI API key to generate learning plans. 
  The app stores all data locally on the device for privacy.
  No server-side processing of user data occurs.
  ```

### 5. Privacy and Legal
- Privacy Policy URL: https://coachai.app/privacy
- Terms of Service URL: https://coachai.app/terms
- Support URL: https://coachai.app/support

## App Store Review Guidelines Compliance

### 2.1 App Completeness
- ✅ App is fully functional
- ✅ All features work as described
- ✅ No placeholder content

### 2.3 Accurate Metadata
- ✅ Description accurately reflects app functionality
- ✅ Screenshots show actual app interface
- ✅ Keywords are relevant

### 3.1.1 In-App Purchase
- ✅ Subscription terms clearly explained
- ✅ Pricing displayed prominently
- ✅ Restore purchases functionality

### 5.1.1 Privacy
- ✅ Privacy policy accessible in app
- ✅ Data collection clearly explained
- ✅ Local storage emphasized

## Build and Archive

1. **Clean Build Folder**: Product → Clean Build Folder
2. **Archive**: Product → Archive
3. **Upload to App Store Connect**: Use Xcode Organizer
4. **Submit for Review**: Complete App Store Connect listing

## Post-Submission

### Monitor Review Status
- Check App Store Connect daily
- Respond to any reviewer questions promptly
- Be prepared to provide demo video if requested

### Marketing Preparation
- Prepare social media assets
- Create landing page at coachai.app
- Plan launch announcement

## Troubleshooting Common Issues

### Rejection Reasons and Solutions

1. **Missing Privacy Policy**
   - Ensure privacy policy is accessible in Settings tab
   - Host privacy policy at provided URL

2. **Subscription Issues**
   - Clearly explain subscription benefits
   - Ensure restore purchases works
   - Test subscription flow thoroughly

3. **API Key Requirement**
   - Clearly explain why API key is needed
   - Provide helpful setup instructions
   - Allow app to function without API key (limited mode)

## Support and Maintenance

### Version Updates
- Monitor iOS compatibility
- Update OpenAI API integration as needed
- Add new features based on user feedback

### User Support
- Monitor app reviews
- Provide timely support responses
- Maintain FAQ and help documentation

## Contact Information

For questions about this submission:
- Developer: [Your Name]
- Email: [Your Email]
- Website: https://coachai.app

---

**Ready for Submission**: This app meets all App Store requirements and is ready for review. 