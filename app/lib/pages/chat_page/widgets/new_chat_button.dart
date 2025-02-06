import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:government_assistant/providers/api_provider.dart';

class NewChatButton extends StatelessWidget {
  const NewChatButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () {
        // Trigger startNewChat to reset the chat
        final apiProvider = Provider.of<ApiProvider>(context, listen: false);
        apiProvider.startNewChat();
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: Theme
            .of(context)
            .scaffoldBackgroundColor,
        side: BorderSide(color: Colors.white), // White border
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20), // Rounded corners
        ),
        padding: const EdgeInsets.symmetric(
            horizontal: 16, vertical: 12), // Adjust button size
      ),
      child: Row(
        children: [
          Icon(
            Icons.add_comment, // The icon for 'New Chat'
            color: Colors.white,
          ),
          const SizedBox(width: 8),
          Text(
            'New Chat',
            style: TextStyle(
              color: Colors.white, // White text
              fontSize: 18, // Adjust font size
            ),
          ),
        ],
      ),
    );
  }
}
