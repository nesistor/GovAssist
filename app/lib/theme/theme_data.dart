import 'package:flutter/material.dart';

ThemeData appThemeData = ThemeData(
  scaffoldBackgroundColor: Colors.black,
  // Czarny kolor tła dla całej aplikacji
  fontFamily: 'Montserrat',
  // Czcionka dla aplikacji
  appBarTheme: const AppBarTheme(
    backgroundColor: Colors.deepPurple, // Fioletowy AppBar
  ),
  textTheme: const TextTheme(
    headlineLarge: TextStyle(
      fontSize: 36,
      color: Colors.white,
      fontWeight: FontWeight.bold,
    ),
    headlineMedium: TextStyle(
      fontSize: 24,
      color: Colors.white,
      fontWeight: FontWeight.bold,
    ),
    headlineSmall: TextStyle(
      fontSize: 18,
      color: Colors.white,
    ),
    bodyLarge: TextStyle(
      fontSize: 18,
      color: Colors.white,
      fontWeight: FontWeight.w500,
    ),
    bodyMedium: TextStyle(
      fontSize: 16,
      color: Colors.white,
      fontWeight: FontWeight.w400,
    ),
    bodySmall: TextStyle(
      fontSize: 14,
      color: Colors.white70,
      fontWeight: FontWeight.w400,
    ),
  ),
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
  useMaterial3: true,
  // Użycie Material Design 3
  // Definicja szarego koloru, który będzie używany w ChatBubble
  cardColor: Colors.grey[800], // Kolor szarego tła podobny do ChatBubble
);
