import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ChatProvider extends ChangeNotifier {
  List<String> conversationTitles = [];
  bool isLoading = false;
  int currentPage = 1;  // Page tracking
  bool hasMore = true; // Flag to indicate if more data is available

  Future<void> fetchConversationTitles({String timeRange = 'all', int page = 1}) async {
    if (isLoading || !hasMore) return;

    isLoading = true;
    notifyListeners();

    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/conversation-title?timeRange=$timeRange&page=$page');

    try {
      String? token = await _getUserToken();
      String? uid = await _getUserUid();

      if (token == null || uid == null) {
        throw Exception('User is not authenticated');
      }

      var response = await http.get(
        url,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);
        var responseData = json.decode(responseBody);

        if (responseData is List) {
          if (page == 1) {
            conversationTitles.clear();  // Clear the list on a fresh load
          }

          for (var item in responseData) {
            if (item is Map<String, dynamic> && item.containsKey('title')) {
              conversationTitles.add(item['title']);
            }
          }
          currentPage = page;
          hasMore = responseData.isNotEmpty;  // Check if there are more titles
          isLoading = false;
          notifyListeners();
        }
      } else {
        throw Exception('Failed to fetch conversation titles');
      }
    } catch (e) {
      print('Error fetching conversation titles: $e');
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> _getUserToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_token');
  }

  Future<String?> _getUserUid() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_uid');
  }
}
