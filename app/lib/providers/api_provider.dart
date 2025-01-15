import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'package:http_parser/http_parser.dart';

import '../models/models.dart';

class ApiProvider with ChangeNotifier {
  final List<Message> _messages = [];
  bool _isLoading = false;
  String _initialMessage = '';

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  String get initialMessage => _initialMessage;

  ApiProvider() {
    _fetchInitialMessage(); // Fetch the initial message when ApiProvider is created
  }

  Future<void> _fetchInitialMessage() async {
    var url = Uri.parse('https://government-assistant-api-183025368636.us-central1.run.app/initial-message');
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
  
  Future<void> generateResponse(String question) async {
    var url = Uri.parse('https://government-assistant-api-183025368636.us-central1.run.app/generate-response');
    try {
      _setLoading(true);
      _addMessage(Message(message: question, isUserMessage: true));

      var response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: json.encode({'question': question}),
      );

      if (response.statusCode == 200) {
        var responseBody = utf8.decode(response.bodyBytes);
        var responseData = json.decode(responseBody);

        if (responseData is List && responseData.isNotEmpty) {
          String serverResponse = responseData[0];
          _addMessage(Message(
            message: serverResponse,
            isUserMessage: false,
            isMarkdown: true,
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
}
