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
  List<String> _options = [];

  List<Message> get messages => _messages;

  List<String> get conversationTitles => _conversationTitles;

  bool get isLoading => _isLoading;

  String get initialMessage => _initialMessage;

  List<String> get options => _options;

  ApiProvider() {
    _fetchInitialMessage(); // Fetch the initial message when ApiProvider is created
  }


  // Add this method to clear the chat
  void startNewChat() {
    _messages.clear();
    _initialMessage = '';
    _isLoading = false;
    _fetchInitialMessage(); // Add this line to fetch the initial message again
    fetchOptions(); // Add this line to fetch options again
    notifyListeners(); // Notify listeners to rebuild UI
  }


  Future<void> fetchConversationTitles(String timeRange) async {
    _isLoading = true;
    notifyListeners();

    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/conversation-title?timeRange=$timeRange');

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
          conversationTitles.clear();
          for (var item in responseData) {
            if (item is Map<String, dynamic> && item.containsKey('title')) {
              conversationTitles.add(item['title']);
            }
          }
          _isLoading = false;
          notifyListeners();
        }
      } else {
        throw Exception('Failed to fetch conversation titles');
      }
    } catch (e) {
      print('Error fetching conversation titles: $e');
      _isLoading = false;
      notifyListeners();
    }
  }



  Future<void> _fetchInitialMessage() async {
    String? uid = await SharedPreferencesHelper.getUserUid();

    var uri = Uri.parse('http://127.0.0.1:8000/initial-message');
    var url = uri.replace(queryParameters: {'uid': uid ?? ''});

    try {
      var response = await http.get(url);
      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);

        // Decode the JSON response
        var responseData = json.decode(responseBody);

        // Assuming the response contains a field 'message'
        if (responseData.containsKey('message')) {
          // Extract the message and clean it (remove quotes and extra characters)
          _initialMessage = responseData['message']?.toString().trim() ??
              'No message available';

          // Remove the <|eos|> if it exists
          _initialMessage = _initialMessage.replaceAll('<|eos|>', '').trim();
        } else {
          _initialMessage = 'No message found in the response';
        }
        notifyListeners();
      } else {
        throw Exception('Failed to fetch initial message');
      }
    } catch (e) {
      _initialMessage = 'Error fetching initial message: $e';
      notifyListeners();
    }
  }


  Future<void> fetchOptions() async {
    var url = Uri.parse(
        'https://government-assistant-api-183025368636.us-central1.run.app/options');
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

        if (responseData is Map && responseData.containsKey('options')) {
          // Set your options here
          List<String> options = List<String>.from(responseData['options']);
          _options = options; // This should work now
          notifyListeners();
        }
      } else {
        throw Exception('Failed to fetch options');
      }
    } catch (e) {
      print('Error fetching options: $e');
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

      String? token = await SharedPreferencesHelper.getUserToken();
      String? uid = await SharedPreferencesHelper.getUserUid();

      print("Sending request as ${uid ?? 'Guest'}");

      _addMessage(Message(message: question, isUserMessage: true));

      var headers = {'Content-Type': 'application/json; charset=utf-8'};

      // Add Authorization header only if token exists (for authenticated users)
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      var response = await http.post(
        url,
        headers: headers,
        body: json.encode({
          'uid': uid ?? '',
          // Send uid even if user is guest, but no token needed
          'question': question,
        }),
      );

      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);
        var responseData = json.decode(responseBody);

        if (responseData.containsKey('response')) {
          _addMessage(Message(
            message: responseData['response'],
            isUserMessage: false,
            isMarkdown: true,
          ));
        } else {
          _addMessage(Message(
            message: 'No valid response received',
            isUserMessage: false,
          ));
        }
      } else {
        _addMessage(Message(
          message: 'Server error: ${response.reasonPhrase}',
          isUserMessage: false,
        ));
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
