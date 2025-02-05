import 'package:flutter/material.dart';
import 'package:government_assistant/responsive.dart';
import 'package:government_assistant/components/background.dart';
import 'package:government_assistant/pages/login_page/widgets/login_form.dart';
import 'package:government_assistant/pages/login_page/widgets/login_page_top_image.dart';
import 'package:government_assistant/pages/login_page/widgets/social_login.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Background(
      child: SingleChildScrollView(
        child: Responsive(
          mobile: MobileLoginPage(),
          desktop: Row(
            children: [
              Expanded(
                child: LoginPageTopImage(),
              ),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 450,
                      child: LoginForm(),
                    ),
                    SizedBox(height: 16),
                    SocialLogin(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MobileLoginPage extends StatelessWidget {
  const MobileLoginPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        LoginPageTopImage(),
        Row(
          children: [
            Spacer(),
            Expanded(
              flex: 8,
              child: LoginForm(),
            ),
            Spacer(),
          ],
        ),
        SizedBox(height: 16),
        SocialLogin(),
      ],
    );
  }
}
