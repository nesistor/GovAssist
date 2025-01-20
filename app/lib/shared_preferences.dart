import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferencesHelper {
  // Method to save user token to SharedPreferences
  static Future<void> saveUserToken(String token) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString("user_token", token);
  }

  // Method to retrieve user token from SharedPreferences
  static Future<String?> getUserToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("user_token");
  }

  static Future<void> checkSignedIn(
      Function(bool) onSignedInStatusChanged) async {
    SharedPreferences s = await SharedPreferences.getInstance();
    bool _isSignedIn = s.getBool("is_signed_in") ?? false;
    onSignedInStatusChanged(_isSignedIn);
  }

  static Future<void> setSignIn(bool isSignedIn) async {
    SharedPreferences s = await SharedPreferences.getInstance();
    s.setBool("is_signed_in", isSignedIn);
  }
}