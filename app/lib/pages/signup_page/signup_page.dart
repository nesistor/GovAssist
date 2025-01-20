import 'package:flutter/material.dart';
import 'package:government_assistant/constants.dart';
import 'package:government_assistant/responsive.dart';
import 'package:government_assistant/components/background.dart';
import 'package:government_assistant/pages/signup_page/widgets/signup_top_image.dart';
import 'package:government_assistant/pages/signup_page/widgets/signup_form.dart';
import 'package:government_assistant/pages/signup_page/widgets/social_signup.dart';

class SignupPage extends StatelessWidget {
  const SignupPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Background(
      child: SingleChildScrollView(
        child: Responsive(
          mobile: MobileSignupPage(),
          desktop: Row(
            children: [
              Expanded(
                child: SignUpScreenTopImage(),
              ),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 450,
                      child: SignUpForm(),
                    ),
                    SizedBox(height: defaultPadding / 2),
                    SocalSignUp()
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}

class MobileSignupPage extends StatelessWidget {
  const MobileSignupPage({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        SignUpScreenTopImage(),
        Row(
          children: [
            Spacer(),
            Expanded(
              flex: 8,
              child: SignUpForm(),
            ),
            Spacer(),
          ],
        ),
        const SocalSignUp()
      ],
    );
  }
}
