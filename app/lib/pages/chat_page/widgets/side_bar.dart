import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:government_assistant/constants.dart';
import 'package:government_assistant/providers/api_provider.dart';

class SideBar extends StatelessWidget {
  const SideBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiProvider>(
      builder: (context, apiProvider, child) {
        return Container(
          width: 200,
          color: kSideBarColor,
          child: Column(
            children: [
              Container(
                height: 100,
                alignment: Alignment.centerLeft,
                padding: const EdgeInsets.only(left: 10.0),
                child: Row(
                  children: [
                    Image.asset(
                      'assets/logo/GovAssist.png',
                      width: 40,
                      height: 40,
                    ),
                    const SizedBox(width: 10),
                    const Text(
                      'GovAssist',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: apiProvider.conversationTitles.length,
                  itemBuilder: (context, index) {
                    return _buildButton(
                        apiProvider.conversationTitles[index], context);
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildButton(String text, BuildContext context) {
    return ListTile(
      title: Text(
        text,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 14,
        ),
      ),
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$text clicked')),
        );
      },
    );
  }
}
