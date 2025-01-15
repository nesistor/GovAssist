import 'package:flutter/material.dart';

class ButtonRow extends StatelessWidget {
  final void Function(String) onButtonPressed;

  const ButtonRow({Key? key, required this.onButtonPressed}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildButton(context, 'Driving License'),
          _buildButton(context, 'ID'),
          _buildButton(context, 'Passport'),
          _buildButton(context, 'Something else?'),
        ],
      ),
    );
  }

  Widget _buildButton(BuildContext context, String text) {
    return ElevatedButton(
      onPressed: () => onButtonPressed(text),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.grey[800], // Same color as the chat bubbles
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      ),
      child: Text(
        text,
        style: const TextStyle(color: Colors.white),
      ),
    );
  }
}
