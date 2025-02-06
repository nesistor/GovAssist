import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:government_assistant/constants.dart';
import 'package:government_assistant/providers/chat_provider.dart';

class SideBar extends StatelessWidget {
  const SideBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ChatProvider>(
      builder: (context, apiProvider, child) {
        return Container(
          width: 250,
          color: kSideBarColor,
          child: Column(
            children: [
              // Nagłówek z logo
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
              // Sekcje z konwersacjami: Today, 7 Days, 30 Days
              Expanded(
                child: ListView(
                  children: [
                    _buildSection("Today", apiProvider, "today"),
                    _buildSection("Previous 7 Days", apiProvider, "7days"),
                    _buildSection("Previous 30 Days", apiProvider, "30days"),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  // Budowanie sekcji konwersacji
  Widget _buildSection(String title, ChatProvider apiProvider, String timeRange) {
    return Column(
      children: [
        // Tytuł sekcji
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(
            title,
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        // Lista konwersacji w tej sekcji
        _buildConversationList(apiProvider, timeRange),
      ],
    );
  }

  // Lista konwersacji w sekcji
  Widget _buildConversationList(ChatProvider apiProvider, String timeRange) {
    // Filtrujemy konwersacje dla danej sekcji
    var filteredTitles = apiProvider.conversationTitles; // W przyszłości można tu dodać logikę filtrowania
    return NotificationListener<ScrollNotification>(
      onNotification: (scrollInfo) {
        // Ładowanie starszych konwersacji, gdy użytkownik dotrze do końca listy
        if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent && !apiProvider.isLoading) {
          apiProvider.fetchConversationTitles(timeRange: timeRange, page: apiProvider.currentPage + 1);
        }
        return false;
      },
      child: ListView.builder(
        shrinkWrap: true,  // Umożliwia przewijanie tylko w obrębie dostępnej przestrzeni
        physics: NeverScrollableScrollPhysics(),  // Nie pozwala na przewijanie listy w środku
        itemCount: filteredTitles.length,
        itemBuilder: (context, index) {
          return ListTile(
            title: Text(
              filteredTitles[index],
              style: TextStyle(
                color: Colors.white,
                textBaseline: TextBaseline.alphabetic,  // Ensure the text is aligned correctly
              ),
              textAlign: TextAlign.left,  // Ensure the text is aligned to the left
            ),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${filteredTitles[index]} clicked')));
            },
          );
        },
      ),
    );
  }
}
