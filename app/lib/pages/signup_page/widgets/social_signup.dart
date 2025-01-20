import 'package:flutter/material.dart';

import 'package:government_assistant/pages/signup_page/widgets/or_divider.dart';
import 'package:government_assistant/pages/signup_page/widgets/social_icon.dart';

class SocalSignUp extends StatelessWidget {
  const SocalSignUp({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const OrDivider(),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SocialIcon(
              iconSrc: "assets/icons/facebook_white.svg",
              press: () {},
            ),
            SocialIcon(
              iconSrc: "assets/icons/twitter-x_white.svg",
              press: () {},
            ),
            SocialIcon(
              iconSrc: "assets/icons/google-plus_white.svg",
              press: () {},
            ),
          ],
        ),
      ],
    );
  }
}
