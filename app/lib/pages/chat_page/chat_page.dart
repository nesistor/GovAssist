import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:government_assistant/providers/api_provider.dart';
import 'package:government_assistant/pages/chat_page/widgets/side_bar.dart';
import 'package:government_assistant/pages/chat_page/widgets/chat_bubble.dart';
import 'package:government_assistant/pages/chat_page/widgets/button_row.dart';
import 'package:government_assistant/pages/chat_page/widgets/input_widget.dart';
import 'package:government_assistant/pages/chat_page/widgets/login_button.dart';
import 'package:government_assistant/pages/login_page/login_page.dart';
import 'package:government_assistant/pages/chat_page/widgets/new_chat_button.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data';

class ChatPage extends StatelessWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context) {
    bool isMobile = MediaQuery
        .of(context)
        .size
        .width < 600;

    return Scaffold(
      appBar: null,
      body: Stack(
        children: [
          isMobile
              ? _MobileLayout()
              : _DesktopLayout(),
          Positioned(
            top: 16.0,
            right: 16.0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const NewChatButton(),
                const SizedBox(width: 10),
                const LoginSignupButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MobileLayout extends StatefulWidget {
  const _MobileLayout({super.key});

  @override
  State<_MobileLayout> createState() => _MobileLayoutState();
}

class _MobileLayoutState extends State<_MobileLayout> {
  // Początkowy stan: Sidebar jest zamknięty
  bool isSidebarOpen = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Otwieranie bocznego paska przez przycisk
      drawer: const SideBar(), // Dodajemy boczny pasek jako drawer
      body: Stack(
        children: [
          // Główna zawartość ekranu
          Row(
            children: [
              // Sidebar: widoczny tylko gdy isSidebarOpen jest true
              if (isSidebarOpen) const SideBar(),
              Expanded(child: ChatBody()),
            ],
          ),
          // Przywracamy poprzednią ikonę menu, która była na górze ekranu
          Positioned(
            left: 10,
            top: 10, // Ustawiłem ikonę na samą górę ekranu
            child: IconButton(
              icon: Icon(
                isSidebarOpen ? Icons.close : Icons.menu, // Ikona menu
                color: Colors.white,
                size: 30,
              ),
              onPressed: () {
                setState(() {
                  // Zmiana stanu: otwieranie lub zamykanie sidebaru
                  isSidebarOpen = !isSidebarOpen;
                });
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _DesktopLayout extends StatelessWidget {
  const _DesktopLayout({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: const [
        // Na większych ekranach Sidebar jest zawsze widoczny
        SideBar(),
        Expanded(child: ChatBody()),
      ],
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
  final ScrollController _scrollController = ScrollController();

  void _sendMessage() async {
    if (_controller.text
        .trim()
        .isEmpty) return;

    final apiProvider = Provider.of<ApiProvider>(context, listen: false);
    await apiProvider.generateResponse(_controller.text);

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

  void _handleFileAttachment() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx'],
    );

    if (result != null) {
      Uint8List fileBytes = result.files.first.bytes!;
      String fileName = result.files.first.name;

      final apiProvider = Provider.of<ApiProvider>(context, listen: false);
      await apiProvider.uploadDocument(fileBytes, fileName);

      _scrollToBottom();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No file selected')),
      );
    }
  }

  void _handleButtonPress(String text) {
    _controller.text = text;
    _sendMessage();
  }

  @override
  Widget build(BuildContext context) {
    final apiProvider = Provider.of<ApiProvider>(context);

    // Sprawdzamy, czy urządzenie jest mobilne
    bool isMobile = MediaQuery
        .of(context)
        .size
        .width < 600;

    return Column(
      children: [
        if (apiProvider.initialMessage.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(
              top: 100.0,
              left: 16.0,
              right: 16.0,
              bottom: 8.0,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ChatBubble(
                  message: apiProvider.initialMessage,
                  isUserMessage: false,
                  isMarkdown: false,
                ),
                const SizedBox(height: 4),
                ButtonRow(onButtonPressed: _handleButtonPress),
              ],
            ),
          ),
        Expanded(
          child: Scrollbar(
            controller: _scrollController,
            thumbVisibility: true,
            child: ListView.builder(
              controller: _scrollController,
              itemCount: apiProvider.messages.length,
              itemBuilder: (context, index) {
                final message = apiProvider.messages[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: ChatBubble(
                    message: message.message,
                    isUserMessage: message.isUserMessage,
                    isMarkdown: message.isMarkdown,
                  ),
                );
              },
            ),
          ),
        ),
        if (apiProvider.isLoading)
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Theme
                        .of(context)
                        .colorScheme
                        .primary,
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  "Loading...",
                  style: Theme
                      .of(context)
                      .textTheme
                      .bodyMedium,
                ),
              ],
            ),
          ),
        Padding(
          // Zmieniamy padding w zależności od urządzenia
          padding: EdgeInsets.symmetric(
            horizontal: isMobile
                ? 8.0
                : 66.0, // Mniejszy padding na urządzeniach mobilnych
          ),
          child: InputWidget(
            controller: _controller,
            onSendMessage: _sendMessage,
            onFileAttachment: _handleFileAttachment,
          ),
        ),
      ],
    );
  }
}
