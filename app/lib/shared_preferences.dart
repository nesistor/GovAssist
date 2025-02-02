import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferencesHelper {
  static const String _userTokenKey = 'userToken';
  static const String _userUidKey = 'userUid'; // Klucz dla UID

  // Zapisywanie tokenu
  static Future<void> saveUserToken(String token) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userTokenKey, token);
  }

  // Zapisywanie UID
  static Future<void> saveUserUid(String uid) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userUidKey, uid);
  }

  // Pobieranie tokenu
  static Future<String?> getUserToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString(_userTokenKey);
  }

  // Pobieranie UID
  static Future<String?> getUserUid() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString(_userUidKey);
  }

  // Czyszczenie tokenu
  static Future<void> clearUserToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userTokenKey);
    await prefs.remove(_userUidKey); // Usuwamy również UID
  }

  // Sprawdzanie statusu zalogowania
  static Future<void> checkSignedIn(Function(bool) onSignedInStatusChanged) async {
    SharedPreferences s = await SharedPreferences.getInstance();
    bool _isSignedIn = s.getBool("is_signed_in") ?? false;
    onSignedInStatusChanged(_isSignedIn);
  }

  // Zapisz status zalogowania
  static Future<void> setSignIn(bool isSignedIn) async {
    SharedPreferences s = await SharedPreferences.getInstance();
    s.setBool("is_signed_in", isSignedIn);
  }
}
