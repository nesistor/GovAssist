import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/api_provider.dart';
import 'pages/chat_page/chat_page.dart';
import 'package:government_assistant/theme/theme_data.dart';

void main() {
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
        theme: appThemeData, // Używamy ThemeData z theme_data.dart
        home: const ChatPage(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
