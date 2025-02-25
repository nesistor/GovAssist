import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'providers/api_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/auth_provider.dart';
import 'package:government_assistant/pages//chat_page/chat_page.dart';
import 'theme/theme_data.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    print('Firebase został poprawnie zainicjalizowany!');
  } catch (e) {
    print('Błąd inicjalizacji Firebase: $e');
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => ApiProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),

      ],
      child: MaterialApp(
        title: 'GovAssist',
        theme: appThemeData,
        home: const ChatPage(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}