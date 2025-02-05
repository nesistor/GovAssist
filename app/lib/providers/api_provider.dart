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

  Future<void> uploadDocument(Uint8List fileBytes, String fileName) async {
  var url = Uri.parse('https://government-assistant-api-183025368636.us-central1.run.app/validate-document');
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

      String resultMessage = responseData['content'] ?? 'No content available';
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
  var url = Uri.parse('https://government-assistant-api-183025368636.us-central1.run.app/generate-response');
  
  try {
    _setLoading(true);
    
    // Add the user's message to the list
    _addMessage(Message(message: question, isUserMessage: true));
    
    var response = await http.post(
      url,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: json.encode({
        'user_id': "1",  // Always send user_id as 1
        'question': question
      }),
    );

    if (response.statusCode == 200) {
      var responseBody = utf8.decode(response.bodyBytes);
      var responseData = json.decode(responseBody);

      String serverResponse = responseData;
      print("Assistant's response: $serverResponse");  // Debug print to confirm message

      // Add assistant's response to the message list
      _addMessage(Message(
        message: serverResponse,
        isUserMessage: false,
        isMarkdown: true,
      ));
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
