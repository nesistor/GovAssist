import 'package:flutter/material.dart';

class ButtonRow extends StatelessWidget {
  final Function(String) onButtonPressed;

  const ButtonRow({Key? key, required this.onButtonPressed}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Określenie, czy urządzenie jest mobilne
    bool isMobile = MediaQuery
        .of(context)
        .size
        .width < 600;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 10.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        // Wyrównanie przycisków do lewej
        children: [
          _buildButton(context, "Driving License"),
          const SizedBox(width: 10),
          _buildButton(context, "ID"),
          const SizedBox(width: 10),
          _buildButton(context, "Passport"),
          const SizedBox(width: 10),
          _buildButton(context, "Social Benefits"),
        ],
      ),
    );
  }

  // Funkcja pomocnicza do tworzenia przycisków
  Widget _buildButton(BuildContext context, String label) {
    bool isMobile = MediaQuery
        .of(context)
        .size
        .width < 600;

    return Expanded(
      flex: isMobile ? 1 : 0,
      // Na urządzeniach mobilnych przyciski zajmują równą szerokość
      child: ElevatedButton(
        onPressed: () => onButtonPressed(label),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.grey[800],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          minimumSize: Size(isMobile ? double.infinity : 150, 40),
          // Równa szerokość na urządzeniach mobilnych
          padding: EdgeInsets.zero, // Usunięcie domyślnego paddingu
        ),
        child: Container(
          height: 40, // Ustalona wysokość dla przycisków
          alignment: Alignment.center, // Wyśrodkowanie tekstu
          child: Text(
            label,
            style: const TextStyle(color: Colors.white),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}
