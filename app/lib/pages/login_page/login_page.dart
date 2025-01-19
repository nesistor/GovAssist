import 'package:flutter/material.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text(
          'Login / Signup Page Content Here',
          style: Theme
              .of(context)
              .textTheme
              .bodyLarge,
        ),
      ),
    );
  }
}
