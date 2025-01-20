import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart'; // Import Firebase core
import 'firebase_options.dart'; // Import Firebase options
import 'providers/api_provider.dart';
import 'pages/chat_page/chat_page.dart';
import 'theme/theme_data.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform, // Use platform-specific Firebase options
  );
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<ApiProvider>(
      create: (_) => ApiProvider(),
      child: MaterialApp(
        title: 'GovAssist',
        theme: appThemeData, // Using ThemeData from theme_data.dart
        home: const ChatPage(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
