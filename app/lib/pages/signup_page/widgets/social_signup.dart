import 'package:flutter/material.dart';
import 'package:government_assistant/pages/signup_page/widgets/or_divider.dart';
import 'package:government_assistant/pages/signup_page/widgets/social_icon.dart'; // Import the SocialIcon widget
import 'package:government_assistant/providers/auth_provider.dart'; // Import the AuthProvider
import 'package:provider/provider.dart';

class SocialSignUp extends StatelessWidget {
  const SocialSignUp({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Column(
      children: [
        const OrDivider(),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SocialIcon(
              iconSrc: "assets/icons/facebook_white.svg",
              press: () async {
                // Call signInWithFacebook method from AuthProvider for signup
                //  await authProvider.signInWithFacebook(context);
              },
            ),
            SocialIcon(
              iconSrc: "assets/icons/google-plus_white.svg",
              press: () async {
                // Call signInWithGoogle method from AuthProvider for signup
                await authProvider.signInWithGoogle(context);
              },
            ),
          ],
        ),
      ],
    );
  }
}
