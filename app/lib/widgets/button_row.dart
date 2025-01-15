import 'package:flutter/material.dart';

class ButtonRow extends StatelessWidget {
  final Function(String) onButtonPressed;

  const ButtonRow({Key? key, required this.onButtonPressed}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 10.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,  // This will center the buttons
        children: [
          ElevatedButton(
            onPressed: () => onButtonPressed("Driving License"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              minimumSize: const Size(100, 40), // Square button dimensions
            ),
            child: const Text("Driving License", style: TextStyle(color: Colors.white)),
          ),
          const SizedBox(width: 10),
          ElevatedButton(
            onPressed: () => onButtonPressed("ID"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              minimumSize: const Size(100, 40),
            ),
            child: const Text("ID", style: TextStyle(color: Colors.white)),
          ),
          const SizedBox(width: 10),
          ElevatedButton(
            onPressed: () => onButtonPressed("Passport"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              minimumSize: const Size(100, 40),
            ),
            child: const Text("Passport", style: TextStyle(color: Colors.white)),
          ),
          const SizedBox(width: 10),
          ElevatedButton(
            onPressed: () => onButtonPressed("Social Benefits"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              minimumSize: const Size(100, 40),
            ),
            child: const Text("Social Benefits", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
