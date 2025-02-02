import 'package:flutter/material.dart';

class InputWidget extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSendMessage;
  final VoidCallback onFileAttachment;

  const InputWidget({
    Key? key,
    required this.controller,
    required this.onSendMessage,
    required this.onFileAttachment,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Container(
        decoration: BoxDecoration(
          color: Theme
              .of(context)
              .cardColor,
          borderRadius: BorderRadius.circular(25),
        ),
        child: Row(
          children: [
            // File attachment button
            IconButton(
              icon: const Icon(Icons.attach_file),
              color: Colors.white,
              iconSize: 20.0,
              onPressed: onFileAttachment,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextField(
                controller: controller,
                style: Theme
                    .of(context)
                    .textTheme
                    .bodyMedium,
                onSubmitted: (_) => onSendMessage(),
                // Enter to send message
                maxLines: null,
                decoration: InputDecoration(
                  hintText: 'Message Government Assistant',
                  hintStyle: Theme
                      .of(context)
                      .textTheme
                      .bodySmall,
                  filled: true,
                  fillColor: Colors.transparent,
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    vertical: 16,
                    horizontal: 16,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // Send button
            IconButton(
              icon: const Icon(Icons.send),
              color: Colors.white,
              onPressed: onSendMessage,
            ),
          ],
        ),
      ),
    );
  }
}
