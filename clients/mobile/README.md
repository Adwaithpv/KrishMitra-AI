# Agri Advisor Mobile App

A Flutter mobile application for the Agentic Agri Advisor system.

## Features

- **Voice Input/Output**: Speech-to-text and text-to-speech capabilities
- **Agent Integration**: Connects to the backend API with specialized agents
- **Location & Crop Context**: Set default location and crop for personalized advice
- **Query History**: View and manage past queries and responses
- **Evidence Display**: Show sources and confidence scores for responses
- **Offline Support**: Basic offline functionality (planned)

## Setup

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Android Studio / VS Code
- Android device or emulator

### Installation

1. Navigate to the mobile app directory:
```bash
cd agri-advisor/clients/mobile
```

2. Install dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
flutter run
```

### Configuration

The app connects to the backend API at `http://127.0.0.1:8000` by default. To change this:

1. Edit `lib/providers/agri_provider.dart`
2. Update the `baseUrl` constant

## Architecture

### Screens

- **Home Screen**: Welcome message, quick actions, recent queries
- **Query Screen**: Main interface for asking questions with voice/text input
- **History Screen**: View and manage query history
- **Settings Screen**: App configuration and user preferences

### Providers

- **AgriProvider**: Manages API communication and app state
- **QueryResponse**: Data model for API responses
- **Evidence**: Data model for response evidence

### Widgets

- **ResponseCard**: Displays query responses with evidence and actions
- **Voice Controls**: Speech-to-text and text-to-speech functionality

## Usage

1. **Set Location & Crop**: Configure your location and primary crop in Settings
2. **Ask Questions**: Use voice or text input to ask agricultural questions
3. **View Responses**: See AI-generated advice with evidence and confidence scores
4. **Voice Output**: Tap the speaker icon to hear responses aloud
5. **History**: Review past queries and responses

## Supported Queries

The app supports various types of agricultural queries:

- **Weather**: Rainfall, drought, temperature alerts
- **Crop Management**: Irrigation, fertilizer, pest control, planting
- **Market**: Prices, trends, mandi information
- **Finance**: Subsidies, loans, credit schemes
- **Policy**: Government schemes, eligibility, applications

## Development

### Adding New Features

1. **New Screens**: Add to `lib/screens/` and update navigation
2. **New Models**: Add to `lib/models/` for data structures
3. **New Widgets**: Add to `lib/widgets/` for reusable components
4. **API Integration**: Update `AgriProvider` for new endpoints

### Testing

```bash
# Run tests
flutter test

# Run with coverage
flutter test --coverage
```

## Dependencies

- **http**: API communication
- **provider**: State management
- **speech_to_text**: Voice input
- **flutter_tts**: Voice output
- **shared_preferences**: Local storage
- **geolocator**: Location services
- **image_picker**: Image upload (for future pest detection)

## Future Enhancements

- **Offline Mode**: Cache responses for offline access
- **Image Upload**: Pest/disease detection from photos
- **Multilingual**: Support for Indian languages
- **Push Notifications**: Weather alerts and reminders
- **SMS Integration**: Send queries via SMS
- **Voice Commands**: Hands-free operation

## Troubleshooting

### Common Issues

1. **API Connection**: Ensure the backend server is running
2. **Voice Permissions**: Grant microphone permissions for voice input
3. **Location Services**: Enable location for personalized advice
4. **Network**: Check internet connection for API calls

### Debug Mode

```bash
flutter run --debug
```

## Contributing

1. Follow Flutter coding standards
2. Add tests for new features
3. Update documentation
4. Test on both Android and iOS
