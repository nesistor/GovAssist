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
      // Zmniejszenie marginesu
      child: Container(
        decoration: BoxDecoration(
          color: Theme
              .of(context)
              .cardColor, // Szary kolor tła
          borderRadius: BorderRadius.circular(25), // Zaokrąglone rogi
        ),
        child: Row(
          children: [
            // Ikona załączania pliku wewnątrz pola tekstowego
            Container(
              decoration: BoxDecoration(
                color: Colors.transparent,
              ),
              child: IconButton(
                icon: const Icon(Icons.attach_file),
                color: Colors.white, // Biała ikona
                iconSize: 20.0, // Zmniejszenie ikony
                onPressed: onFileAttachment,
              ),
            ),
            const SizedBox(width: 8),
            // Węższy TextField
            Expanded(
              child: TextField(
                controller: controller,
                style: Theme
                    .of(context)
                    .textTheme
                    .bodyMedium,
                onSubmitted: (_) => onSendMessage(),
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
                    vertical: 16, // Wysokość inputa
                    horizontal: 16, // Odstępy wewnętrzne
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // Ikona wysyłania wiadomości wewnątrz pola tekstowego
            Container(
              decoration: BoxDecoration(
                color: Colors.transparent,
              ),
              child: IconButton(
                icon: const Icon(Icons.send),
                color: Colors.white,
                onPressed: onSendMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
