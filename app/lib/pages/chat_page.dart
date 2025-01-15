import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/api_provider.dart';
import '../widgets/chat_bubble.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data'; 

class ChatPage extends StatelessWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'GovAssist',
          style: TextStyle(
            color: Colors.white, 
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.grey[800], 
        centerTitle: true,
        elevation: 0, 
      ),
      body: const ChatBody(),
    );
  }
}

class ChatBody extends StatefulWidget {
  const ChatBody({super.key});

  @override
  State<ChatBody> createState() => _ChatBodyState();
}

class _ChatBodyState extends State<ChatBody> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController(); // Scroll controller for managing scrolling

  void _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    final apiProvider = Provider.of<ApiProvider>(context, listen: false);
    await apiProvider.generateResponse(_controller.text);

    // Automatically scroll to the bottom after a new message is added
    _scrollToBottom();
    _controller.clear();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final apiProvider = Provider.of<ApiProvider>(context);

    return Column(
      children: [
        Expanded(
          child: Scrollbar( // Adds a visible scrollbar for desktop-style scrolling
            controller: _scrollController,
            thumbVisibility: true, // Ensure the scrollbar thumb is always visible
            child: ListView.builder(
              controller: _scrollController, // Attach the ScrollController
              itemCount: apiProvider.messages.length,
              itemBuilder: (context, index) {
                final message = apiProvider.messages[index];
                return ChatBubble(
                  message: message.message,
                  isUserMessage: message.isUserMessage,
                  isMarkdown: message.isMarkdown,
                );
              },
            ),
          ),
        ),
        if (apiProvider.isLoading) // Show the loading indicator
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
                SizedBox(width: 10),
                Text("Loading...", style: TextStyle(color: Colors.white)),
              ],
            ),
          ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.attach_file, color: Colors.white),
                onPressed: () {
                  // Add your document attachment function here
                },
              ),
              Expanded(
                child: TextField(
                  controller: _controller,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    hintText: 'Type your message...',
                    hintStyle: TextStyle(color: Colors.white),
                    border: OutlineInputBorder(),
                    filled: true,
                    fillColor: Colors.black,
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: _sendMessage,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
