import 'package:flutter/material.dart';
import 'package:government_assistant/pages/login_page/login_page.dart';

class LoginSignupButton extends StatelessWidget {
  const LoginSignupButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 16.0, // Odstęp od góry
      right: 16.0, // Odstęp od prawej strony
      child: ElevatedButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const LoginPage()),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme
              .of(context)
              .scaffoldBackgroundColor, // Tło czarne
          side: BorderSide(color: Colors.white), // Białe obramowanie
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20), // Zaokrąglone rogi
          ),
          padding: const EdgeInsets.symmetric(
              horizontal: 32, vertical: 12), // Wymiary przycisku
        ),
        child: Text(
          'Login',
          style: TextStyle(
            color: Colors.white, // Kolor tekstu na biały
            fontSize: 18, // Dopasowanie rozmiaru czcionki
          ),
        ),
      ),
    );
  }
}
