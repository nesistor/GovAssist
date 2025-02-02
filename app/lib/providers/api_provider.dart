import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'package:http_parser/http_parser.dart';
import 'package:government_assistant/shared_preferences.dart';

import '../models/models.dart';

class ApiProvider with ChangeNotifier {
  final List<Message> _messages = [];
  final List<String> _conversationTitles = [];
  bool _isLoading = false;
  String _initialMessage = '';

  List<Message> get messages => _messages;

  List<String> get conversationTitles => _conversationTitles;

  bool get isLoading => _isLoading;

  String get initialMessage => _initialMessage;

  ApiProvider() {
    _fetchInitialMessage(); // Fetch the initial message when ApiProvider is created
  }


  // Add this method to clear the chat
  void startNewChat() {
    _messages.clear();
    _initialMessage = '';
    _isLoading = false;
    notifyListeners(); // Notify listeners to rebuild UI
  }


  Future<void> fetchConversationTitles() async {
    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/conversation-title');
    try {
      String? token = await SharedPreferencesHelper.getUserToken();
      String? uid = await SharedPreferencesHelper.getUserUid();

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
          _conversationTitles.clear();
          for (var item in responseData) {
            if (item is Map<String, dynamic> && item.containsKey('title')) {
              _conversationTitles.add(item['title']);
            }
          }
          notifyListeners();
        }
      } else {
        throw Exception('Failed to fetch conversation titles');
      }
    } catch (e) {
      print('Error fetching conversation titles: $e');
    }
  }


  Future<void> _fetchInitialMessage() async {
    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/initial-message');
    try {
      var response = await http.get(url);
      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);

        // Remove the quotes from the initial message
        _initialMessage = responseBody.replaceAll('"', '').trim();

        notifyListeners();
      } else {
        throw Exception('Failed to fetch initial message');
      }
    } catch (e) {
      _initialMessage = 'Error fetching initial message: $e';
      notifyListeners();
    }
  }

  Future<void> uploadDocument(Uint8List fileBytes, String fileName) async {
    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/validate-document');
    try {
      _setLoading(true); // Set loading state to true
      String mimeType = _detectMimeType(fileName);

      var request = http.MultipartRequest('POST', url);
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: fileName,
        contentType: MediaType.parse(mimeType),
      ));

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);
        var responseData = json.decode(responseBody);

        String resultMessage = responseData['content'] ??
            'No content available';
        _addMessage(Message(
          message: resultMessage,
          isUserMessage: false,
          isMarkdown: true,
        ));
      } else {
        _addMessage(Message(
          message: 'Document upload failed: ${response.reasonPhrase}',
          isUserMessage: false,
        ));
      }
    } catch (e) {
      _addMessage(Message(
        message: 'Error occurred: $e',
        isUserMessage: false,
      ));
    } finally {
      _setLoading(false); // Set loading state to false
    }
  }

  Future<void> generateResponse(String question) async {
    var url = Uri.parse('http://127.0.0.1:8000/generate-response');
    try {
      _setLoading(true);

      // Fetch token and UID from SharedPreferences
      String? token = await SharedPreferencesHelper.getUserToken();
      String? uid = await SharedPreferencesHelper.getUserUid();

      if (token == null || uid == null) {
        throw Exception('User is not authenticated');
      }

      print("Sending token: $token and UID: $uid");

      // Add user message to the list
      _addMessage(Message(message: question, isUserMessage: true));

      var response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'uid': uid,
          'question': question,
        }),
      );

      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);
        var responseData = json.decode(responseBody);

        // Print the full response data to inspect its structure
        print("Full response data: $responseData");

        // Ensure the response is not null and contains the 'response' key
        if (responseData != null && responseData.containsKey('response')) {
          var serverResponse = responseData['response'];

          // If the response is a string, process it as usual
          if (serverResponse is String) {
            print("Assistant's response: $serverResponse");
            _addMessage(Message(
              message: serverResponse,
              isUserMessage: false,
              isMarkdown: true,
            ));
          }
          // If the response is an integer, convert it to a string and process
          else if (serverResponse is int) {
            print("Assistant's response (integer): $serverResponse");
            _addMessage(Message(
              message: serverResponse.toString(),
              isUserMessage: false,
              isMarkdown: true,
            ));
          }
          // Handle other unexpected types
          else {
            _addMessage(Message(
              message: 'Unexpected response format: $serverResponse',
              isUserMessage: false,
            ));
          }
        } else {
          // Handle the case where the response does not contain the expected key
          _addMessage(Message(
            message: 'No valid response received from the server',
            isUserMessage: false,
          ));
        }
      } else {
        throw Exception('Failed to load response');
      }
    } catch (e) {
      _addMessage(Message(
        message: 'Error: $e',
        isUserMessage: false,
      ));
    } finally {
      _setLoading(false);
    }
  }


  void _addMessage(Message message) {
    _messages.add(message);
    notifyListeners();
  }

  void _setLoading(bool isLoading) {
    _isLoading = isLoading;
    notifyListeners();
  }

  String _detectMimeType(String fileName) {
    if (fileName.endsWith('.pdf')) {
      return 'application/pdf';
    } else if (fileName.endsWith('.docx')) {
      return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    } else {
      throw Exception('Unsupported file type. Only PDF and DOCX are allowed.');
    }
  }
}
