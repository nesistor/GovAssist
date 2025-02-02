import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:government_assistant/providers/api_provider.dart';

class NewChatButton extends StatelessWidget {
  const NewChatButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 16.0,
      left: 16.0, // Positioned on the left side
      child: ElevatedButton(
        onPressed: () {
          // Trigger startNewChat to reset the chat
          Provider.of<ApiProvider>(context, listen: false).startNewChat();
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme
              .of(context)
              .colorScheme
              .primary, // Adjust background color
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
      ),
    );
  }
}
