import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/agri_provider.dart';
import '../l10n/app_localizations.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final t = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(t.settingsTitle),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: Consumer<AgriProvider>(
        builder: (context, provider, child) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Profile Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.profile,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Location Information (auto-detected)
                      ListTile(
                        leading: const Icon(Icons.location_on),
                        title: Text(t.currentLocation),
                        subtitle: Text(provider.userLocation ?? 'Auto-detecting...'),
                        trailing: const Icon(Icons.gps_fixed, color: Colors.green),
                        onTap: null, // Disabled since location is auto-detected
                      ),
                      
                      // Crop Setting
                      ListTile(
                        leading: const Icon(Icons.agriculture),
                        title: Text(t.primaryCrop),
                        subtitle: Text(provider.userCrop ?? 'Not set'),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          _showCropDialog(context, provider);
                        },
                      ),
                      const SizedBox(height: 8),
                      ListTile(
                        leading: const Icon(Icons.language),
                        title: Text(t.language),
                        subtitle: Text(_languageName(provider.languageCode)),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () => _showLanguageDialog(context, provider),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // App Settings
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.appSettings,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Voice Settings
                      SwitchListTile(
                        title: Text(t.voiceInput),
                        subtitle: Text(t.voiceInputSubtitle),
                        value: true, // TODO: Implement voice settings
                        onChanged: (value) {
                          // TODO: Save voice setting
                        },
                      ),
                      
                      SwitchListTile(
                        title: Text(t.voiceOutput),
                        subtitle: Text(t.voiceOutputSubtitle),
                        value: true, // TODO: Implement voice settings
                        onChanged: (value) {
                          // TODO: Save voice setting
                        },
                      ),
                      
                      SwitchListTile(
                        title: Text(t.offlineMode),
                        subtitle: Text(t.offlineModeSubtitle),
                        value: false, // TODO: Implement offline mode
                        onChanged: (value) {
                          // TODO: Save offline setting
                        },
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Data Management
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.dataManagement,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      ListTile(
                        leading: const Icon(Icons.clear_all),
                        title: Text(t.clearQueryHistory),
                        subtitle: Text(t.deleteAllStoredQueries),
                        onTap: () {
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: Text(t.clearHistory),
                              content: Text(t.areYouSureClearHistory),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context),
                                  child: Text(t.cancel),
                                ),
                                TextButton(
                                  onPressed: () {
                                    provider.clearHistory();
                                    Navigator.pop(context);
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text(t.historyCleared)),
                                    );
                                  },
                                  child: Text(t.clear),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // About Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.about,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      ListTile(
                        leading: const Icon(Icons.info),
                        title: Text(t.version),
                        subtitle: const Text('1.0.0'),
                      ),
                      
                      ListTile(
                        leading: const Icon(Icons.description),
                        title: Text(t.privacyPolicy),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          // TODO: Show privacy policy
                        },
                      ),
                      
                      ListTile(
                        leading: const Icon(Icons.help),
                        title: Text(t.helpSupport),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          // TODO: Show help
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }



  void _showCropDialog(BuildContext context, AgriProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(AppLocalizations.of(context).selectPrimaryCrop),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView(
            shrinkWrap: true,
            children: [
              'wheat', 'rice', 'cotton', 'maize',
              'pulses', 'sugarcane', 'groundnut'
            ].map((crop) => ListTile(
              title: Text(crop),
              onTap: () {
                provider.setUserCrop(crop);
                Navigator.pop(context);
              },
            )).toList(),
          ),
        ),
      ),
    );
  }

  void _showLanguageDialog(BuildContext context, AgriProvider provider) {
    final t = AppLocalizations.of(context);
    final languages = <String, String>{
      'en': 'English',
      'hi': 'हिंदी',
      'ta': 'தமிழ்',
      'te': 'తెలుగు',
      'bn': 'বাংলা',
      'mr': 'मराठी',
      'kn': 'ಕನ್ನಡ',
      'gu': 'ગુજરાતી',
      'pa': 'ਪੰਜਾਬੀ',
      'ml': 'മലയാളം',
    };
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(t.selectLanguage),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView(
            shrinkWrap: true,
            children: languages.entries.map((e) => RadioListTile<String>(
              value: e.key,
              groupValue: provider.languageCode,
              onChanged: (val) async {
                if (val != null) {
                  await provider.setLanguageCode(val);
                  if (context.mounted) Navigator.pop(context);
                }
              },
              title: Text(e.value),
            )).toList(),
          ),
        ),
      ),
    );
  }

  String _languageName(String code) {
    const map = {
      'en': 'English',
      'hi': 'हिंदी',
      'ta': 'தமிழ்',
      'te': 'తెలుగు',
      'bn': 'বাংলা',
      'mr': 'मराठी',
      'kn': 'ಕನ್ನಡ',
      'gu': 'ગુજરાતી',
      'pa': 'ਪੰਜਾਬੀ',
      'ml': 'മലയാളം',
    };
    return map[code] ?? code;
  }
}
