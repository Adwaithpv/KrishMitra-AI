import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/agri_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
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
                      const Text(
                        'Profile',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Location Information (auto-detected)
                      ListTile(
                        leading: const Icon(Icons.location_on),
                        title: const Text('Current Location'),
                        subtitle: Text(provider.userLocation ?? 'Auto-detecting...'),
                        trailing: const Icon(Icons.gps_fixed, color: Colors.green),
                        onTap: null, // Disabled since location is auto-detected
                      ),
                      
                      // Crop Setting
                      ListTile(
                        leading: const Icon(Icons.agriculture),
                        title: const Text('Primary Crop'),
                        subtitle: Text(provider.userCrop ?? 'Not set'),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          _showCropDialog(context, provider);
                        },
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
                      const Text(
                        'App Settings',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Voice Settings
                      SwitchListTile(
                        title: const Text('Voice Input'),
                        subtitle: const Text('Enable speech-to-text'),
                        value: true, // TODO: Implement voice settings
                        onChanged: (value) {
                          // TODO: Save voice setting
                        },
                      ),
                      
                      SwitchListTile(
                        title: const Text('Voice Output'),
                        subtitle: const Text('Enable text-to-speech'),
                        value: true, // TODO: Implement voice settings
                        onChanged: (value) {
                          // TODO: Save voice setting
                        },
                      ),
                      
                      SwitchListTile(
                        title: const Text('Offline Mode'),
                        subtitle: const Text('Use cached responses when offline'),
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
                      const Text(
                        'Data Management',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      ListTile(
                        leading: const Icon(Icons.clear_all),
                        title: const Text('Clear Query History'),
                        subtitle: const Text('Delete all stored queries'),
                        onTap: () {
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('Clear History'),
                              content: const Text('Are you sure you want to clear all query history?'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed: () {
                                    provider.clearHistory();
                                    Navigator.pop(context);
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('History cleared')),
                                    );
                                  },
                                  child: const Text('Clear'),
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
                      const Text(
                        'About',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      ListTile(
                        leading: const Icon(Icons.info),
                        title: const Text('Version'),
                        subtitle: const Text('1.0.0'),
                      ),
                      
                      ListTile(
                        leading: const Icon(Icons.description),
                        title: const Text('Privacy Policy'),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () {
                          // TODO: Show privacy policy
                        },
                      ),
                      
                      ListTile(
                        leading: const Icon(Icons.help),
                        title: const Text('Help & Support'),
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
        title: const Text('Select Primary Crop'),
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
}
